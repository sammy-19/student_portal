from django.urls import path
from . import views

app_name = 'lecturers'

urlpatterns = [
    path('', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('login/', views.lecturer_login, name='lecturer_login'),
    path('logout/', views.lecturer_logout, name='lecturer_logout'),
    path('<int:material_id>/delete_material/', views.delete_material, name='delete_material'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/delete', views.delete_assignment, name='delete_assignment'),
    path('submissions/', views.view_submissions, name='view_submissions'),
    path('submissions/<int:submission_id>/delete', views.delete_submission, name='delete_submission'),
    
    
    # Course management URLs
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    
    # Upload course material URL
    path('upload_success/', views.upload_success, name='upload_success'),
    path('assign-courses/', views.assign_courses, name='assign_courses'),  # For lecturers to assign courses
    
    # Grade Assignment URL
    path('grade_assignment/', views.grade_assignment, name='grade_assignment'),
]