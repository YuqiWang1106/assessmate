from django import template

register = template.Library()

@register.filter
def exclude_team_members(course_members, team_members):
    team_member_ids = [member.course_member.id for member in team_members]
    return [member for member in course_members if member.id not in team_member_ids]
