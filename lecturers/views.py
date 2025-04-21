from students.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import CombinedMaterialForm
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

# --- Upload Success View (Optional) ---
@login_required
def upload_success(request):
    # You might not need this view if you show messages directly on the dashboard
    return render(request, 'lecturers/upload_success.html')


# --- CLEANED UP Dashboard View (Handles GET only) ---
@login_required(login_url='/lecturers/login/') # Set login URL correctly
def lecturer_dashboard(request):
    try:
        lecturer = Lecturer.objects.get(user=request.user)
    except Lecturer.DoesNotExist:
        messages.error(request, "Access denied. Only lecturers are allowed.")
        return redirect('lecturers:lecturer_login')

    material_form = CombinedMaterialForm() # For GET request

    if request.method == 'POST':
        material_form = CombinedMaterialForm(request.POST, request.FILES)
        if material_form.is_valid():
            material_form.save()
            messages.success(request, "Course material added successfully!")
            return redirect('lecturers:lecturer_dashboard')
        else:
            messages.error(request, "Failed to add material. Please check the form errors below.")
            # Fall through to render with the invalid form

    # Fetch other context data
    courses = lecturer.assigned_courses.all()
    course_materials = CourseMaterial.objects.filter(course__in=courses).order_by('-uploaded_at')
    assignments = Assignment.objects.filter(lecturer=request.user).order_by('-due_date')

    context = {
        'lecturer': lecturer,
        'courses': courses,
        'course_materials': course_materials,
        'assignments': assignments,
        'material_form': material_form, # Pass the single form
    }
    return render(request, 'lecturers/dashboard.html', context)
    
# Create a new assignment
@login_required
def create_assignment(request):
    lecturer = get_object_or_404(Lecturer, user=request.user)

    if request.method == 'POST':
        # Get data from POST
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        course_id = request.POST.get('course')
        course = Course.objects.get(id=course_id)

        # --- Correctly get the uploaded file from request.FILES ---
        assignment_file = request.FILES.get('file') # Use request.FILES.get()

        # Create the Assignment object, passing the file object
        try:
             Assignment.objects.create(
                 title=title,
                 description=description,
                 due_date=due_date,
                 course=course,
                 file=assignment_file, # Assign the actual file object here
                 lecturer=request.user,
                 # programme=programme logic removed based on previous interactions
             )
             messages.success(request, f"Assignment '{title}' created successfully.")
             return redirect('lecturers:lecturer_dashboard') # Redirect back to dashboard
        except Exception as e:
             # Catch potential errors during creation
             messages.error(request, f"An error occurred while creating the assignment: {e}")
             courses = lecturer.assigned_courses.all()
             form_data = request.POST
             return render(request, 'lecturers/create_assignment.html', {'courses': courses, 'form_data': form_data})

    # GET request
    # Show only courses assigned to this lecturer in the dropdown
    course = Course.objects.all()
    return render(request, 'lecturers/create_assignment.html', {'courses': course})
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
    # Use request.user directly if your Lecturer model has a OneToOneField to User named 'user'
    # Or adjust based on how you link Django User to Lecturer
    lecturer = get_object_or_404(Lecturer, user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        # MODIFICATION: Get the image file from request.FILES
        image_file = request.FILES.get('image') # Use .get() to handle missing file gracefully

        # Basic validation check (consider using Django Forms for robust validation)
        if name and description:
            # Create the new course, passing the image file
            course = Course.objects.create(
                name=name,
                description=description,
                image=image_file # Assign the uploaded file object here
                                 # Django handles saving it via the configured storage (e.g., Cloudinary)
            )

            lecturer.assigned_courses.add(course)
            # lecturer.save() # Not typically needed just for adding to M2M

            return redirect('lecturers:lecturer_dashboard')
        else:
            pass # Or add context={'error': 'Name and description required.'}

    # Render the form for GET request or if POST failed validation (in a more robust setup)
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
    courses = Course.objects.all() # You might want to filter this list

    if request.method == 'POST':
        programme_id = request.POST.get('programme')
        course_ids = request.POST.getlist('courses') # List of course IDs to assign TO the programme

        # Basic validation
        if not programme_id or not course_ids:
            messages.error(request, "Please select a programme and at least one course.")
            # It's better to re-render the form with an error than just redirecting immediately
            context = {'programmes': programmes, 'courses': courses, 'error': 'Selection missing.'}
            return render(request, 'lecturers/assign_courses.html', context)

        programme = get_object_or_404(Programme, id=programme_id)
        selected_courses = Course.objects.filter(id__in=course_ids)

        # --- CORRECT LOGIC for ManyToManyField ---
        # For each course selected, add the chosen programme to its 'programmes' list.
        courses_updated_count = 0
        for course in selected_courses:
            # .add() handles duplicates; it won't add if the relationship already exists.
            course.programmes.add(programme)
            courses_updated_count += 1
            # No need to call course.save() when using .add()/.remove()/.set() for ManyToMany

        if courses_updated_count > 0:
            messages.success(request, f"{courses_updated_count} course(s) successfully assigned to programme '{programme.name}'.")
        else:
             messages.warning(request, "No courses were assigned (check selection).")


        # --- Student Assignment Logic (Review Carefully) ---
        # This part assigns the selected courses to *all* students currently in the programme.
        # Decide if you want to REPLACE (.set()) or ADD TO (.add()) the students' course lists.
        # Using .add() is generally safer if students might have other courses.
        students_in_programme = Student.objects.filter(program_of_study=programme)
        if students_in_programme.exists():
             for student in students_in_programme:
                 # Option: Add these courses without removing others
                 student.assigned_courses.add(*selected_courses)

                 # Option: Replace student's courses entirely (original logic was like this)
                 # student.assigned_courses.set(selected_courses)

             messages.info(request, f"Selected courses also added to {students_in_programme.count()} student(s) in the programme.")
        # --- End Student Assignment Logic ---

        return redirect('lecturers:assign_courses') # Redirect back to the assignment page

    # GET request
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
