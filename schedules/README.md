### Schedules (Daily Tasks)
1. Overview
Modul ini merupakan bagian yang menampilkan tugas perawatan harian (Daily Tasks) dan riwayat perawatan (Plant Care Log) milik pengguna. Pengguna dapat mengaksesnya melalui pilihan "Schedule" yang tersedia pada Navigation Bar. Halaman ini hanya dapat diakses oleh pengguna yang sudah login.

Daftar tanaman yang dipakai modul ini diambil dari catatan pengguna pada modul Notes (Jurnal). Setiap catatan yang statusnya belum "Done" dihitung sebagai satu tanaman. Dari tanaman-tanaman tersebut, sistem memilih maksimal 3 tanaman berbeda untuk setiap harinya, dan tiap tanaman memiliki 4 tugas perawatan: Siram Air, Beri Pupuk, Ganti Pot, dan Cek Hama (maksimal 3 x 4 = 12 tugas per hari). Pemilihan tanaman bersifat acak tetapi tetap sama sepanjang hari yang sama, lalu berganti di hari berikutnya. Jika pengguna baru menambahkan tanaman di tengah hari, slot yang masih kosong akan langsung terisi tanpa menghapus tugas yang sudah ada.

Jika pengguna belum memiliki catatan tanaman sama sekali, halaman akan menampilkan tugas "Tambahkan 1 tanaman ke Jurnal" beserta tombol menuju form tambah catatan. Setiap tanaman ditampilkan sebagai satu kartu misi dengan progress bar. Tombol "Details" membuka pop-up berisi keempat tugas, dan pengguna dapat menekan "Tandai Selesai" pada masing-masing tugas. Setiap tugas yang diselesaikan menambah XP pada Green Track pengguna (modul Dashboard) dan tercatat pada Plant Care Log.

Selain itu, halaman menampilkan pesan apresiasi ketika semua tugas hari itu selesai, pengingat pada pukul 18.00 (waktu Asia/Jakarta) jika masih ada tugas yang belum selesai, serta pesan peringatan jika pengguna melewatkan tugas pada hari-hari sebelumnya.

2. Features
- Daily Tasks (maksimal 3 tanaman x 4 tugas per hari, dibuat otomatis saat halaman dibuka)
- Task Completion ("Tandai Selesai" dan penambahan XP Green Track)
- Mission Progress & Details Pop-up per tanaman
- Prompt "Tambahkan 1 tanaman ke Jurnal" jika pengguna belum memiliki tanaman
- Plant Care Log (10 log terbaru) dengan tombol "Expand More" untuk memuat 20 log berikutnya tanpa reload halaman (AJAX)
- Pesan apresiasi ketika semua tugas hari ini selesai
- Pengingat pukul 18.00 jika masih ada tugas yang belum selesai
- Pesan peringatan untuk hari-hari yang terlewat (missed days)
- Auto refresh halaman saat pergantian hari
- Management command generate_daily_tasks untuk membuat tugas semua pengguna (opsional, dapat dijadwalkan dengan cron)


3. Project Structure

schedules/
├── management/
│   └── commands/
│       ├── __init__.py
│       └── generate_daily_tasks.py
├── migrations/
├── static/
│   └── css/
│       └── schedules/
│           └── style.css
├── templates/
│   └── schedules/
│       ├── _log_rows.html
│       ├── base_schedules.html
│       └── dashboard.html
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── README.md
├── services.py
├── tests.py
├── urls.py
└── views.py

## AI Disclosure
Dalam pengerjaan modul schedules ini, saya menggunakan Artificial Intelligence:
- Claude Sonnet 5.5 Medium:
Saya menggunakan AI ini untuk styling CSS modern dan hal yang advance seperti mengurangi display care log (Menjadi 10 terbaru) dan fitur "Expand More" (menambah 20 log yang sudah lampau), ataupun generate daily tasks setiap harinya secara otomatis.
- Gemini Flash 3.6 High:
Saya menggunakan AI ini hanya sebagai penjelasan/alur lebih lanjut dari hasil yang sudah dibuat oleh Claude Sonnet 5.5 Medium (Hemat token), terutama library baru seperti urlencode yang digunakan dalam menyelesaikan tugas. 

Penjelasan materi lainnya selain dari Gemini Flash 3.6 High diambil dari GeeksForGeeks dan W3School. Selebihnya pengerjaan seperti dashboard.html, _log_rows.html, moduls.py, urls.py, services.py (kecuali function generate_daily_tasks) murni dibuat oleh saya sendiri.