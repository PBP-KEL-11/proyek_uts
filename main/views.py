from django.shortcuts import render

# Create your views here.

def landing_page(request):
    return render(request, 'main/index.html')

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        'last_login': last_login,
    }
    return render(request, 'main/index.html', context)
