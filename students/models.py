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
    programmes = models.ManyToManyField(Programme, related_name='courses', blank=True)
    image = models.ImageField(upload_to='images/course_images/', blank=True, null=True, default='images/course_images/default.jpg') # Added image field for Course

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
    intake_date = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True)
    duration_years = models.IntegerField(default="2")   # Duration of the course
    assigned_courses = models.ManyToManyField(Course, related_name='students', blank=True)   # Many-to-Many relationship
    program_of_study = models.ForeignKey(Programme, on_delete=models.CASCADE, default=1)
    profile_picture = models.ImageField(upload_to='images/student_profiles/', default='images/profiles/profile.jpg', blank=True, null=True) # Added profile_picture for Student

    def __str__(self):
         return self.user.username

    def current_year_and_semester(self):
    
        # 1. Check if the link to the profile exists AND if that profile has an intake_date set
        if not self.intake_date or not self.intake_date.intake_date:
            # Return a default or indicator that the date is missing
            return None, None

        # 2. Access the actual date field *within* the linked StudentProfile object
        actual_intake_date = self.intake_date.intake_date # <-- The crucial change

        today = date.today()
        # 3. Use the actual_intake_date for calculations
        start_month = actual_intake_date.month
        course_start_year = actual_intake_date.year

        # --- Rest of your calculation logic ---
        # Ensure robust calculation
        if today < actual_intake_date: # Handle cases where intake date is in the future
             return 1, 1 # Or None, None or 0, 0 depending on requirements

        total_months = (today.year - course_start_year) * 12 + (today.month - start_month)

        current_year = (total_months // 12) + 1

        months_into_current_academic_year = total_months % 12
        if months_into_current_academic_year < 6: # Assuming semesters split at 6 months
            current_semester = 1
        else:
            current_semester = 2

        # Ensure duration_years is treated as an int for comparison
        try:
            duration = int(self.duration_years)
            if current_year > duration:
                current_year = duration
                # Optional: Cap semester at 2 if year is capped? Depends on logic.
                # current_semester = 2
        except (ValueError, TypeError):
            # Handle cases where duration_years might not be a valid number
            # Maybe log a warning or set a default behavior
            print(f"Warning: Invalid duration_years '{self.duration_years}' for student {self.user.username}")
            # Decide how to proceed if duration is invalid. Maybe return None, None?
            return None, None # Example: return None if duration is invalid

        return current_year, current_semester

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', default='course_materials/finacial_statements.pdf')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_lecturer')
    programme = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True)
    assignment_title_at_submission = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         # Use the stored title if assignment is gone
         title = self.assignment.title if self.assignment else self.assignment_title_at_submission
         return f'{self.student.user.username} - {title}'

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.SET_NULL, null=True)
    assignment_title_at_grading = models.CharField(max_length=255, blank=True)
    grade = models.IntegerField()
    
    def __str__(self):
        title = self.assignment.title if self.assignment else self.assignment_title_at_grading
        return f"Result for {self.student.user.username} on {title}"