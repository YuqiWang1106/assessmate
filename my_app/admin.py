from django.contrib import admin
from .models import User, Course, Team, TeamMember, Assessment, AssessmentQuestion, AssessmentResponse

admin.site.register(User)
admin.site.register(Course)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Assessment)
admin.site.register(AssessmentQuestion)
admin.site.register(AssessmentResponse)
