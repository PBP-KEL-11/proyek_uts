from django.forms import ModelForm
from .models import User
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import SplitPhoneNumberField

class RegisterForm(UserCreationForm):

    phone = SplitPhoneNumberField(region='ID')

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'phone',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]

        labels = {
            'email': 'Email Address',
            'phone': 'Phone Number',
        }

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