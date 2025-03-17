from django.urls import path
from . import views 

urlpatterns = [
    path("teacher_dashboard/<uuid:teacher_id>/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student_dashboard/<uuid:user_id>/", views.student_dashboard, name="student_dashboard"),
    path("", views.landing_page, name="landing"), 
]
