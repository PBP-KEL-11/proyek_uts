# Main Page


## 1. Overview

Halaman Main menjadi halaman pertama yang tampil saat pengguna membuka website Tanamin. Berbagai informasi mengenai fungsionalitas website Tanamin secara garis besar, fitur-fitur yang ada di dalamnya, serta panduan untuk memulai semua terangkum dalam halaman ini. Jika pengguna sudah login, maka tampilan header di halaman main akan lengkap terdiri dari Home, Journal, Schedule, Plants, dan Dashboard. Sedangkan jika pengguna belum login, header hanya akan menampilkan tombol Login dan Register.


## 2. Technology Stack

- Python: Backend programming language.
- Django: Web application framework.
- HTML: Page structure and templates.
- CSS: User interface styling.
- Database: SQLite during local development
- Deployment platform: PWS (Pacil Web Service)


## 3. Project Structure


    main/
    ├── migrations/
    ├── static/
    │   ├── css/
    │   │   └── main/
    │   │       └── style.css
    │   ├── img/
    │   │   └── main/
    │   └── js/
    │       └── main/
    │           └── toast.js
    ├── templates/
    │   └── main/
    │       ├── includes/
    │       │   ├── footer.html
    │       │   ├── header.html
    │       │   └── toast.html
    │       ├── base.html
    │       └── index.html
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── README.md
    ├── tests.py
    ├── urls.py
    └── views.py


## AI Disclosure

Pengerjaan Halaman Utama website ini dibantu oleh Claude.

Terdapat kesulitan pada saat mengimplementasikan notifikasi toast, khususnya pada bagian styling CSS. Toast yang muncul (notifikasi Login Berhasil dan Logout Berhasil) setelah login dan logout sudah terimplementasi dengan benar. Namun, untuk toast yang muncul setelah pengguna memencet tombol 'Simpan' di halaman Edit Profil, tampilannya hanya tulisan hitam dengan background berwarna putih, tidak sama dengan tampilan notifikasi toast yang muncul setelah pengguna login atau logout.

Beberapa rekomendasi yang diberikan AI tidak kunjung menyelesaikan solusi. Mungkin ada kesalahan dari saya pribadi yang tidak sengaja melewatkan suatu langkah yang disarankan. Akhirnya, saya memutuskan untuk menaruh style CSS di dalam file toast.html itu sendiri.