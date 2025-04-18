from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from lecturers.models import Lecturer
from lecturers.forms import *
from students.forms import StudentRegistrationForm
from students.models import *  
from lecturers.models import Lecturer
from .models import Announcement, Admin


# Create your views here.

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            admin = Admin.objects.get(username=username, password=password) # Check against Admin model
            request.session['admin_id'] = admin.id
            messages.success(request, "Login successful. Welcome, Admin!")
            return redirect('administration:admin_dashboard')
        except Admin.DoesNotExist:
            messages.error(request, "Invalid admin credentials.")

        # Corrected part: Pass the messages from the request context
        return render(request, 'administration/login.html', {'messages': messages.get_messages(request)})

    return render(request, 'administration/login.html')

def admin_logout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
    messages.success(request, "Successfully logged out.")
    return redirect('administration:admin_login')

def admin_dashboard(request):
    if 'admin_id' not in request.session:
        messages.error(request, "You must be logged in as admin to view this page.")
        return redirect('administration:admin_login')
    
    students = Student.objects.all().order_by('-id')[:3]  # Get all students
    lecturers = Lecturer.objects.all().order_by('-id')[:3]  # Get all lecturers

    # Render the dashboard template and pass the students and lecturers
    return render(request, 'administration/dashboard.html', {
        'students': students,
        'lecturers': lecturers,
    })

def create_announcement(request):
    if request.method == 'POST':
        title = request.POST['title']
        message = request.POST['announcement']
        target_group = request.POST.get('target_group', 'both')  # Get the target group from form
        Announcement.objects.create(title=title, message=message, target_group=target_group)
        messages.success(request, "Announcement created successfully!")
        return redirect('administration:admin_dashboard')
    
    return render(request, 'administration/create_announcement.html')

def list_lecturers(request):
    lecturers = Lecturer.objects.all()
    return render(request, 'administration/list_lecturers.html', {'lecturers': lecturers})

def student_list(request):
    students = StudentProfile.objects.all()  # Get all student profiles
    return render(request, 'administration/student_list.html', {'students': students})

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student_profile = form.save()  # Save the StudentProfile data

            # Create a new User with the student's name as the username and student_number as password
            user = User.objects.create_user(username=student_profile.name, password=student_profile.student_number)

            # Automatically assign the student to the first course (you can adjust this logic)
            course = Course.objects.first()

            # Create the Student object
            student = Student.objects.create(user=user, student_number=student_profile.student_number, course=course, program_of_study=student_profile.program_of_study)

            messages.success(request, f'Student {student_profile.name} has been successfully registered.')
             
            return redirect('administration:student_list')  # Redirect to student list or dashboard
    else:
        form = StudentRegistrationForm()

    return render(request, 'administration/register_student.html', {'form': form})

def register_lecturers(request):
    if request.method == 'POST':
        form = RegisterLecturerForm(request.POST)
        if form.is_valid():
            # Create the new user (lecturer)
            user = form.save(commit=False)
            user.set_password('password1234')  # You should set a secure password or generate one
            user.save()
            
            # Create the lecturer profile
            contact = form.cleaned_data['contact']
            lecturer_profile = Lecturer.objects.create(
                user=user,
                contact=contact
            )
            selected_programmes = form.cleaned_data['programme'] 
            lecturer_profile.programme.set(selected_programmes)
            messages.success(request, f"Lecturer '{user.username}' registered successfully.")
            
            return redirect('administration:list_lecturers')
    else:
        form = RegisterLecturerForm()
    
    return render(request, 'administration/register_lecturers.html', {'form': form})