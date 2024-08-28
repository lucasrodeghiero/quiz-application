from django import forms
from django.contrib.auth.models import User
from . import models

class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = ['address', 'mobile', 'profile_pic']
        widgets = {
            'profile_pic': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Profile Picture',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['profile_pic'].widget.clear_checkbox_label = None
        self.fields['profile_pic'].widget.initial_text = None
        self.fields['profile_pic'].widget.template_name = 'django/forms/widgets/input.html'
