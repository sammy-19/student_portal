from django import forms
from .models import Submission, StudentProfile

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['student_number', 'name', 'program_of_study', 'duration_years', 'intake_date', 'gender']
        widgets = {
            'student_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'program_of_study': forms.Select(attrs={'class': 'form-control'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'intake_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']  # Assuming students are uploading files for their assignments
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
