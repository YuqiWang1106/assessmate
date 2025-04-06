from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Team, Assessment, TeamMember, CourseMember, User, AssessmentResponse, AssessmentQuestion, QuestionAnalysisCache, TeamAssessmentAnalysis, OpenEndedToneAnalysis
from collections import defaultdict
from django.utils.timezone import now
import requests
import urllib.parse
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from .forms import CourseForm, TeamForm
from django.utils import timezone
import json
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from django.contrib import messages


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    
    try:
        user = User.objects.get(email=email)
        if user.role != role:
            return redirect(f"/?error=role_mismatch")
    except User.DoesNotExist:

        user = User.objects.create(
            email=email,
            name=name,
            role=role,
            created_at=now()
        )
        if role == "teacher":
            Course.objects.create(
                teacher=user,
                course_name="Welcome to Assessmate!",
                course_number="Teacher101",
                created_at=now()
            )
        elif role == "student":
            intro_course, _ = Course.objects.get_or_create(
                course_name="Welcome to Assessmate!",
                course_number="Student101",
                defaults={"teacher": None, "created_at": now()}
            )
            CourseMember.objects.create(course=intro_course, user=user)

    

    # store the user session to restrict access to protected pages
    request.session["user_id"] = str(user.id)
    request.session["user_email"] = user.email
    request.session["user_role"] = user.role

    # Invitation Logic
    invited_email = request.session.get("invited_email")
    invited_course_id = request.session.get("invited_course_id")

    if user.role == "student" and invited_email == email and invited_course_id:
        try:
            invited_course = Course.objects.get(id=invited_course_id)
            if not CourseMember.objects.filter(user=user, course=invited_course).exists():
                CourseMember.objects.create(user=user, course=invited_course)
        except Course.DoesNotExist:
            pass

        request.session.pop("invited_email", None)
        request.session.pop("invited_course_id", None)


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

    for course in courses:
            Assessment.objects.filter(
                course=course,
                status="published",
                due_date__lt=timezone.now()
            ).update(status="finished")

    # New teacher without any course yet
    if not courses.exists():
            return render(request, "teacher_dashboard.html", {
                "user": teacher,
                "teacher": teacher,
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
        ).order_by("due_date")[:4]
        ) for course in courses}


    return render(request, "teacher_dashboard.html", {
        "user": teacher,
        "teacher": teacher,
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


def teacher_courses(request, teacher_id):
    """Get Teacher's Courses"""
    if "user_id" not in request.session:
        return redirect("landing")

    teacher = get_object_or_404(User, id=teacher_id, role="teacher")

    selected_semester = request.GET.get("semester")
    selected_year = request.GET.get("year")
    courses = Course.objects.filter(teacher_id=teacher_id)
    semesters = Course.objects.filter(teacher_id=teacher_id).values_list('course_semester', flat=True).distinct()
    years = Course.objects.filter(teacher_id=teacher_id).values_list('course_year', flat=True).distinct()

    courses = Course.objects.filter(teacher=teacher)
    if selected_semester:
        courses = courses.filter(course_semester=selected_semester)
    if selected_year:
        courses = courses.filter(course_year=selected_year)
    
    return render(request, "teacher_courses.html", {
        "teacher": teacher,
        "courses": courses,
        "semesters": semesters, 
        "years": years,
        "selected_semester": selected_semester,
        "selected_year": selected_year,
        
    })
    



def new_course(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., save it to the database)
            course = form.save(commit=False)
            course.teacher = teacher  # Assign teacher from the URL
            course.save()
            #return redirect('teacher_courses')
            return redirect(reverse('teacher_courses', kwargs={'teacher_id': teacher_id}))
            # Save the course to the database or perform other actions
           
    else:
        form = CourseForm()

    semesters = Course.objects.values_list('course_semester', flat=True).distinct()
    years = Course.objects.values_list('course_year', flat=True).distinct()

    return render(request, "new_course.html", {"form": form, "teacher": teacher, "semesters": semesters, "years": years})

def new_team(request, teacher_id, course_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    course = get_object_or_404(Course, id=course_id, teacher=teacher)
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., save it to the database)
            team = form.save(commit=False)
            team.course = course
            team.save()
            return redirect(reverse('edit_team', kwargs={
                'teacher_id': teacher_id, 
                'course_id': course_id,
                'team_id': team.id
                }))
            # Save the course to the database or perform other actions
           
    else:
        form = TeamForm()
    return render(request, "new_team.html", {"form": form, "teacher": teacher, "course": course})

def teams_dashboard(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    courses = Course.objects.filter(teacher=teacher)
    selected_course_id = request.GET.get("course_id")

    if selected_course_id:
        selected_course = get_object_or_404(Course, id=selected_course_id, teacher=teacher)
    else:
        selected_course = courses.first()

    teams = Team.objects.filter(course=selected_course)

    team_data = []
    for team in teams:
        member_count = TeamMember.objects.filter(team=team).count()
        team_data.append({"team": team, "member_count": member_count})

    return render(request, "teams_dashboard.html", {
        "teacher": teacher,
        "selected_course": selected_course,
        "teams": teams,
        "team_data":team_data
    })

def assessment_dashboard(request, teacher_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    courses = Course.objects.filter(teacher=teacher)
    selected_course_id = request.GET.get("course_id")

    if selected_course_id:
        selected_course = get_object_or_404(Course, id=selected_course_id, teacher=teacher)
    else:
        selected_course = courses.first()

    overdue_assessments = Assessment.objects.filter(
        course=selected_course,
        status="published",
        due_date__lt=timezone.now()
    )

    for assessment in overdue_assessments:
        assessment.status = "finished"
        assessment.save()

    draft_assessments = Assessment.objects.filter(course=selected_course, status="draft").order_by("-created_at")
    published_assessments = Assessment.objects.filter(course=selected_course, status="published").order_by("due_date")
    finished_assessments = Assessment.objects.filter(course=selected_course, status="finished").order_by("-due_date")

    return render(request, "assessment_dashboard.html", {
        "teacher": teacher,
        "selected_course": selected_course,
        "draft_assessments": draft_assessments,
        "published_assessments": published_assessments,
        "finished_assessments": finished_assessments,
    })

def edit_team(request, teacher_id, course_id, team_id=None):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    course = get_object_or_404(Course, id=course_id, teacher=teacher)
    team = None

    if team_id:
        team = get_object_or_404(Team, id=team_id, course=course)

    all_course_members = CourseMember.objects.filter(course=course)

    team_members = TeamMember.objects.filter(team=team)
    team_member_ids = team_members.values_list('course_member_id', flat=True)
    remaining_course_members = all_course_members.exclude(id__in=team_member_ids)

    course_members_data = []
    for cm in remaining_course_members:
        existing_team_member = TeamMember.objects.filter(course_member=cm).first()
        course_members_data.append({
            "course_member": cm,
            "team_name": existing_team_member.team.team_name if existing_team_member else None
        })

    return render(request, "edit_team.html", {
        "teacher": teacher,
        "course": course,
        "team": team,
        "team_members": team_members,
        "course_members_data": course_members_data 
    })


def remove_from_team(request, teacher_id, course_id, team_id, member_id):
    if request.method == 'POST':
        member = get_object_or_404(TeamMember, id=member_id, team_id=team_id)
        member.delete()
    return redirect('edit_team', teacher_id=teacher_id, course_id=course_id, team_id=team_id)

def add_to_team(request, teacher_id, course_id, team_id, member_id):
    if request.method == 'POST':
        member = get_object_or_404(CourseMember, id=member_id)
        team = get_object_or_404(Team, id=team_id)
        if TeamMember.objects.filter(team=team, course_member=member).exists():
            # Optional: Show a message that the member is already in the team
            return redirect('edit_team', teacher_id=teacher_id, course_id=course_id, team_id=team_id)

        # Add member to the team
        TeamMember.objects.create(team=team, course_member=member)
    return redirect('edit_team', teacher_id=teacher_id, course_id=course_id, team_id=team_id)


def create_assessment(request, teacher_id, course_id, assessment_id=None):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    course = get_object_or_404(Course, id=course_id, teacher=teacher)
    assessment = None
    questions = []

    if assessment_id:
        assessment = get_object_or_404(Assessment, id=assessment_id, course__teacher=teacher, status="draft")
        questions = AssessmentQuestion.objects.filter(assessment=assessment)

    if request.method == "POST":
        title = request.POST.get("assessment_title", "").strip()
        if not title:
            existing_count = Assessment.objects.filter(
                course=course,
                title__startswith="Untitled Assessment"
            ).count()
            title = f"Untitled Assessment {existing_count + 1}"


        status = "published" if request.POST.get("publish") == "true" else "draft"
        due_date = request.POST.get("due_date")

        if assessment:
            assessment.title = title
            assessment.status = status
            assessment.publish_date = timezone.now() if status == "published" else None
            assessment.due_date = due_date if due_date else None
            assessment.save()
            AssessmentQuestion.objects.filter(assessment=assessment).delete()
        else:
            assessment = Assessment.objects.create(
                course=course,
                title=title,
                status=status,
                publish_date=timezone.now() if status == "published" else None,
                due_date=due_date if due_date else None
            )

        i = 1
        while True:
            text_key = f"question_text_{i}"
            type_key = f"question_type_{i}"
            if text_key not in request.POST:
                break

            AssessmentQuestion.objects.create(
                assessment=assessment,
                question_type=request.POST[type_key],
                content=request.POST[text_key]
            )
            i += 1

        # return redirect("assessment_dashboard", teacher_id=teacher.id)
        return redirect(f"/assessment_dashboard/{teacher.id}/?course_id={course.id}")

    
    return render(request, "create_assessment.html", {
        "teacher": teacher,
        "course": course,
        "course_id": course.id,
        "assessment": assessment,
        "questions": questions,
        "questions_json": json.dumps([
        {"question_type": q.question_type, "content": q.content}
        for q in questions
    ])
    })

def delete_assessment(request, teacher_id, assessment_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    assessment = get_object_or_404(Assessment, id=assessment_id, course__teacher=teacher)
    course_id = request.GET.get("course_id", assessment.course.id)

    AssessmentQuestion.objects.filter(assessment=assessment).delete()
    assessment.delete()

    # return redirect("assessment_dashboard", teacher_id=teacher.id)
    return redirect(f"/assessment_dashboard/{teacher_id}/?course_id={course_id}")

def view_assessment(request, teacher_id, assessment_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    assessment = get_object_or_404(Assessment, id=assessment_id, course__teacher=teacher, status="published")
    questions = AssessmentQuestion.objects.filter(assessment=assessment)
    course_id = request.GET.get("course_id", assessment.course.id)

    return render(request, "create_assessment.html", {
        "teacher": teacher,
        "assessment": assessment,
        "questions": questions,
        "course_id": course_id,
        "questions_json": json.dumps([
            {"question_type": q.question_type, "content": q.content}
            for q in questions
        ]),
        "readonly": True
    })

def delete_team(request, teacher_id, course_id, team_id):
    team = get_object_or_404(Team, id=team_id, course=course_id)

    if request.method == "POST":  # Only allow POST requests for deletion
        team.delete()
        return redirect(reverse('teams_dashboard', kwargs={'teacher_id': teacher_id}))

    return redirect(reverse('teams_dashboard', kwargs={'teacher_id': teacher_id})) 

@csrf_exempt
def delete_course(request, teacher_id, course_id):
    """Delete a course"""
    course = get_object_or_404(Course, id=course_id, teacher_id=teacher_id)
    
    if request.method == "POST":  # Only allow POST requests for deletion
        course.delete()
        return redirect(reverse('teacher_courses', kwargs={'teacher_id': teacher_id}))

    return redirect(reverse('teacher_courses', kwargs={'teacher_id': teacher_id}))

# Sending Invite to Student
@csrf_exempt
@require_POST
def invite_student(request):
    """Invite a student to a course by email (sends email with special invite link)."""
    try:
        data = json.loads(request.body)
        email = data.get("email")
        course_id = data.get("course_id")

        if not email or not course_id:
            return JsonResponse({"success": False, "message": "Missing email or course ID."}, status=400)

        course = get_object_or_404(Course, id=course_id)

        invite_link = f"http://127.0.0.1:8000/invite/accept/?course_id={course_id}&email={email}"

        message = f"""
                        Hi,

                        You have been invited to join the course: "{course.course_name}" on Assessmate!

                        Click the link below to join:
                        {invite_link}

                        After clicking the link, you’ll be prompted to log in or register using your @bc.edu Google account.

                        See you on Assessmate!
                    """

        send_mail(
            subject=f"Invitation to join {course.course_name} on Assessmate",
            message=message,
            from_email="no-reply@assessmate.edu",
            recipient_list=[email],
            fail_silently=False,
        )

        return JsonResponse({"success": True, "message": f"Invitation sent to {email}"})
    
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


# Student Accept Invitation
def accept_invitation(request):
    email = request.GET.get("email")
    course_id = request.GET.get("course_id")

    if not email or not course_id:
        return HttpResponseForbidden("Invalid invitation link.")

    request.session["invited_email"] = email
    request.session["invited_course_id"] = course_id

    return redirect(f"/accounts/google/login/?role=student")

# Sutudent Course Detail
def student_course_detail(request, user_id, course_id):
    if "user_id" not in request.session:
        return redirect("landing")

    student = get_object_or_404(User, id=user_id, role="student")
    course = get_object_or_404(Course, id=course_id)

    Assessment.objects.filter(
        course=course,
        status="published",
        due_date__lt=timezone.now()
    ).update(status="finished")

    current_assessments = Assessment.objects.filter(
        course=course,
        status="published",
        due_date__gte=now()
    ).order_by("due_date")

    finished_assessments = Assessment.objects.filter(
        course=course,
        status="finished"
    ).order_by("-due_date")

    return render(request, "student_course_detail.html", {
        "course": course,
        "user": student,
        "current_assessments": current_assessments,
        "finished_assessments": finished_assessments,
    })

# Student Take Assessment Page
def student_take_assessment(request, user_id, course_id, assessment_id):
    student = get_object_or_404(User, id=user_id, role="student")
    course = get_object_or_404(Course, id=course_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, course=course, status="published")

    if assessment.due_date and assessment.due_date < timezone.now():
        return redirect("student_course_detail", user_id=student.id, course_id=course.id)
   
    course_member = get_object_or_404(CourseMember, user=student, course=course)
    team_member = TeamMember.objects.filter(course_member=course_member).first()

    if not team_member:
        return HttpResponseForbidden("You are not in a team for this course.")

    team = team_member.team
    teammate_members = TeamMember.objects.filter(team=team)
    teammates = [tm.course_member.user for tm in teammate_members]

    return render(request, "student_take_assessment.html", {
        "student": student,
        "course": course,
        "assessment": assessment,
        "teammates": teammates,
    })

# Student Answer Assessment Page
def student_take_assessment_form(request, user_id, course_id, assessment_id, target_user_id):
    student = get_object_or_404(User, id=user_id, role="student")
    course = get_object_or_404(Course, id=course_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, course=course, status="published")
    target_user = get_object_or_404(User, id=target_user_id)

    if assessment.due_date and assessment.due_date < timezone.now():
        return HttpResponseForbidden("This assessment is closed (past deadline).")

    questions = AssessmentQuestion.objects.filter(assessment=assessment)
    questions_json = json.dumps([
        {"question_type": q.question_type, "content": q.content}
        for q in questions
    ])

    try:
        previous_response = AssessmentResponse.objects.get(
            from_user=student,
            to_user=target_user,
            assessment=assessment
        )
        previous_answers = previous_response.answers
    except AssessmentResponse.DoesNotExist:
        previous_answers = {}

    return render(request, "student_answer_assessment.html", {
        "student": student,
        "course": course,
        "assessment": assessment,
        "target_user": target_user,
        "questions_json": questions_json,
        "previous_answers": json.dumps(previous_answers),
    })



@csrf_exempt
@require_POST
def submit_assessment(request):
    try:
        data = json.loads(request.body)
        from_user_id = data.get("student_id")
        to_user_id = data.get("target_user_id")
        assessment_id = data.get("assessment_id")
        answers = data.get("answers")

        from_user = get_object_or_404(User, id=from_user_id, role="student")
        to_user = get_object_or_404(User, id=to_user_id)
        assessment = get_object_or_404(Assessment, id=assessment_id)

        response, created = AssessmentResponse.objects.update_or_create(
            from_user=from_user,
            to_user=to_user,
            assessment=assessment,
            defaults={
                "answers": answers,
                "submitted": True
            }
        )
        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)



# Teacher Result Page with LLM
def teacher_view_results(request, teacher_id, course_id, assessment_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    course = get_object_or_404(Course, id=course_id, teacher=teacher)
    assessment = get_object_or_404(Assessment, id=assessment_id, course=course)
    selected_team_id = request.GET.get("team_id")
    teams = Team.objects.filter(course=course)

    selected_team = None
    team_members = []
    detail_analyses = []
    profile_card = {}

    if selected_team_id:
        selected_team = get_object_or_404(Team, id=selected_team_id, course=course)
        team_member_links = TeamMember.objects.filter(team=selected_team)
        team_members = [tm.course_member.user for tm in team_member_links]
        all_questions = list(AssessmentQuestion.objects.filter(assessment=assessment))

        #1. Detail Part
        for idx, q in enumerate(all_questions, start=1):
            # Check Datavase
            cached = QuestionAnalysisCache.objects.filter(
                team=selected_team,
                assessment=assessment,
                question=q
            ).first()

            if cached:
                detail_analyses.append({
                    "question": q.content,
                    "type": q.question_type,
                    "summary": cached.summary,
                    "analysis": cached.analysis
                })
                continue

            # Answer Block
            qtype = q.question_type
            question_key = f"{qtype}_{idx}"
            answers = []
            print(f"\n=== Question {idx}: {q.content} ({qtype}) ===")
            for from_user in team_members:
                for to_user in team_members:
                    try:
                        r = AssessmentResponse.objects.get(
                            assessment=assessment,
                            from_user=from_user,
                            to_user=to_user
                        )
                        ans = r.answers.get(question_key)
                        if ans:
                            line = f"{from_user.name} → {to_user.name}: {ans}"
                            answers.append(line)
                            # answers.append(f"{from_user.name} → {to_user.name}: {ans}")
                    except AssessmentResponse.DoesNotExist:
                        continue

            if not answers:
                continue

            # Prompt
            if qtype == "open":
                prompt = f"""
                    You are a peer-assessment assistant. Below are all the answers to the question:

                    Question: "{q.content}"

                    Answers:
                    {chr(10).join(answers)}

                    Please generate a structured JSON with:
                    1. "summary": a concise summary of the general feedback or shared opinions from the team;
                    2. "analysis": a performance insight or observation about team collaboration based on the feedback.

                    Output JSON schema:
                    {{
                        "summary": "...",
                        "analysis": "..."
                    }}
                """
            else:
                prompt = f"""
                    You are a peer-assessment assistant. Below are Likert scale answers to the question:

                    Question: "{q.content}"

                    Each answer is on a scale from 1 to 5:
                    1 = Strongly Agree, 2 = Agree, 3 = Neutral, 4 = Disagree, 5 = Strongly Disagree

                    Answers:
                    {chr(10).join(answers)}

                    Please analyze the overall sentiment and what it reflects about team collaboration.
                    Output structured JSON with:
                    {{
                        "summary": "...",
                        "analysis": "..."
                    }}
                """

            print("\n==== Prompt to LLM ====\n", prompt)

            try:
                response = client.responses.create(
                    model="gpt-4o-2024-08-06",
                    input=[
                        {"role": "system", "content": "You are a helpful assistant that analyzes peer assessment data and outputs structured JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "peer_assessment_analysis",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "summary": {"type": "string"},
                                    "analysis": {"type": "string"}
                                },
                                "required": ["summary", "analysis"],
                                "additionalProperties": False
                            },
                            "strict": True
                        }
                    }
                )

                result = json.loads(response.output_text)
                print("\n=== LLM Result ===")
                print("Summary:", result.get("summary"))
                print("Analysis:", result.get("analysis"))

                detail_analyses.append({
                    "question": q.content,
                    "type": qtype,
                    "summary": result["summary"],
                    "analysis": result["analysis"]
                })

                # Store Data
                QuestionAnalysisCache.objects.create(
                    team=selected_team,
                    assessment=assessment,
                    question=q,
                    question_type=qtype,
                    summary=result["summary"],
                    analysis=result["analysis"]
                )

            except Exception as e:
                detail_analyses.append({
                    "question": q.content,
                    "type": qtype,
                    "summary": "LLM error.",
                    "analysis": str(e)
                })

        # 2. Overall
        cached_profile = TeamAssessmentAnalysis.objects.filter(
            team=selected_team,
            assessment=assessment
        ).first()

        if cached_profile:
            profile_card = {
                "overall_rating": cached_profile.overall_rating,
                "keywords": cached_profile.keywords,
                "summary": cached_profile.summary,
                "suggestions": cached_profile.suggestions,
                "radar_scores": cached_profile.radar_scores
            }
        else:
            all_blocks = []
            for idx, q in enumerate(all_questions, start=1):
                key = f"{q.question_type}_{idx}"
                block = [f"Question: {q.content}"]
                for from_user in team_members:
                    for to_user in team_members:
                        try:
                            r = AssessmentResponse.objects.get(
                                assessment=assessment,
                                from_user=from_user,
                                to_user=to_user
                            )
                            ans = r.answers.get(key)
                            if ans:
                                block.append(f"{from_user.name} → {to_user.name}: {ans}")
                        except AssessmentResponse.DoesNotExist:
                            continue
                if len(block) > 1:
                    all_blocks.append("\n".join(block))

            joined_blocks = "\n\n".join(all_blocks)

            profile_prompt = f"""
            You are a peer-assessment analyzer. Below is a full set of responses from a team, including open-ended answers and Likert scale ratings. 
            Your task is to evaluate the team’s overall collaboration, communication, and group dynamics.

            Likert scale values:
            1 = Strongly Agree, 2 = Agree, 3 = Neutral, 4 = Disagree, 5 = Strongly Disagree

            Assessment data:
            {joined_blocks}

            Please return a structured JSON with the following fields:

            {{
                "overall_rating": float,  // A number from 0 to 5 (inclusive), in steps of 0.5.

                "keywords": list of 3 to 5 concise descriptive labels capturing team performance dimensions:
                    - teamwork (e.g., "collaborative", "conflict-prone", "supportive")
                    - communication (e.g., "clear", "unclear", "passive")
                    - participation (e.g., "engaged", "uneven", "inactive")
                    - consistency (e.g., "aligned", "discrepant", "self-critical")

                "summary": A short summary (max 3 sentences) describing the team’s dynamics, key strengths, or issues.

                "suggestions": A brief paragraph (max 2 sentences) giving constructive advice to help the team improve performance and collaboration.

                "radar_scores": {{
                    "collaboration": int (0–100),
                    "communication": int (0–100),
                    "participation": int (0–100),
                    "respect": int (0–100),
                    "consistency": int (0–100)
                }}
            }}

            Guidelines:
            - Use radar_scores to reflect relative strengths (not just raw quality).
            - Prefer mid-range values (40–80) unless data clearly indicates strong extremes.
            - 100 means excellent and consistent performance; 0 means severe problems.
            - Stay objective and constructive.

            !!! Output only a valid JSON object. No explanations or extra text.
            """

            print("\n==== Profile Card Prompt ====\n", profile_prompt)

            try:
                profile_response = client.responses.create(
                    model="gpt-4o-2024-08-06",
                    input=[
                        {"role": "system", "content": "You summarize and evaluate peer assessments."},
                        {"role": "user", "content": profile_prompt}
                    ],
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "team_profile_card",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "overall_rating": {"type": "number"},
                                    "keywords": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "summary": {"type": "string"},
                                    "suggestions": {"type": "string"},
                                    "radar_scores": {
                                        "type": "object",
                                        "properties": {
                                            "collaboration": {"type": "integer"},
                                            "communication": {"type": "integer"},
                                            "participation": {"type": "integer"},
                                            "respect": {"type": "integer"},
                                            "consistency": {"type": "integer"}
                                        },
                                        "required": ["collaboration", "communication", "participation", "respect", "consistency"],
                                        "additionalProperties": False
                                    }
                                },
                                "required": ["overall_rating", "keywords", "summary", "suggestions", "radar_scores"],
                                "additionalProperties": False
                            },
                            "strict": True
                        }
                    }
                )

                print("\n=== Raw Profile Output ===")
                print(profile_response.output_text)

                parsed = json.loads(profile_response.output_text)
                profile_card = parsed

                print("\n=== Parsed Profile Card ===")
                print(json.dumps(profile_card, indent=2))

                # Store to Database
                TeamAssessmentAnalysis.objects.create(
                    team=selected_team,
                    assessment=assessment,
                    overall_rating=parsed["overall_rating"],
                    keywords=parsed["keywords"],
                    summary=parsed["summary"],
                    suggestions=parsed["suggestions"],
                    radar_scores=parsed["radar_scores"]
                )

            except Exception as e:
                print("[PROFILE CARD ERROR]", e)
                if 'profile_response' in locals():
                    print("Raw LLM output (possibly invalid JSON):")
                    print(getattr(profile_response, "output_text", "[no output_text]"))

                profile_card = {
                    "overall_rating": 0.0,
                    "keywords": [],
                    "summary": "LLM error.",
                    "suggestions": str(e),
                    "radar_scores": {
                        "collaboration": 0,
                        "communication": 0,
                        "participation": 0,
                        "respect": 0,
                        "consistency": 0
                    }
                }

    return render(request, "teacher_view_results.html", {
        "teacher": teacher,
        "course": course,
        "assessment": assessment,
        "teams": teams,
        "selected_team": selected_team,
        "team_members": team_members,
        "detail_analyses": detail_analyses,
        "profile_card": profile_card,
        "radar_scores": profile_card.get("radar_scores", {})
    })


# Tecaher Check Student Detail
def teacher_student_detail(request, teacher_id, course_id, assessment_id, team_id, student_id):
    teacher = get_object_or_404(User, id=teacher_id, role="teacher")
    course = get_object_or_404(Course, id=course_id, teacher=teacher)
    assessment = get_object_or_404(Assessment, id=assessment_id, course=course)
    team = get_object_or_404(Team, id=team_id, course=course)
    selected_student = get_object_or_404(User, id=student_id)

    team_member_links = TeamMember.objects.filter(team=team)
    team_members = [tm.course_member.user for tm in team_member_links]
    questions = AssessmentQuestion.objects.filter(assessment=assessment)

    all_answers = []

    for from_user in team_members:
        try:
            response = AssessmentResponse.objects.get(
                assessment=assessment,
                from_user=from_user,
                to_user=selected_student,
            )
        except AssessmentResponse.DoesNotExist:
            continue

        answer_block = {
            "from_user": from_user,
            "answers": []
        }

        for idx, question in enumerate(questions, start=1):
            key = f"{question.question_type}_{idx}"
            original = response.answers.get(key, "No answer")

            item = {
                "question": question.content,
                "type": question.question_type,
                "answer": original,
                "key": key
            }

            if question.question_type == "open" and original != "No answer":
                cache = OpenEndedToneAnalysis.objects.filter(
                    assessment=assessment,
                    question=question,
                    from_user=from_user,
                    to_user=selected_student
                ).first()

                if cache:
                    item["tone_analysis"] = cache.tone_feedback
                    item["rewritten"] = cache.rewritten_answer
                else:
                    prompt = f"""
                    You're a helpful assistant reviewing peer feedback for tone and language. 
                    A student wrote the following answer in a peer assessment:

                    "{original}"

                    Please output a JSON with two fields:
                    1. "tone_feedback": a 3-sentence evaluation of the wording, tone, and appropriateness.
                    2. "rewritten_answer": a safer, kinder, and more constructive version of the same answer.

                    IMPORTANT:
                    - The rewritten version should preserve the original meaning.
                    - Keep the sentence **structure and number of sentences similar to the original**.
                    - Try to match the **length and style** of the original, unless the original is clearly inappropriate.
                    - Do NOT add extra commentary or explanations.

                    Output JSON format:
                    {{
                        "tone_feedback": "...",
                        "rewritten_answer": "..."
                    }}
"""


                    try:
                        result = client.responses.create(
                            model="gpt-4o-2024-08-06",
                            input=[
                                {"role": "system", "content": "You evaluate tone and rewrite sensitive text."},
                                {"role": "user", "content": prompt}
                            ],
                            text={
                                "format": {
                                    "type": "json_schema",
                                    "name": "tone_check",
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "tone_feedback": {"type": "string"},
                                            "rewritten_answer": {"type": "string"}
                                        },
                                        "required": ["tone_feedback", "rewritten_answer"],
                                        "additionalProperties": False
                                    },
                                    "strict": True
                                }
                            }
                        )
                        parsed = json.loads(result.output_text)
  
                        item["tone_analysis"] = parsed["tone_feedback"]
                        item["rewritten"] = parsed["rewritten_answer"]

                        OpenEndedToneAnalysis.objects.create(
                            assessment=assessment,
                            question=question,
                            from_user=from_user,
                            to_user=selected_student,
                            tone_feedback=parsed["tone_feedback"],
                            rewritten_answer=parsed["rewritten_answer"]
                        )

                    except Exception as e:
                        item["tone_analysis"] = "LLM error."
                        item["rewritten"] = "Could not generate rewritten version."

            answer_block["answers"].append(item)

        all_answers.append(answer_block)

    return render(request, "teacher_student_detail.html", {
        "teacher": teacher,
        "course": course,
        "assessment": assessment,
        "team": team,
        "selected_student": selected_student,
        "team_members": team_members,
        "all_answers": all_answers,
    })


# Edit Answer
@require_POST
@csrf_protect
def edit_open_answer(request):
    from_user_id = request.POST.get("from_user_id")
    to_user_id = request.POST.get("to_user_id")
    assessment_id = request.POST.get("assessment_id")
    question_key = request.POST.get("question_key")
    new_answer = request.POST.get("new_answer", "").strip()

    try:
        response = AssessmentResponse.objects.get(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            assessment_id=assessment_id
        )
        answers = response.answers or {}
        answers[question_key] = new_answer
        response.answers = answers
        response.save()
        return redirect(request.META.get("HTTP_REFERER", "/"))
    except AssessmentResponse.DoesNotExist:
        return JsonResponse({"success": False, "message": "Response not found."}, status=404)


# Publish Results
@require_POST
@csrf_protect
def toggle_results_publish(request):
    assessment_id = request.POST.get("assessment_id")
    action = request.POST.get("action")
    teacher_id = request.POST.get("teacher_id")
    course_id = request.POST.get("course_id")

    assessment = get_object_or_404(Assessment, id=assessment_id)
    course = assessment.course

    if action == "publish":
        assessment.results_released = True
        assessment.save()

        # 获取所有课程学生
        student_memberships = CourseMember.objects.filter(course=course)
        student_emails = [cm.user.email for cm in student_memberships]

        # 构建跳转链接（到该课程下的 assessment results 页面）
        login_link = f"http://127.0.0.1:8000/accounts/google/login/?role=student&next=/student_course_detail/{course_id}/"

        message = f"""
        Hello,

        The results for the assessment **"{assessment.title}"** in course **{course.course_number} - {course.course_name}** have just been released on Assessmate 🎉.

        You can now log in to view your feedback and team summary.

        👉 Click the link below to login and check it out:
        {login_link}

        See you on Assessmate!
        """

        send_mail(
            subject=f"[Assessmate] Results released for {assessment.title}",
            message=message,
            from_email="no-reply@assessmate.edu",
            recipient_list=student_emails,
            fail_silently=False,
        )

        messages.success(request, "Results have been published and students notified!")

    elif action == "unpublish":
        assessment.results_released = False
        assessment.save()
        messages.info(request, "Results have been unpublished.")
    else:
        messages.error(request, "Invalid action.")

    return redirect(reverse("teacher_view_results", kwargs={
        "teacher_id": teacher_id,
        "course_id": course_id,
        "assessment_id": assessment_id
    }))

# @require_POST
# @csrf_protect
# def toggle_results_publish(request):
#     assessment_id = request.POST.get("assessment_id")
#     action = request.POST.get("action")
#     teacher_id = request.POST.get("teacher_id")
#     course_id = request.POST.get("course_id")

#     assessment = get_object_or_404(Assessment, id=assessment_id)

#     if action == "publish":
#         assessment.results_released = True
#         messages.success(request, "Results have been published successfully!")
#     elif action == "unpublish":
#         assessment.results_released = False
#         messages.info(request, "Results have been unpublished.")
#     else:
#         messages.error(request, "nvalid action.")
        
#     assessment.save()

#     return redirect(reverse("teacher_view_results", kwargs={
#         "teacher_id": teacher_id,
#         "course_id": course_id,
#         "assessment_id": assessment_id
#     }))


# Student Result Page
def student_view_results(request, user_id, course_id, assessment_id):
    student = get_object_or_404(User, id=user_id, role="student")
    course = get_object_or_404(Course, id=course_id)
    assessment = get_object_or_404(Assessment, id=assessment_id, course=course, status="finished")

    if not assessment.results_released:
        return HttpResponseForbidden("Results are not yet released.")

    course_member = get_object_or_404(CourseMember, user=student, course=course)
    team_member = TeamMember.objects.filter(course_member=course_member).first()
    if not team_member:
        return HttpResponseForbidden("You are not in a team for this course.")
    team = team_member.team

    teammates = [tm.course_member.user for tm in TeamMember.objects.filter(team=team)]

    questions = AssessmentQuestion.objects.filter(assessment=assessment)

    likert_results = []
    open_ended_results = []

    for idx, question in enumerate(questions, start=1):
        key = f"{question.question_type}_{idx}"

        if question.question_type == "likert":
            scores = []
            for from_user in teammates:
                try:
                    response = AssessmentResponse.objects.get(
                        assessment=assessment,
                        from_user=from_user,
                        to_user=student
                    )
                    score = int(response.answers.get(key, 0))
                    scores.append(score)
                except AssessmentResponse.DoesNotExist:
                    continue

            if scores:
                likert_results.append({
                    "question": question.content,
                    "student_avg": round(sum(scores) / len(scores), 2),
                    "team_low": min(scores),
                    "team_high": max(scores),
                    "team_mean": round(sum(scores) / len(scores), 2)
                })

        elif question.question_type == "open":
            responses = []
            for from_user in teammates:
                try:
                    response = AssessmentResponse.objects.get(
                        assessment=assessment,
                        from_user=from_user,
                        to_user=student
                    )
                    answer = response.answers.get(key)
                    if answer:
                        responses.append(answer)
                except AssessmentResponse.DoesNotExist:
                    continue

            if responses:
                open_ended_results.append({
                    "question": question.content,
                    "answers": responses
                })

    return render(request, "student_view_results.html", {
        "student": student,
        "course": course,
        "assessment": assessment,
        "likert_results": likert_results,
        "open_ended_results": open_ended_results,
    })



