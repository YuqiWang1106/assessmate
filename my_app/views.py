from django.shortcuts import render, get_object_or_404
from .models import Course, Team, Assessment, TeamMember, CourseMember, User
from django.utils.timezone import now
from collections import defaultdict


from django.shortcuts import render
from .models import Course, Team, Assessment
from django.utils.timezone import now

def teacher_dashboard(request, teacher_id):
    """获取教师 Dashboard 数据并渲染 HTML"""

    # 1. 获取当前教师的所有课程
    courses = Course.objects.filter(teacher_id=teacher_id)

    # 2. 检查 GET 参数中是否有 selected_course
    selected_course_id = request.GET.get("selected_course", None)
    
    # 3. 如果有，就用它；如果没有，就默认选第一个课程
    if selected_course_id:
        selected_course = courses.filter(id=selected_course_id).first()
        if not selected_course:
            # 如果 GET 里的 course_id 不在该老师的课程中，就 fallback
            selected_course = courses.first()
    else:
        selected_course = courses.first()
    
    # 4. 构建 teams_dict 和 assessments_dict
    teams_dict = {course.id: list(Team.objects.filter(course=course)) for course in courses}

    assessments_dict = {course.id: list(Assessment.objects.filter(
        course=course,
        status="published", 
        due_date__gte=now()
        )) for course in courses}


    # 5. 渲染模板
    return render(request, "teacher_dashboard.html", {
        "courses": courses,
        "teams_dict": teams_dict,  
        "assessments_dict": assessments_dict,
        "selected_course": selected_course,  
    })


def student_dashboard(request, user_id):
    """Render student dashboard based on student ID"""

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


# def teacher_dashboard(request, teacher_id):
#     """获取教师 Dashboard 数据并渲染 HTML"""

#     courses = Course.objects.filter(teacher_id=teacher_id)
#     upcoming_assessments = Assessment.objects.filter(
#         course__teacher_id=teacher_id,
#         status="published",
#         due_date__gte=now()
#     ).order_by("due_date")[:5]

#     teams_dict = {course.id: list(Team.objects.filter(course=course)) for course in courses}
#     assessments_dict = {course.id: list(Assessment.objects.filter(course=course)) for course in courses}

#     return render(request, "teacher_dashboard.html", {
#         "courses": courses,
#         "upcoming_assessments": upcoming_assessments,
#         "teams_dict": teams_dict,  # 直接改名
#         "assessments_dict": assessments_dict  # 直接改名
#     })
