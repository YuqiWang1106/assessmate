from django.contrib import admin
from .models import User, Course, CourseMember, Team, TeamMember, Assessment, AssessmentQuestion, AssessmentResponse

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "role", "created_at")  
    search_fields = ("email", "name")  
    readonly_fields = ("id", "created_at")  

admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(CourseMember)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Assessment)
admin.site.register(AssessmentQuestion)
admin.site.register(AssessmentResponse)


