from django import forms
from django.contrib.auth.models import User
from .models import Lecturer
from students.models import CourseMaterial

class RegisterLecturerForm(forms.ModelForm):
    programme = forms.CharField(max_length=100, required=True)
    contact = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = f"{self.cleaned_data['first_name']}_{self.cleaned_data['last_name']}".lower()
        user.set_password(self.cleaned_data.get('student_number', 'defaultpassword'))  # Replace 'defaultpassword' with a secure default or leave it as is
        if commit:
            user.save()
        return user

# lecturers/forms.py

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'file', 'course', 'programme', 'description']  # Form fields
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'programme': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial  # Assuming you have a model for course materials
        fields = ['title', 'course', 'programme', 'video_link', 'video_file']  # Include the relevant fields
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'programme': forms.Select(attrs={'class': 'form-control'}),
            'video_link': forms.TextInput(attrs={'class': 'form-control'}),
            'video_file': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
        }
    
    # Custom validation to restrict file types
    def clean_video(self):
        video = self.cleaned_data.get('video', False)
        if video:
            if not video.content_type.startswith('video'):
                raise forms.ValidationError('File type is not supported. Please upload a video.')
            if video.size > 500 * 1024 * 1024:  # 500 MB limit
                raise forms.ValidationError("Video file too large ( > 500 MB )")
        return video