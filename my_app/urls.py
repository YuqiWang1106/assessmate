from django.urls import path
from . import views 
from my_app.views import delete_course, invite_student

urlpatterns = [
    path("teacher_dashboard/<uuid:teacher_id>/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student_courses/<uuid:user_id>/", views.student_courses, name="student_courses"),
    path("student_dashboard/<uuid:user_id>/", views.student_dashboard, name="student_dashboard"),
    path("", views.landing_page, name="landing"), 
    path("accounts/google/login/", views.google_login, name="google_login"),
    path("accounts/google/callback/", views.google_callback, name="google_callback"),
    path("teacher_courses/<uuid:teacher_id>/", views.teacher_courses, name="teacher_courses"),
    path("new_course/<uuid:teacher_id>/", views.new_course, name="new_course"),
    path("new_team/<uuid:teacher_id>/<uuid:course_id>/", views.new_team, name="new_team"),
    path("edit_team/<uuid:teacher_id>/<uuid:course_id>/<uuid:team_id>/", views.edit_team, name="edit_team"),
    path("remove_from_team/<uuid:teacher_id>/<uuid:course_id>/<uuid:team_id>/<uuid:member_id>/", views.remove_from_team, name='remove_from_team'),
    path("teams_dashboard/<uuid:teacher_id>/", views.teams_dashboard, name="teams_dashboard"),
    path("assessment_dashboard/<uuid:teacher_id>/", views.assessment_dashboard, name="assessment_dashboard"),
    path("create_assessment/<uuid:teacher_id>/<uuid:course_id>/", views.create_assessment, name="create_assessment"),
    path("edit_assessment/<uuid:teacher_id>/<uuid:assessment_id>/<uuid:course_id>/", views.create_assessment, name="edit_assessment"),
    # path("edit_assessment/<uuid:teacher_id>/<uuid:assessment_id>/", views.create_assessment, name="edit_assessment"),
    path("delete_assessment/<uuid:teacher_id>/<uuid:assessment_id>/", views.delete_assessment, name="delete_assessment"),
    path("view_assessment/<uuid:teacher_id>/<uuid:assessment_id>/", views.view_assessment, name="view_assessment"),
    path("delete_course/<uuid:teacher_id>/<uuid:course_id>/", delete_course, name="delete_course"),
    path('invite-student/', invite_student, name='invite_student'),
]
