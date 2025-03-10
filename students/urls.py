from django.urls import path
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views


#Custom Logout View
class CustomLogoutView(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, "Successfully logged out")
        return super().dispatch(request, *args, **kwargs)

app_name = 'students'

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='students/login.html'), name='login'),
    path('announcements/', views.announcement_view, name='announcement_view'),
    path('logout/', views.std_logout, name='std_logout'),
    path('view-courses/', views.view_courses, name='view_courses'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('course/<int:course_id>/videos/', views.course_videos, name='course_videos'),
    path('download/<int:material_id>/', views.download_course_material, name='download_course_material'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)