# User Authentication


## 1. Overview

Modul ini menjadi gerbang pertama bagi user untuk bisa menggunakan fitur utama yang ada pada Tanamin. Pengguna diarahkan untuk mendaftar akun (Register). Apabila sudah memiliki akun, pengguna dapat langsung masuk ke halaman Login. Jika lupa password, akan diarahkan ke halaman Forgot Password untuk mengisi alamat email agar email resmi Tanamin dapat mengirimkan pesan email ke alamat email yang bersangkutan. Pesan email berisi tautan yang mengarahkan pengguna ke halaman Create New Password. Setelah berhasil, pengguna bisa kembali login dengan password yang terbaru. 

Jika ingin keluar dari Tanamin, pengguna bisa memencet tombol Logout untuk keluar akun.


## 2. Features

- User Registration
- Login
- Logout
- Reset Password


## 3. Technology Stack

- Python: Backend programming language.
- Django: Web application framework.
- HTML: Page structure and templates.
- CSS: User interface styling.
- Database: SQLite during local development
- Deployment platform: PWS (Pacil Web Service)


## 4. Project Structure


    authentication/
    ├── migrations/
    ├── static/
    │   └── authentication/
    │       └── css/
    │           └── style.css
    ├── templates/
    │   └── authentication/
    │       ├── _form_fields.html
    │       ├── base_authentication.html
    │       ├── base_profile.html
    │       ├── edit_profile.html
    │       ├── login.html
    │       ├── password_reset_complete.html
    │       ├── password_reset_confirm.html
    │       ├── password_reset_done.html
    │       ├── password_reset_email.html
    │       ├── password_reset_form.html
    │       ├── password_reset_subject.txt
    │       ├── profile.html
    │       └── register.html
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── README.md
    ├── test.py
    ├── urls.py
    └── views.py


## AI Disclosure

Pengerjaan Modul Authentication ini dibantu oleh Claude.
Pertanyaan yang diajukan seputar bagaimana cara agar pengguna bisa menggunggah foto profil di akun Tanamin. Apakah ada *dependecies* yang perlu di install dan sebagainya. Claude menjelaskan langkah

Kemudian mengenai bagaimana cara menyelesaikan konflik ketika merge di github. Juga menanyakan apakah sebaiknya base.html dipecah menjadi header.html dan footer.html agar file base.html tidak terlalu kompleks.