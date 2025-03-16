# from django.contrib import admin
# from .models import User, Course, CourseMember, Team, TeamMember, Assessment, AssessmentQuestion, AssessmentResponse

# class UserAdmin(admin.ModelAdmin):
#     list_display = ("id", "email", "name", "role", "created_at")  
#     search_fields = ("email", "name")  
#     readonly_fields = ("id", "created_at")  

# admin.site.register(User, UserAdmin)
# admin.site.register(Course)
# admin.site.register(CourseMember)
# admin.site.register(Team)
# admin.site.register(TeamMember)
# admin.site.register(Assessment)
# admin.site.register(AssessmentQuestion)
# admin.site.register(AssessmentResponse)


from django.contrib import admin
from .models import User, Course, CourseMember, Team, TeamMember, Assessment, AssessmentQuestion, AssessmentResponse

# 1. 用户管理
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "role", "created_at")  
    search_fields = ("email", "name")  
    list_filter = ("role", "created_at")  
    readonly_fields = ("id", "created_at")  

# 2. 课程管理
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "course_number", "course_name", "teacher", "created_at")
    search_fields = ("course_number", "course_name")
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at")

# 3. 课程成员管理
class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "user", "joined_at")
    search_fields = ("course__course_number", "user__name", "user__email")
    list_filter = ("course", "joined_at")
    readonly_fields = ("id", "joined_at")

# 4. 团队管理
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "team_name", "course", "created_at")
    search_fields = ("team_name", "course__course_number")
    list_filter = ("course", "created_at")
    readonly_fields = ("id", "created_at")

# 5. 团队成员管理
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "course_member", "joined_at")
    search_fields = ("team__team_name", "course_member__user__name")
    list_filter = ("team", "joined_at")
    readonly_fields = ("id", "joined_at")

# 6. 评估管理
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "status", "publish_date", "due_date", "results_released", "created_at")
    search_fields = ("title", "course__course_number")
    list_filter = ("status", "course", "publish_date", "due_date", "created_at")
    readonly_fields = ("id", "created_at")

# 7. 评估问题管理
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "question_type", "content")
    search_fields = ("assessment__title", "content")
    list_filter = ("question_type", "assessment")
    readonly_fields = ("id",)

# 8. 评估反馈管理
class AssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "from_user", "to_user", "submitted", "last_saved")
    search_fields = ("assessment__title", "from_user__name", "to_user__name")
    list_filter = ("submitted", "assessment")
    readonly_fields = ("id", "last_saved")

# 注册到 Django Admin
admin.site.register(User, UserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseMember, CourseMemberAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(AssessmentQuestion, AssessmentQuestionAdmin)
admin.site.register(AssessmentResponse, AssessmentResponseAdmin)
