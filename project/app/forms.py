from django import forms

from .models import Student, Course

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'