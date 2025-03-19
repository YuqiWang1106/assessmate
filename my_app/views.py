from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Team, Assessment, TeamMember, CourseMember, User
from django.utils.timezone import now
from collections import defaultdict


from django.shortcuts import render
from .models import Course, Team, Assessment
from django.utils.timezone import now

import requests
import urllib.parse
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from .models import User

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/accounts/google/callback/"


def google_login(request):
    """Sends user to correct login page, based on selected role"""
    role = request.GET.get("role")
    if role not in ["student", "teacher"]:
        return redirect("landing") # redirect back to landing page if role missing/invalid
    
    # constructs Google OAuth login URL
    params = {
        "client_id": "***REMOVED***",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": role,
        "prompt": "select_account",
    }
    return redirect(f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}")

def google_callback(request):
    """After successful Google login, retrieves user info and redirects to proper dashboard"""
    code = request.GET.get("code") # gets authorization code from Google's response after successful login
    role = request.GET.get("state") # role from url, created in google_login()

    if not code or not role:
        return redirect("landing")
    
    # authorization code is exchanged to get token ID
    data = {
        "code": code,
        "client_id": "***REMOVED***",
        "client_secret": "***REMOVED***",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    token_info = response.json()

    if "id_token" not in token_info:
        return redirect("landing")
    
    # with token ID, can get info on user from Google
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    user_info_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    user_info = user_info_response.json()

    email = user_info.get("email")
    name = user_info.get("name")

    # ensures only BC emails can have further access
    if not email.endswith("@bc.edu"):
        return HttpResponseForbidden("Please use a @bc.edu email")
    
    # checks if user exists, if not, creates user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"name": name, "role": role, "created_at": now()},
    )

    # store the user session to restrict access to protected pages -> done in dashboard views
    request.session["user_id"] = str(user.id)
    request.session["user_email"] = user.email
    request.session["user_role"] = user.role

    # redirects user to their respective dashboard
    if user.role == "teacher":
        return redirect("teacher_dashboard", teacher_id=user.id)
    else:
        return redirect("student_courses", user_id=user.id)



def teacher_dashboard(request, teacher_id):
    """Get Teacher Dashboard Data"""
    if "user_id" not in request.session:
        return redirect("landing")

    teacher = get_object_or_404(User, id=teacher_id, role="teacher")

    courses = Course.objects.filter(teacher_id=teacher_id)

    # New teacher without any course yet
    if not courses.exists():
            return render(request, "teacher_dashboard.html", {
                "user": teacher,
                "courses": courses,
                "teams_dict": {},  
                "assessments_dict": {},
                "selected_course": None,
                "no_courses": True,
            })

    # Teacher already has at least 1 course
    selected_course_id = request.GET.get("selected_course")
    selected_course = None
    
    if selected_course_id:
        selected_course = courses.filter(id=selected_course_id).first()
        if not selected_course:
            selected_course = courses.first()
    else:
        selected_course = courses.first()
    

    teams_dict = {course.id: list(Team.objects.filter(course=course)) for course in courses}

    assessments_dict = {course.id: list(Assessment.objects.filter(
        course=course,
        status="published", 
        due_date__gte=now()
        )) for course in courses}


    return render(request, "teacher_dashboard.html", {
        "user": teacher,
        "courses": courses,
        "teams_dict": teams_dict,  
        "assessments_dict": assessments_dict,
        "selected_course": selected_course,
        "no_courses": False, 
    })


def student_courses(request, user_id):
    if "user_id" not in request.session:
        return redirect("landing")

    # Ensure the user exists and is a student
    student = get_object_or_404(User, id=user_id, role="student")

    # Get the courses the student is enrolled in
    course_memberships = CourseMember.objects.filter(user=student)
    courses = [cm.course for cm in course_memberships]
    return render(request, "student_courses.html", {
        "courses": courses,
        "user": student,
    })

def student_dashboard(request, user_id):
    """Render student dashboard based on student ID"""
    if "user_id" not in request.session:
        return redirect("landing")

    # Ensure the user exists and is a student
    student = get_object_or_404(User, id=user_id, role="student")

    # Get the courses the student is enrolled in
    course_memberships = CourseMember.objects.filter(user=student)
    courses = [cm.course for cm in course_memberships]

    # Get teams the student is part of
    teams_dict = {course.id: [] for course in courses}
    for cm in course_memberships:
        team_memberships = TeamMember.objects.filter(course_member=cm)
        teams_dict[cm.course.id] = [tm.team for tm in team_memberships]

    # Get assessments courses
    assessments_dict = {course.id: list(Assessment.objects.filter(course=course)) for course in courses}

    return render(request, "student_dashboard.html", {
        "courses": courses,
        "teams_dict": teams_dict,
        "assessments_dict": assessments_dict,
    })

def landing_page(request):
    return render(request, 'landing_page.html')
