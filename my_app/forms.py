from django import forms

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