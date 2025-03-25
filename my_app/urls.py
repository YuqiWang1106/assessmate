from django.urls import path
from . import views 

urlpatterns = [
    path("teacher_dashboard/<uuid:teacher_id>/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student_courses/<uuid:user_id>/", views.student_courses, name="student_courses"),
    path("student_dashboard/<uuid:user_id>/", views.student_dashboard, name="student_dashboard"),
    path("", views.landing_page, name="landing"), 
    path("accounts/google/login/", views.google_login, name="google_login"),
    path("accounts/google/callback/", views.google_callback, name="google_callback"),
    path("teacher_courses/<uuid:teacher_id>/", views.teacher_courses, name="teacher_courses"),
    path("new_course/<uuid:teacher_id>/", views.new_course, name="new_course"),
    path("assessment_dashboard/<uuid:teacher_id>/", views.assessment_dashboard, name="assessment_dashboard"),
    path("create_assessment/<uuid:teacher_id>/", views.create_assessment, name="create_assessment"),
    path("edit_assessment/<uuid:teacher_id>/<uuid:assessment_id>/", views.create_assessment, name="edit_assessment"),
]
