
from django.db import models
from django.conf import settings  
from django.contrib.auth.models import AbstractUser

# User model to include roles (Student, Teacher, Administrator)
class User(AbstractUser):
    ROLES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=10, choices=ROLES)
    enrolled_courses = models.ManyToManyField('Course', related_name='students', blank=True)

    def __str__(self):
        return self.username


class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('OE', 'Open Ended'),
    )
    text = models.TextField()  
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ') 
    time_limit = models.IntegerField(default=10)  

    def __str__(self):
        return self.text

    def get_correct_answer(self):
        
        if self.question_type in ['MCQ', 'TF']:
            return self.options.filter(is_correct=True).first()  
        return None  


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')  
    text = models.CharField(max_length=255) 
    is_correct = models.BooleanField(default=False) 
    ordering = models.IntegerField()  

    class Meta:
        ordering = ['ordering'] 

    def __str__(self):
        return self.text


class Course(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title



class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    questions = models.ManyToManyField(Question, related_name='quizzes')
    title = models.CharField(max_length=255, default="Untitled Quiz")  

    def __str__(self):
        return self.title


class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt by {self.user} on {self.quiz.lesson.title} - Score: {self.score}"


class Badge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')

    def __str__(self):
        return self.name


class Leaderboard(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='leaderboard')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, through='LeaderboardEntry', related_name='leaderboards')

    def __str__(self):
        return f"Leaderboard for {self.course.title}"


class LeaderboardEntry(models.Model):
    leaderboard = models.ForeignKey(Leaderboard, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    rank = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('leaderboard', 'student')

    def __str__(self):
        return f"{self.student} in {self.leaderboard} - Score: {self.score}"


class Quest(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    rewards = models.ManyToManyField(Badge, related_name='quests')

    def __str__(self):
        return self.title


class QuestCompletion(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='completions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='completed_quests')
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} completed {self.quest.title}"


class BadgeAcquisition(models.Model):
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='acquisitions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges_acquired')
    acquired_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} earned {self.badge.name}"
