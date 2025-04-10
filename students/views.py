from .models import Assignment, Submission, Student, Result, StudentProfile, Course, CourseMaterial, Programme # Added Programme
from administration.models import Announcement
from django.shortcuts import render, get_object_or_404, redirect
from .forms import AssignmentSubmissionForm
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone # For current time and date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
import os
import random # Import random for progress bar colors

def download_course_material(request, material_id):
    try:
        course_material = get_object_or_404(CourseMaterial, id=material_id) # Use get_object_or_404 is cleaner

        # Ensure the material has a file associated
        if not course_material.file:
             raise Http404("Course material has no file associated with it.")

        file_path = course_material.file.path

        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type='application/octet-stream') # More generic binary type
                    # Get filename and encode properly for header
                    filename = os.path.basename(file_path)
                    try:
                        # Try encoding with utf-8 first
                        filename.encode('utf-8')
                        response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    except UnicodeEncodeError:
                         # Fallback for filenames with characters not in utf-8
                         filename_ascii = filename.encode('ascii', 'ignore').decode('ascii')
                         response['Content-Disposition'] = f'attachment; filename="Download_{filename_ascii}"'

                    # --- REMOVED incorrect render call ---
                    # render(request, 'students/download_course_material.html') # This line was incorrect here
                    return response
            except IOError:
                 raise Http404("Error reading the file.")
        else:
            raise Http404("File does not exist on server.")

    except CourseMaterial.DoesNotExist: # This case is handled by get_object_or_404 now
        raise Http404("Course material not found") # Keep for clarity, though get_object_or_404 raises Http404


@login_required
def course_videos(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    student = get_object_or_404(Student, user=request.user)

    # Authorization check (optional but good)
    if not course.programmes.filter(id=student.program_of_study.id).exists():
        messages.error(request, "You are not enrolled in a programme offering this course.")
        return redirect('students:student_dashboard')

    # Get ALL materials for the course, order as desired
    course_materials = CourseMaterial.objects.filter(course=course).order_by('title') # Or by uploaded_at

    # No need to pre-filter only videos here
    # No need for dummy 'completed' status here unless you implement tracking

    context = {
        'course': course,
        'course_materials': course_materials, # Pass the full queryset
    }
    return render(request, 'students/course_videos.html', context)


@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact support.")
        logout(request) # Log out user if profile is missing
        return redirect('login') # Redirect to login

    # --- Get data based on the student ---
    programme = student.program_of_study
    # Get courses associated with the student's programme
    assigned_courses = programme.courses.all() # Using related_name is efficient

    # --- Course Materials Query (Consider Logic) ---
    course_materials = CourseMaterial.objects.filter(programme=programme)
    
    assignments_for_programme = Assignment.objects.filter(course__programmes=programme).distinct()

    # Exclude assignments already submitted by this student
    submitted_assignment_ids = Submission.objects.filter(student=student).values_list('assignment_id', flat=True)
    pending_assignments = assignments_for_programme.exclude(id__in=submitted_assignment_ids)

    # Filter out assignments past their due date (only show upcoming/current)
    current_datetime = timezone.now()
    upcoming_assignments = pending_assignments.filter(due_date__gte=current_datetime.date()).order_by('due_date')

    results = Result.objects.filter(student=student)
    #current_year, current_semester = student.current_year_and_semester()

    # --- Calculations (Overall Progress) ---
    total_results_count = results.count()
    total_grade_sum = sum(result.grade for result in results if result.grade is not None) # Handle potential None grades
    # Assuming max grade per assignment is 100
    overall_progress = (total_grade_sum / (total_results_count * 100)) * 100 if total_results_count > 0 else 0
    overall_progress = int(overall_progress)

    # --- Course Progress Data ---
    course_progress_data = []
    progress_bar_colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#607D8B"]
    color_index = 0

    # Use the correctly fetched assigned_courses
    for course in assigned_courses:
        course_results = results.filter(course=course)
        course_results_count = course_results.count()
        course_grade_sum = sum(res.grade for res in course_results if res.grade is not None)
        course_overall_progress = (course_grade_sum / (course_results_count * 100)) * 100 if course_results_count > 0 else 0
        course_overall_progress = int(course_overall_progress)

        course_progress_data.append({
            'image': course.image, # Template needs 'if' check for this
            'course_name': course.name,
            'progress': course_overall_progress,
            'progress_color': progress_bar_colors[color_index % len(progress_bar_colors)],
        })
        color_index += 1
        
    # --- Video Annotation ---
    # Renamed variable to avoid conflict
    materials_list = list(course_materials) # Convert queryset to list to add attributes
    for material in materials_list:
        # A slightly more robust check for video types
        is_video_file = False
        if material.video_file and hasattr(material.video_file, 'name'):
             # Basic extension check (can be improved with MIME types if needed)
             is_video_file = material.video_file.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'))
        material.is_video = is_video_file or bool(material.video_link)

    # --- Tutorial Progress ---
    assigned_courses_list = list(assigned_courses) # Convert to list to add attributes
    for course in assigned_courses_list:
        course.tutorial_progress = random.randint(0, 100) # Dummy data

    # --- Context ---
    context = {
        'student': student,
        'programme': programme,
        'course_materials': materials_list, # Pass the list with 'is_video' attribute
        'assignments': upcoming_assignments, # Pass filtered assignments
        'assigned_courses': assigned_courses_list, # Pass the list with 'tutorial_progress'
        'results': results,
        # 'lecturer': lecturer, # Removed lecturer from context
        'overall_progress': overall_progress,
        'current_datetime': current_datetime, # Pass current time if needed in template
        #'current_year': current_year,
        #'current_semester': current_semester,
        'course_progress_data': course_progress_data,
    }
    return render(request, 'students/student_dashboard.html', context)


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = get_object_or_404(Student, user=request.user) # Simpler way to get student

    # Prevent submission if assignment due date has passed
    if assignment.due_date < timezone.now().date():
         messages.error(request, f"The deadline for submitting '{assignment.title}' has passed.")
         return redirect('students:student_dashboard')

    # Prevent re-submission
    if Submission.objects.filter(student=student, assignment=assignment).exists():
         messages.warning(request, f"You have already submitted assignment '{assignment.title}'.")
         return redirect('students:student_dashboard')

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.assignment = assignment
            submission.save()
            messages.success(request, f"Assignment '{assignment.title}' submitted successfully.")
            return redirect('students:student_dashboard')
        # If form is invalid, it will re-render below with errors
    else: # GET request
        form = AssignmentSubmissionForm()

    # --- CORRECTED template path ---
    return render(request, 'students/submit_assignment.html', {'form': form, 'assignment': assignment})


def announcement_view(request):
    # Consider filtering announcements (e.g., by programme, or only active ones) if needed
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'students/announcements.html', {'announcements': announcements})


@login_required
def view_courses(request):
    try:
        # Using related name 'student' on User requires related_name='student' in Student model's OneToOneField
        # If not set, the default is user.student
        student = request.user.student
    except AttributeError:
         # Handle case where student profile doesn't exist or related name is different
         messages.error(request, "Student profile not found.")
         logout(request)
         return redirect('login')

    # --- CORRECTED Course Query using ManyToManyField ---
    # Get courses associated with the student's programme
    # programme_courses = Course.objects.filter(programmes=student.program_of_study)
    # Or using related name:
    programme_courses = student.program_of_study.courses.all()

    context = {
        'student': student,
        'assigned_courses': programme_courses, # Pass the correctly filtered courses
    }
    return render(request, 'students/view_courses.html', context)


def std_logout(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('login') # Redirect to a generic login page, adjust if needed