
from django import forms
from .models import QuizAttempt, Question, Course, Quiz, Option
from django.forms import modelformset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'teacher']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'time_limit']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct', 'ordering']
        widgets = {
            'is_correct': forms.RadioSelect 
        }


OptionFormSet = modelformset_factory(Option, form=OptionForm, extra=4, can_delete=True)

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'lesson', 'questions']
        widgets = {
            'questions': forms.CheckboxSelectMultiple()
        }

class QuizAttemptForm(forms.ModelForm):
    class Meta:
        model = QuizAttempt
        fields = []

    def __init__(self, *args, **kwargs):
        self.quiz = kwargs.pop('quiz', None)
        super().__init__(*args, **kwargs)
        for question in self.quiz.questions.all():
            if question.question_type == 'OE':  # Open-ended
                self.fields[f'question_{question.pk}'] = forms.CharField(
                    label=question.text,
                    widget=forms.TextInput(attrs={'placeholder': 'Your answer'}),
                    required=True
                )
            elif question.question_type in ['MCQ', 'TF']:  # MCQ or True/False
                self.fields[f'question_{question.pk}'] = forms.ChoiceField(
                    label=question.text,
                    choices=[(opt.pk, opt.text) for opt in question.options.all()],
                    widget=forms.RadioSelect,
                    required=True
                )

    def save(self, commit=True):
        instance = super().save(commit=False)
        score = 0
        for question in self.quiz.questions.all():
            answer = self.cleaned_data.get(f'question_{question.pk}')
            if question.question_type in ['MCQ', 'TF']:
                correct_option = question.options.filter(is_correct=True).first()
                if correct_option and str(correct_option.pk) == answer:
                    score += 1
            elif question.question_type == 'OE':
                
                pass
        instance.score = score
        if commit:
            instance.save()
        return instance

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'role')

from django.contrib.auth.models import User
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']