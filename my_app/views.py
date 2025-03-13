from django.shortcuts import render
from .models import Course, Team, Assessment
from django.utils.timezone import now
from collections import defaultdict

def teacher_dashboard(request, teacher_id):
    """获取教师 Dashboard 数据并渲染 HTML"""

    courses = Course.objects.filter(teacher_id=teacher_id)
    upcoming_assessments = Assessment.objects.filter(
        course__teacher_id=teacher_id,
        status="published",
        due_date__gte=now()
    ).order_by("due_date")[:5]

    teams_dict = {course.id: list(Team.objects.filter(course=course)) for course in courses}
    assessments_dict = {course.id: list(Assessment.objects.filter(course=course)) for course in courses}

    return render(request, "teacher_dashboard.html", {
        "courses": courses,
        "upcoming_assessments": upcoming_assessments,
        "teams_dict": teams_dict,  # 直接改名
        "assessments_dict": assessments_dict  # 直接改名
    })
