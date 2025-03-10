from django.db import models

# Create your models here.

# administration/models.py
class Admin(models.Model):
    username=models.CharField(max_length=30)
    password=models.CharField(max_length=30)
    
    def __str__(self):
        return self.username

class Announcement(models.Model):
    title = models.CharField(max_length=150)
    message = models.TextField()
    target_group = models.CharField(max_length=50, choices=[('students', 'Students'), ('lecturers', 'Lecturers'), ('both', 'Both')])
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.message[:50]
