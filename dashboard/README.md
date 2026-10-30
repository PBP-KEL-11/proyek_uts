### User Authentication
1. Overview
Modul ini merupakan bagian yang menampilkan permainan Green Track yang pengguna dapat mendaftarkan diri. Green Track merupakan gamifikasi dari rutinitas pengguna dalam mengurus tanaman mereka . Pengguna dapat mengaksesnya melalui pilihan "Dashboard" yang tersedia pada Navigation Bar.

Pengguna yang belum mendaftarkan diri ke Green Track akan dialihkan ke laman untuk mendaftarkan diri, sedangkan pengguna yang sudah mendaftarkan diri akan langsung dialihkan ke laman yang menampilkan detail Green Track mereka. Green Track memiliki atribut level, xp, dan badge yang akan meningkat setiap kali pengguna menyelesaikan sebuah tugas rutin. Pengguna juga dapat membuat nickname mereka sendiri untuk Green Track beserta deskripsi mereka terkait alasan ingin mendaftarkan diri ke Green Track. Pengguna juga dapat menghapus atau mengupdate Green Track mereka.

Untuk pengguna yang merupakan admin, maka ketika memasuki laman Dashboard, maka akan melalui proses yang sama sebagaimana pengguna biasa, tetapi akan mendapati Navigation Bar nya memiliki dua opsi baru, yakni Pengguna Green Track dan Tanaman Pengguna Tanamin. Dengan kedua opsi tersebut, admin dapat memantau daftar pengguna yang sudah mendaftar Green Track dan tanaman-tanaman yang dipilih oleh pengguna beserta detail mereka. Admin tidak dapat mengubah atau menghapus pengguna ataupun Green Track mereka.

2. Features
- Green Track Registration
- Green Track Update
- Green Track Delete
- Green Track Dashboard
- Green Track Users List(Admin Only)
- Green Track User's detail(Admin Only)
- Users' Plants List(Admin Only)
- User's Plants detail(Admin Only)

3. Technology Stack
- Python: Backend programming language.
- Django: Web application framework.
- Javascript: Frontend programming language.
- HTML: Page structure and templates.
- CSS: User interface styling.
- Database: SQLite during local development
- Deployment platform: PWS (Pacil Web Service).

4. Project Structure

dashboard/
├── migrations/
├── static/
│   └── css/
│   │    └── style.css
│   └── img/
│        └── background-image.jpeg
├── templates/
│   └── dashboard/
│       ├── admin_greentrack_dashboard.html
│       ├── admin_greentrack_detail.html
│       ├── admin_user_dashboard.html
│       ├── admin_user_detail.html
│       ├── base_dashboard.html
│       ├── create_greentrack.html
│       ├── greentrack_detail.html
│       └── update_greentrack.html
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── README.md
├── tests.py
├── urls.py
└── views.py

### AI Disclosure
Dalam pengerjaan modul dashboard ini saya tidak menggunakan AI apapun. Sumber utama saya adalah website W3School, GeeksForGeeks, dan dokumentasi Django. Adapun untuk menyelesaikan masalah yang spesifik, maka saya selalu mencari solusi menggunakan website StackOverflow atau website-website forum internet lainnya yang serupa.