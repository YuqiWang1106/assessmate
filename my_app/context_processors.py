from django.urls import reverse
from my_app.models import User

def user_dashboard_url(request):
    user_id = request.session.get("user_id")
    user_role = request.session.get("user_role")

    if user_id and user_role:
        try:
            if user_role == 'student':
                return {'user_dashboard_url': reverse('student_courses', args=[user_id])}
            elif user_role == 'teacher':
                return {'user_dashboard_url': reverse('teacher_dashboard', args=[user_id])}
        except Exception as e:
            pass
    return {'user_dashboard_url': reverse('landing')}