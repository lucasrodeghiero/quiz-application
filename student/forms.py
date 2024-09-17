from django import forms
from django.contrib.auth.models import User
from . import models

class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if self.instance.pk:
            # For update: exclude the current user's username from the uniqueness check
            if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("Username is already taken. Please choose another one.")
        else:
            # For sign-up: check if the username is already taken
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Username is already taken. Please choose another one.")
        
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if self.instance.pk:
            # For update: exclude the current user's email from the uniqueness check
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("Email is already associated with another account.")
        else:
            # For sign-up: check if the email is already taken
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Email is already associated with another account.")
        
        return email

class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = ['mobile', 'email']
