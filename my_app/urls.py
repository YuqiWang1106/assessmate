from django.urls import path
from . import views 

urlpatterns = [
    path("teacher_dashboard/<uuid:teacher_id>/", views.teacher_dashboard, name="teacher_dashboard"),
]
