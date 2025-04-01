from django import forms
from .models import Course, User, Team, TeamMember
'''
class CourseForm(forms.Form):
    #course_number = forms.CharField(max_length=20, label="Course Number")
    course_number = forms.CharField(
        max_length=20, 
        label="Course Number",
        widget=forms.TextInput(attrs={'placeholder': 'ex. CSCI3356'})
    )
    course_name = forms.CharField(
        max_length=100,
        label="Course Name", 
        widget= forms.TextInput(attrs={'placeholder': 'ex. Software Engineering'})
    )
'''

class CourseForm(forms.ModelForm):
    SEMESTER_CHOICES = [
        ('Spring', 'Spring'),
        ('Summer', 'Summer'),
        ('Fall', 'Fall'),
    ]

    course_semester = forms.ChoiceField(
        choices=SEMESTER_CHOICES,
        label="Semester",
        widget=forms.Select(attrs={'class': 'styled-dropdown'})
    )

    course_year = forms.CharField(
        label="Year",
        widget=forms.TextInput(attrs={
            'type': 'number',
            'min': '2000',
            'max': '2099',
            'step': '1',
            'placeholder': 'ex. 2025',
            'class': 'styled-dropdown'
        })
    )

    class Meta:
        model = Course
        fields = ['course_number', 'course_name', 'course_semester', 'course_year']
        widgets = {
            'course_number': forms.TextInput(attrs={'placeholder': 'ex. CSCI3356'}),
            'course_name': forms.TextInput(attrs={'placeholder': 'ex. Software Engineering'}),
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['team_name']
        widgets = {
            'team_name': forms.TextInput(attrs={'placeholder': 'ex. Team1'})
        }

