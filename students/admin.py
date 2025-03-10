from django.contrib import admin
from .models import Student, Assignment, Result, Submission, Course, CourseMaterial, StudentProfile, Programme

# Register your models here.

admin.site.register(CourseMaterial)
admin.site.register(Programme)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Result)
admin.site.register(Student)
admin.site.register(StudentProfile)