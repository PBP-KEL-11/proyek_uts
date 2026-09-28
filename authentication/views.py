import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .forms import RegisterForm, EditProfileForm

# Create your views here.

def register(request):

    if request.user.is_authenticated:
        return redirect('main:show_main')
    
    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Akun berhasil dibuat. Silakan login.')
        return redirect('authentication:login_user')

    context = {
        "form": form,
    }
    return render(request, 'authentication/register.html', context)


def login_user(request):
    if request.user.is_authenticated:
        return redirect('main:show_main')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(request, 'Login berhasil!')


            response = redirect('main:show_main')
            response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            return response
        
    else:
        form = AuthenticationForm(request)

    context = {
        'form': form
    }

    return render(request, 'authentication/login.html', context)


@login_required(login_url='authentication:login_user')
def profile(request):
    return render(request, 'authentication/profile.html')


@login_required(login_url='authentication:login_user')
def edit_profile(request):

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui!')

            return redirect('authentication:profile')

    else:
        form = EditProfileForm(instance=request.user)

    context = {
        'form': form,
    }

    return render(request, 'authentication/edit_profile.html', context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")    #  menghapus cookie last_login menggunakan method delete_cookie()
                                            #  agar informasi di browser klien tetap sinkron dan bersih
    return response