from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('',views.admin_dashboard, name='admin_dashboard'),
    path('login/',views.admin_login, name='admin_login'),
    path('logout',views.admin_logout, name='admin_logout'),
    path('create_announcement/', views.create_announcement, name='create_announcement'),
        
    # Register and list lecturers URL
    path('register_lecturers/', views.register_lecturers, name='register_lecturers'),
    path('list_lecturers/', views.list_lecturers, name='list_lecturers'),
    
    # Register and list students URL
    path('register/', views.register_student, name='register_student'),
    path('students/', views.student_list, name='student_list'),
]
