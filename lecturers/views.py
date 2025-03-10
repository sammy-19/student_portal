from students.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CourseMaterialForm, VideoUploadForm
from .models import Lecturer
from django.http import HttpResponse


# Lecturer login view
def lecturer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                lecturer = Lecturer.objects.get(user=user)
                login(request, user)
                messages.success(request, "Login successful. Welcome, Lecturer!")
                return redirect('lecturers:lecturer_dashboard')
            except Lecturer.DoesNotExist:
                messages.error(request, "You are not authorized as a lecturer.")
                return render(request, 'lecturers/login.html', {'messages.error': messages.error})
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return render(request, 'lecturers/login.html', {'messages.error': messages.error})
    
    return render(request, 'lecturers/login.html')

def lecturer_logout(request):
    logout(request)  # This will remove the user session and log them out
    messages.success(request, "Successfully logged out.")
    return redirect('lecturers:lecturer_login')  # Redirect to lecturer login page


@login_required
def upload_material(request):
    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lecturers:upload_success')  # Redirect after successful upload
    else:
        form = CourseMaterialForm()

    return render(request, 'lecturers/dashboard.html', {'form': form})

@login_required
def upload_success(request):
    return render(request, 'lecturers/upload_success.html')

@login_required (login_url='/lecturers/login/?next=/lecturers/')
def lecturer_dashboard(request):
    try:
        lecturer = Lecturer.objects.get(user=request.user)  # Check if the user is a lecturer
    except Lecturer.DoesNotExist:
        return HttpResponse("Access denied. Only lecturers are allowed.")
    lecturer = get_object_or_404(Lecturer, user=request.user)
    courses = lecturer.assigned_courses.all()
    course_materials = CourseMaterial.objects.filter(course__in=courses)
    assignments = Assignment.objects.filter(course__in=lecturer.assigned_courses.all())
    
    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        video_form = VideoUploadForm(request.POST, request.FILES)
        if video_form.is_valid():
            video_form.save()
            return redirect('lecturers:upload_success')
        
        if form.is_valid():
            form.save()
            return redirect('lecturers:upload_success')  # Redirect after successful upload
                
    else:
        form = CourseMaterialForm()
        video_form = VideoUploadForm()
        
    return render(request, 'lecturers/dashboard.html', {
        'lecturer': lecturer,
        'courses': courses,
        'course_materials': course_materials,
        'assignments': assignments,
        'form': form,
        "video_form": video_form,
        })
    
# Create a new assignment
@login_required
def create_assignment(request):
    lecturer = get_object_or_404(Lecturer, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        course_id = request.POST.get('course')
        course = Course.objects.get(id=course_id)
        programme = request.POST.get('programme')
        
        # Include the lecturer's programme when creating an assignment
        Assignment.objects.create(
            title=title,
            description=description,
            due_date=due_date,
            course=course,
            lecturer=request.user,
            programme=programme  # Save the programme
        )
        return redirect('lecturers:lecturer_dashboard')
    
    courses = lecturer.assigned_courses.all()  # Only show courses assigned to this lecturer
    return render(request, 'lecturers/create_assignment.html', {'courses': courses})

# View submissions for a specific assignment
@login_required
def view_submissions(request):
    assignments = Assignment.objects.filter(lecturer=request.user)
    if not assignments.exists():
        return render(request, 'lecturers/view_submissions.html')
    submissions = Submission.objects.filter(assignment__in=assignments)
    return render(request, 'lecturers/view_submissions.html', {'submissions': submissions, 'assignment': assignments})

@login_required
def create_course(request):
    lecturer = get_object_or_404(Lecturer, user=request.user)  # Get the current logged-in lecturer
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Create the new course
        course = Course.objects.create(name=name, description=description)
        
        # Assign the course to the lecturer
        lecturer.assigned_courses.add(course)
        lecturer.save()  # Save the lecturer instance to persist the changes
        
        return redirect('lecturers:lecturer_dashboard')
    
    return render(request, 'lecturers/create_course.html')


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.description = request.POST.get('description')
        course.save()
        return redirect('lecturers:lecturer_dashboard')
    return render(request, 'lecturers/edit_course.html', {'course': course})

@login_required
def assign_courses(request):
    programmes = Programme.objects.all()
    courses = Course.objects.all()

    if request.method == 'POST':
        programme_id = request.POST.get('programme')
        course_ids = request.POST.getlist('courses')

        programme = get_object_or_404(Programme, id=programme_id)
        selected_courses = Course.objects.filter(id__in=course_ids)

        # Assign selected courses to the programme
        for course in selected_courses:
            course.programme = programme
            course.save()

        # Automatically assign these courses to all students in the programme
        students_in_programme = Student.objects.filter(program_of_study=programme)
        for student in students_in_programme:
            student.assigned_courses.set(selected_courses)
        
        return redirect('lecturers:assign_courses')

    context = {
        'programmes': programmes,
        'courses': courses,
    }
    return render(request, 'lecturers/assign_courses.html', context)

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('lecturers:lecturer_dashboard')

def delete_material(request, material_id):
    course_material = get_object_or_404(CourseMaterial, id=material_id)
    course_material.delete()
    return redirect('lecturers:lecturer_dashboard')
    
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.delete()
    return redirect('lecturers:lecturer_dashboard')

def delete_submission(request, submission_id):
    submissions = get_object_or_404(Submission, id=submission_id)
    submissions.delete()
    return redirect('lecturers:lecturer_dashboard')

@login_required
def grade_assignment(request):
    if request.method == 'POST':
        student_number = request.POST.get('student_number')
        assignment_id = request.POST.get('assignment_id')
        score = request.POST.get('score')

        # Validate the score
        if not score:
            return HttpResponse("Score is required.", status=400)
        
        try:
            score = int(score)
        except ValueError:
            return HttpResponse("Invalid score format. Must be an integer.", status=400)

        if score < 0 or score > 100:
            return HttpResponse("Score must be between 0 and 100.", status=400)

        # Fetch the student and assignment
        student = get_object_or_404(Student, student_number=student_number)
        assignment = get_object_or_404(Assignment, id=assignment_id)

        # Create or update the result, ensuring assignment is included
        result, created = Result.objects.get_or_create(
            student=student, 
            course=assignment.course, 
            assignment=assignment,
            defaults={'grade': score}  # Set the grade when creating the result
        )

        # If the result already exists, update the grade
        if not created:
            result.grade = score
            result.save()

        return redirect('lecturers:grade_assignment')  # Redirect back to the grading page

    # Fetch all submissions for grading
    submissions = Submission.objects.all()

    # Fetch existing results and map them to their corresponding submissions
    submission_results = []
    for submission in submissions:
        try:
            result = Result.objects.get(student=submission.student, assignment=submission.assignment)
        except Result.DoesNotExist:
            result = None
        submission_results.append((submission, result))

    context = {
        'submission_results': submission_results,  # Pass tuple of (submission, result)
    }
    return render(request, 'lecturers/grade_assignment.html', context)
