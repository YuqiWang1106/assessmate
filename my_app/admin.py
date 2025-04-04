from django.contrib import admin
from .models import User, Course, CourseMember, Team, TeamMember, Assessment, AssessmentQuestion, AssessmentResponse, TeamAssessmentAnalysis, QuestionAnalysisCache, OpenEndedToneAnalysis

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "name", "role", "created_at")  
    search_fields = ("email", "name")  
    list_filter = ("role", "created_at")  
    readonly_fields = ("id", "created_at")  


class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "course_number", "course_name", "teacher", "created_at", 'course_semester', 'course_year')
    search_fields = ("course_number", "course_name", "course_semester", "course_year")
    list_filter = ("created_at", "course_semester", "course_year")
    readonly_fields = ("id", "created_at")


class CourseMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "user", "joined_at")
    search_fields = ("course__course_number", "user__name", "user__email")
    list_filter = ("course", "joined_at")
    readonly_fields = ("id", "joined_at")


class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "team_name", "course", "created_at")
    search_fields = ("team_name", "course__course_number")
    list_filter = ("course", "created_at")
    readonly_fields = ("id", "created_at")


class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "course_member", "joined_at")
    search_fields = ("team__team_name", "course_member__user__name")
    list_filter = ("team", "joined_at")
    readonly_fields = ("id", "joined_at")


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "status", "publish_date", "due_date", "results_released", "created_at")
    search_fields = ("title", "course__course_number")
    list_filter = ("status", "course", "publish_date", "due_date", "created_at")
    readonly_fields = ("id", "created_at")


class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "question_type", "content")
    search_fields = ("assessment__title", "content")
    list_filter = ("question_type", "assessment")
    readonly_fields = ("id",)


class AssessmentResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "from_user", "to_user", "submitted", "last_saved")
    search_fields = ("assessment__title", "from_user__name", "to_user__name")
    list_filter = ("submitted", "assessment")
    readonly_fields = ("id", "last_saved")



class TeamAssessmentAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "team",
        "assessment",
        "overall_rating",
        "keywords",         
        "summary",
        "suggestions",
        "radar_scores",     
        "created_at"
    )
    search_fields = ("team__team_name", "assessment__title")
    list_filter = ("team", "assessment")
    readonly_fields = ("created_at",)


class QuestionAnalysisCacheAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "team",
        "assessment",
        "question",
        "question_type",
        "summary",
        "analysis",
        "created_at"
    )
    search_fields = ("question__content", "team__team_name")
    list_filter = ("question_type", "assessment")
    readonly_fields = ("created_at",)

class OpenEndedToneAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "assessment", 
        "question", 
        "from_user", 
        "to_user", 
        "tone_feedback", 
        "rewritten_answer", 
        "created_at"
    )
    search_fields = (
        "assessment__title", 
        "question__content", 
        "from_user__name", 
        "to_user__name"
    )
    list_filter = ("assessment", "question", "created_at")
    readonly_fields = ("id", "created_at")


admin.site.register(User, UserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseMember, CourseMemberAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(AssessmentQuestion, AssessmentQuestionAdmin)
admin.site.register(AssessmentResponse, AssessmentResponseAdmin)
admin.site.register(TeamAssessmentAnalysis, TeamAssessmentAnalysisAdmin)
admin.site.register(QuestionAnalysisCache, QuestionAnalysisCacheAdmin)
admin.site.register(OpenEndedToneAnalysis, OpenEndedToneAnalysisAdmin)