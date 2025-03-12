from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Programme(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    student_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=30)
    program_of_study = models.ForeignKey(Programme, on_delete=models.CASCADE)
    duration_years = models.IntegerField()
    intake_date = models.DateField()
    gender = models.CharField(max_length=30, choices=(('Male', 'Male'), ('Female', 'Female')))
    profile_picture = models.ImageField(upload_to='images/profiles/', default='images/profiles/profile.jpg', blank=True, null=True) # Added profile_picture

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='images/course_images/', blank=True, null=True) # Added image field for Course

    def __str__(self):
        return self.name

class CourseMaterial(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/', null=True, blank=True)
    video_link = models.URLField(max_length=500, null=True, blank=True)
    video_file = models.FileField(upload_to='video_lectures/', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, default=1)
    description = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_number = models.CharField(max_length=30, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)
    intake_date = models.DateField(default=date(2024, 9, 2))   # Intake date for the course
    duration_years = models.IntegerField(default="2")   # Duration of the course
    assigned_courses = models.ManyToManyField(Course, related_name='students', blank=True)   # Many-to-Many relationship
    program_of_study = models.ForeignKey(Programme, on_delete=models.CASCADE, default=1)
    profile_picture = models.ImageField(upload_to='images/student_profiles/', default='images/profiles/profile.jpg', blank=True, null=True) # Added profile_picture for Student

    def __str__(self):
        return self.user.username

    def current_year_and_semester(self):
        #Calculate the current year and semester based on the intake date.
        today = date.today()
        start_month = self.intake_date.month
        course_start_year = self.intake_date.year

        # Calculate the total number of months the student has been studying
        total_months = (today.year - course_start_year) * 12 + (today.month - start_month)

        # Calculate the current year
        current_year = total_months // 12 + 1

        # Calculate the current semester
        if (total_months % 12) < 6:
            current_semester = 1
        else:
            current_semester = 2

        # Ensure the current year doesn't exceed the course duration
        if current_year > self.duration_years:
            current_year = self.duration_years

        return current_year, current_semester

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_lecturer')
    programme = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.username} - {self.assignment.title}'

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING)  # Ensure this field is present
    grade = models.IntegerField()