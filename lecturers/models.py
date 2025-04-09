from django.db import models
from students.models import Course, Programme
from django.contrib.auth.models import User

class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    assigned_courses = models.ManyToManyField(Course)
    programme = models.ManyToManyField(Programme)
    contact = models.CharField(max_length=20)
    

    def __str__(self):
        return self.user.username
