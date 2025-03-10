from django.shortcuts import render, redirect
from .models import Assignment, Submission, Student, Result, StudentProfile, Course, CourseMaterial
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


def download_course_material(request, material_id):
    try:
        course_material = CourseMaterial.objects.get(id=material_id)
        file_path = course_material.file.path
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/force-download')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
                render(request, 'students/download_course_material.html')
                return response
        else:
            raise Http404("File does not exist")
    
    except CourseMaterial.DoesNotExist:
        raise Http404("Course material not found")
    
@login_required
def course_videos(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course_materials = CourseMaterial.objects.filter(course=course)

    # Filter for videos only
    videos = [material for material in course_materials if material.video_file or material.video_link]
    #add completed status
    for video in videos:
        video.completed = False # You might store this in the database

    return render(request, 'students/course_videos.html', {'course': course, 'videos': videos})


@login_required
def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None

    if student:
        programme = student.program_of_study
        course_materials = CourseMaterial.objects.filter(programme=student.program_of_study)
        assignments = Assignment.objects.filter(programme=student.program_of_study)
        assigned_courses = Course.objects.filter(programme=student.program_of_study)
        results = Result.objects.filter(student=student)
        announcements = Announcement.objects.filter(target_group__in=['students', 'both']).order_by('-created_at')
        current_year, current_semester = student.current_year_and_semester()
        
        # Calculate overall progress
        total_assignments = results.count()
        total_grade = sum(result.grade for result in results)
        overall_progress = (total_grade / (total_assignments * 100)) * 100 if total_assignments > 0 else 0
       
        # Check if the course has an assigned lecturer
        lecturer = None
        
        # Exclude assignments that have been submitted
        submitted_assignments = Submission.objects.filter(student=student).values_list('assignment_id', flat=True)
        assignments = assignments.exclude(id__in=submitted_assignments)
        
        if assignments.exists():
            first_assignment = assignments.first()  # Assuming the course has a lecturer
            lecturer = first_assignment.lecturer if first_assignment.lecturer else None
        
        current_datetime = timezone.now()
        assignments = assignments.filter(due_date__gt=current_datetime)
        
        # Annotate each material with a flag to indicate whether it's a video
        
        for material in course_materials:
            if material.video_file:
                material.is_video = material.video_file.name.endswith(('.mp4', '.avi', '.mov', '.mkv'))  # Add more extensions as needed
            else:
                material.is_video = False
            
        return render(request, 'students/student_dashboard.html', {
            'student': student,
            'programme': programme,
            'course_materials': course_materials,
            'assignments': assignments,
            'assigned_courses': assigned_courses,
            'results': results,
            'lecturer': lecturer,
            'overall_progress': overall_progress,
            'current_datetime': current_datetime,
            'current_year': current_year,
            'current_semester': current_semester,
        })
    else:
        return redirect('login')

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
        # Get the Student object associated with the logged-in user
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('students:student_dashboard')
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.assignment = assignment
            submission.save()
            return redirect('students:student_dashboard')
    else:
        form = AssignmentSubmissionForm()

    return render(request, 'students/submit_assignment.html/', {'form': form, 'assignment': assignment})

def announcement_view(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'students/announcements.html', {'announcements': announcements})

@login_required
def view_courses(request):
    student = request.user.student  # Get the logged-in student's profile
    assigned_courses = Course.objects.filter(programme=student.program_of_study)  # Fetch courses by student's programme

    context = {
        'student': student,
        'assigned_courses': assigned_courses,
    }
    
    return render(request, 'students/view_courses.html', context)

def std_logout(request):
    logout(request)  # This will remove the user session and log them out
    messages.success(request, "Successfully logged out.")
    return redirect('login')  # Redirect to lecturer login page