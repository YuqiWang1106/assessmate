from django import forms
from .models import Course, User
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
    class Meta:
        model = Course
        fields = ['course_number', 'course_name', 'course_semester', 'course_year']
        # Adding placeholder attributes to the form fields
        widgets = {
            'course_number': forms.TextInput(attrs={'placeholder': 'ex. CSCI3356'}),
            'course_name': forms.TextInput(attrs={'placeholder': 'ex. Software Engineering'}),
            'course_semester': forms.TextInput(attrs={'placeholder': 'ex. Fall'}),
            'course_year': forms.TextInput(attrs={'placeholder': 'ex. 2025'})

        }
