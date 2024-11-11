
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import (
    Course, Lesson, Quiz, QuizAttempt, Leaderboard, Badge, Quest, 
    QuestCompletion, BadgeAcquisition, LeaderboardEntry
)
from .forms import QuizAttemptForm, CustomUserCreationForm

User = get_user_model()  


@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.role == 'student':
       
        recent_attempts = QuizAttempt.objects.filter(user=user).order_by('-attempted_at')[:5]
        earned_badges = BadgeAcquisition.objects.filter(student=user)
        completed_quests = QuestCompletion.objects.filter(student=user)
        enrolled_courses = Course.objects.filter(lessons__quizzes__attempts__user=user).distinct()

        context.update({
            'recent_attempts': recent_attempts,
            'earned_badges': earned_badges,
            'completed_quests': completed_quests,
            'enrolled_courses': enrolled_courses,
        })

    elif user.role == 'teacher':
        
        courses_taught = Course.objects.filter(teacher=user)

        
        recent_attempts = QuizAttempt.objects.filter(
            quiz__lesson__course__in=courses_taught
        ).order_by('-attempted_at')[:5]

        context.update({
            'courses_taught': courses_taught,
            'recent_attempts': recent_attempts,
        })

    elif user.role == 'admin':
      
        total_users = User.objects.count()
        total_courses = Course.objects.count()
        total_quiz_attempts = QuizAttempt.objects.count()

        context.update({
            'total_users': total_users,
            'total_courses': total_courses,
            'total_quiz_attempts': total_quiz_attempts,
        })

   
    if 'recent_attempts' not in context:
        context['no_recent_attempts'] = "No recent attempts to display."
    
    if 'courses_taught' not in context:
        context['no_courses_message'] = "You haven't been assigned any courses yet."

    print(context) 

    return render(request, 'main/dashboard.html', context)





def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def course_list(request):
    if request.user.role == 'teacher':
        
        courses_taught = Course.objects.filter(teacher=request.user)
        return render(request, 'main/course_list.html', {'courses_taught': courses_taught})

    elif request.user.role == 'student':
      
        enrolled_courses = request.user.enrolled_courses.all()  
        return render(request, 'main/course_list.html', {'enrolled_courses': enrolled_courses})
    
    else:
    
        courses = Course.objects.all()
        return render(request, 'main/course_list.html', {'courses': courses})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'main/course_detail.html', {'course': course})

@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'main/quiz_detail.html', {'quiz': quiz})



@login_required 
def attempt_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.all()

    if request.method == 'POST':
        form = QuizAttemptForm(request.POST, quiz=quiz)
        if form.is_valid():
            quiz_attempt = form.save(commit=False)
            quiz_attempt.user = request.user
            quiz_attempt.quiz = quiz
            quiz_attempt.attempted_at = timezone.now()
            quiz_attempt.save()
            
          
            score = 0
            for question in questions:
                user_answer = form.cleaned_data.get(f'question_{question.pk}')
                correct_answer = question.get_correct_answer()  

                if user_answer == str(correct_answer.pk):  
                    score += question.points if hasattr(question, 'points') else 1  
            
            quiz_attempt.score = score  
            quiz_attempt.save()
            
            return redirect('quiz_result', pk=quiz_attempt.pk)

    else:
        form = QuizAttemptForm(quiz=quiz)

    return render(request, 'main/attempt_quiz.html', {
        'form': form,
        'quiz': quiz,
        'questions': questions,
    })





@login_required
def quiz_result(request, pk):
    quiz_attempt = get_object_or_404(QuizAttempt, pk=pk)
    return render(request, 'main/quiz_result.html', {'quiz_attempt': quiz_attempt})

@login_required
def leaderboard(request, pk):
    leaderboard = get_object_or_404(Leaderboard, pk=pk)
    entries = LeaderboardEntry.objects.filter(leaderboard=leaderboard).order_by('-score')
    return render(request, 'main/leaderboard.html', {'leaderboard': leaderboard, 'entries': entries})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Lesson
from .forms import CourseForm

@login_required
def create_course(request):
    
    if request.user.role not in ['teacher', 'admin']:
        messages.error(request, "You don't have permission to create a course.")
        return redirect('course_list')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'main/course_form.html', {'form': form, 'action': 'Create'})

@login_required
def update_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
  
    if request.user.role not in ['teacher', 'admin']:
        messages.error(request, "You don't have permission to update this course.")
        return redirect('course_list')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'main/course_form.html', {'form': form, 'action': 'Update'})

@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to delete this course.")
        return redirect('course_list')

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('course_list')
    
    return render(request, 'main/confirm_delete.html', {'object': course})




@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            
            course.teacher = request.user
            course.save()  
            return redirect('course_list')  
    else:
        form = CourseForm()
    
    return render(request, 'main/create_course.html', {'form': form})



#analy

from django.db.models import Avg
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import QuizAttempt, Course, User

from django.db.models import Avg

@login_required
def teacher_dashboard(request):
    user = request.user
    if user.role != 'teacher':
        return redirect('some_other_view')

    courses_taught = Course.objects.filter(teacher=user)
    student_scores = []

    for course in courses_taught:
        students = course.students.all()  
        for student in students:
            avg_score = QuizAttempt.objects.filter(
                quiz__lesson__course=course, user=student
            ).aggregate(Avg('score'))['score__avg']
            
            student_scores.append({
                'student': student,
                'course': course,
                'avg_score': avg_score if avg_score else 0
            })

    context = {
        'student_scores': student_scores
    }

    return render(request, 'main/teacher_dashboard.html', context)





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

@login_required
def admin_dashboard(request):
    user = request.user

    
    if user.role != 'admin':
        return redirect('dashboard')  

  
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_admins = User.objects.filter(role='admin').count()

  
    user_data = {
        'labels': ['Students', 'Teachers', 'Admins'],
        'data': [total_students, total_teachers, total_admins]
    }

    context = {
        'user_data': user_data
    }

    return render(request, 'main/admin_dashboard.html', context)



from django.db.models import Count
from django.shortcuts import render
from .models import QuizAttempt, BadgeAcquisition, Course

@login_required
def user_activity(request):
    
    quiz_attempts = QuizAttempt.objects.values('user').annotate(attempt_count=Count('id')).order_by('-attempt_count')[:5]

  
    course_enrollments = Course.objects.values('teacher').annotate(enrollment_count=Count('lessons__quizzes__attempts')).order_by('-enrollment_count')[:5]

    
    badge_acquisitions = BadgeAcquisition.objects.values('student').annotate(badge_count=Count('id')).order_by('-badge_count')[:5]

    context = {
        'quiz_attempts': quiz_attempts,
        'course_enrollments': course_enrollments,
        'badge_acquisitions': badge_acquisitions,
    }
    
    return render(request, 'main/user_activity.html', context)



from django.shortcuts import render
from .models import QuizAttempt

@login_required
def student_quiz_history(request, student_id):
    attempts = QuizAttempt.objects.filter(user__id=student_id).order_by('attempted_at')
    labels = [attempt.attempted_at.strftime('%Y-%m-%d') for attempt in attempts]
    scores = [attempt.score for attempt in attempts]

    context = {
        'labels': labels,
        'scores': scores
    }
    
    return render(request, 'main/student_quiz_history.html', context)

from django.contrib.auth import logout

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  
    else:
        return redirect('dashboard') 
    
    

@login_required
def edit_course(request, pk):
    course = Course.objects.get(pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')  
    else:
        form = CourseForm(instance=course)

    return render(request, 'main/edit_course.html', {'form': form})




from django.shortcuts import get_object_or_404

@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return redirect('course_list')  







from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import UserForm


User = get_user_model()

def user_management(request):
    users = User.objects.all()  

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            user_id = request.POST.get('user_id')
            user_to_delete = get_object_or_404(User, pk=user_id)
            user_to_delete.delete()
            messages.success(request, 'User deleted successfully.')
            return redirect('user_management')

        elif action == 'create':
            form = UserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'User created successfully.')
                return redirect('user_management')
            else:
                messages.error(request, 'There was an error creating the user.')

    else:
        form = UserForm()

    return render(request, 'main/user_management.html', {
        'users': users,
        'form': form,
    })



def course_management(request):
    return render(request, 'main/course_management.html')

def reports(request):
    return render(request, 'main/reports.html')