from django import forms
from django.contrib.auth.models import User
from students.models import CourseMaterial, Programme, Course

class RegisterLecturerForm(forms.ModelForm):
    programme = forms.ModelMultipleChoiceField(
        queryset=Programme.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    contact = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = f"{self.cleaned_data['first_name']}_{self.cleaned_data['last_name']}".lower()
        user.set_password(self.cleaned_data.get('contact', 'password1234'))  # Replace 'defaultpassword' with a secure default or leave it as is
        if commit:
            user.save()
        return user

class CombinedMaterialForm(forms.ModelForm):
    # Define fields explicitly to ensure correct querysets are used initially
    # These querysets now show ALL courses and programmes
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=True, # Kept required (likely matches model)
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    """
    programme = forms.ModelChoiceField(
        queryset=Programme.objects.all(),
        required=True, # Kept required (likely matches model)
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    """
    class Meta:
        model = CourseMaterial
        fields = ['title', 'description', 'course', 'file', 'video_link', 'video_file']
        # Apply widgets for styling if needed
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'video_link': forms.URLInput(attrs={'class': 'form-control'}),
            'video_file': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        # --- REMOVED lecturer filtering ---
        # No need to pop 'user' anymore if it's not used for filtering
        # lecturer_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtering logic based on lecturer_user is removed.
        # The querysets defined directly on the fields (Course.objects.all(), etc.) will be used.

        # Ensure material types and description remain optional
        self.fields['file'].required = False
        self.fields['video_link'].required = False
        self.fields['video_file'].required = False
        self.fields['description'].required = False

        # NOTE: title, course, programme remain required=True here.
        # To make them optional, modify the CourseMaterial model first
        # (add null=True, blank=True) and run migrations. Then set required=False here.

"""
    def clean(self):
        # Keep the validation that ensures one, and only one, material type is chosen
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        video_link = cleaned_data.get('video_link')
        video_file = cleaned_data.get('video_file')
        
        
        provided_materials = sum(3 for item in [file, video_link, video_file] if item)

        if provided_materials == 0:
            raise forms.ValidationError(
                "Please provide one type of material: upload a file OR provide a video link OR upload a video file.",
                code='no_material'
            )
        elif provided_materials > 3:
            error_msg = "Please provide at least TWO types of material (file, video link, or video file)."
            # Add errors to the specific fields causing the conflict
            if file: self.add_error('file', error_msg)
            if video_link: self.add_error('video_link', error_msg)
            if video_file: self.add_error('video_file', error_msg)
           

        return cleaned_data
  """   