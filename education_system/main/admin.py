
from django.contrib import admin
from .models import (
    User, Question, Option, Course, Lesson, Quiz, QuizAttempt, Badge, 
    Leaderboard, LeaderboardEntry, Quest, QuestCompletion, BadgeAcquisition
)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_staff', 'is_active')

admin.site.register(User, UserAdmin)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'time_limit')
    search_fields = ('text',)
    list_filter = ('question_type',)
    inlines = [OptionInline]

admin.site.register(Question, QuestionAdmin)


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    inlines = [LessonInline]

admin.site.register(Course, CourseAdmin)


class QuizAdmin(admin.ModelAdmin):
    list_display = ('lesson',)
    list_filter = ('lesson__course',)

admin.site.register(Quiz, QuizAdmin)


class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'attempted_at')
    search_fields = ('user__username', 'quiz__lesson__course__title')
    list_filter = ('quiz__lesson__course', 'user', 'score')

admin.site.register(QuizAttempt, QuizAttemptAdmin)


class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(Badge, BadgeAdmin)


class LeaderboardEntryInline(admin.TabularInline):
    model = LeaderboardEntry
    extra = 1

class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('course',)
    search_fields = ('course__title',)
    inlines = [LeaderboardEntryInline]

admin.site.register(Leaderboard, LeaderboardAdmin)


class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('leaderboard', 'student', 'score', 'rank')
    list_filter = ('leaderboard__course', 'rank')

admin.site.register(LeaderboardEntry, LeaderboardEntryAdmin)


class QuestAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'description')
    search_fields = ('title', 'course__title')

admin.site.register(Quest, QuestAdmin)


class QuestCompletionAdmin(admin.ModelAdmin):
    list_display = ('quest', 'student', 'completed_at')
    list_filter = ('quest__course', 'student')

admin.site.register(QuestCompletion, QuestCompletionAdmin)


class BadgeAcquisitionAdmin(admin.ModelAdmin):
    list_display = ('badge', 'student', 'acquired_at')
    list_filter = ('badge', 'student')

admin.site.register(BadgeAcquisition, BadgeAcquisitionAdmin)
