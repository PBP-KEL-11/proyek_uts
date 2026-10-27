import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

from .forms import RegisterForm, EditProfileForm

# Create your views here.

def register(request):
    if request.user.is_authenticated:
        return redirect('main:show_main')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Akun berhasil dibuat. Selamat datang!')

            response = JsonResponse({
                'status': 'success',
                'message': 'Registration successful',
                'redirect_url': reverse('main:show_main'),
            })
            response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return response

        return JsonResponse(
            {'status': 'error', 'errors': form.errors.get_json_data()},
            status=400,
        )

    form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('main:show_main')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Login berhasil!')

            response = JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'redirect_url': reverse('main:show_main'),
            })
            response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return response

        return JsonResponse(
            {'status': 'error', 'errors': form.errors.get_json_data()},
            status=400,
        )

    form = AuthenticationForm(request)
    return render(request, 'authentication/login.html', {'form': form})


@login_required(login_url='authentication:login_user')
def profile(request):
    return render(request, 'authentication/profile.html')


@login_required(login_url='authentication:login_user')
def edit_profile(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            profile_url = reverse('authentication:profile')

            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profil berhasil diperbarui',
                    'redirect_url': profile_url,
                })
            return redirect(profile_url)

        if is_ajax:
            return JsonResponse(
                {'status': 'error', 'errors': form.errors.get_json_data()},
                status=400,
            )
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'authentication/edit_profile.html', {'form': form})


def logout_user(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logout(request)

    if is_ajax:
        response = JsonResponse({
            'status': 'success',
            'message': 'Logout berhasil',
            'redirect_url': reverse('main:show_main'),
        })
    else:
        response = redirect('main:show_main')

    response.delete_cookie('last_login')
    return response