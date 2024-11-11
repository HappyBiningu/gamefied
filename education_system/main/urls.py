
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/edit/<int:pk>/', views.edit_course, name='edit_course'),  
    path('courses/delete/<int:pk>/', views.delete_course, name='delete_course'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('quiz/<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:pk>/attempt/', views.attempt_quiz, name='attempt_quiz'),
    path('quiz/result/<int:pk>/', views.quiz_result, name='quiz_result'),
    path('dashboard/leaderboard/<int:pk>/', views.leaderboard, name='leaderboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('user_management/', views.user_management, name='user_management'),
    path('course-management/', views.course_management, name='course_management'),
    path('reports/', views.reports, name='reports'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/user_activity/', views.user_activity, name='user_activity'),
    path('student/<int:student_id>/quiz-history/', views.student_quiz_history, name='student_quiz_history'),
    # Authentication paths
    path('accounts/', include('django.contrib.auth.urls')),  
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]


