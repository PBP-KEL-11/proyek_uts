from django.forms import ModelForm
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import SplitPhoneNumberField

class RegisterForm(UserCreationForm):

    full_name = forms.CharField(
        label='Full Name',
        max_length=150
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'full_name',
            'password1',
            'password2',
        ]

        labels = {
            'email': 'Email Address',
        }

        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        full_name = self.cleaned_data['full_name'].strip()
        name_parts = full_name.split(' ', 1)

        user.first_name = name_parts[0]

        if len(name_parts) > 1:
            user.last_name = name_parts[1]
        else:
            user.last_name = ''

        if commit:
            user.save()

        return user

class EditProfileForm(ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
        ]

        labels = {
            'email': 'Email Address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
        }