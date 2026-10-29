# Notes / Jurnal Tanaman

Fitur Catatan & Jurnal Pribadi pada Tanamin: pengguna mencatat progres dan kejadian penting pada tanamannya (judul, kategori, status, metode tanam, tanggal tanam, lokasi, isi catatan, dan foto).

Penanggung jawab modul: Rebeccaniaga Napitupulu (2506598394)

# Fitur
- Daftar catatan lewat AJAX (tanpa reload), dengan state loading, kosong, dan error.
- Pencarian (judul / nama tanaman / lokasi) dengan debouncing 400 ms dan filter kategori.
- Tambah catatan lewat modal, tambah/edit lewat halaman form, hapus dengan halaman konfirmasi.
- Semua field wajib diisi (termasuk foto). Kalau ada satu saja yang kosong, catatan tidak disimpan dan muncul toast merah: "Gagal menambahkan catatan…" (tambah) atau "Gagal menyimpan catatan…" (edit).
- Foto divalidasi (JPG/PNG, maks. 2 MB, harus gambar asli) lalu diperkecil otomatis (sisi terpanjang 1280 px).
- Perlindungan XSS (strip tag di server + escapeHtml di JS) dan CSRF (X-CSRFToken untuk fetch).
- Catatan bisa ditautkan ke tanaman di "Kebun Saya" lewat ?garden_plant_id= dari Dashboard.
- Catatan hanya bisa dilihat/diubah/dihapus oleh pemiliknya (catatan orang lain → 404).


📅 Progress Mingguan
# Progress Minggu 1
- Membuat model Note (judul, nama tanaman, kategori, status, metode tanam, tanggal tanam, lokasi, isi, foto).
- Membuat NoteForm (ModelForm) dan halaman tambah/edit/hapus dengan template yang meng-extend base_notes.html.
- Menambahkan relasi user ke Note supaya tiap catatan punya pemilik, dan memfilter semua query dengan user=request.user.
# Progress Minggu 2
- Mengubah halaman daftar jadi AJAX: halaman hanya merender kerangka, data diambil lewat fetch() ke api_list (JSON).
- Menambahkan pencarian dengan debouncing, filter kategori, serta tiga kondisi tampilan (loading, kosong, error).
- Menambahkan modal tambah catatan lewat fetch() + FormData ke api_create, lengkap dengan toast sukses/gagal.
- Menambahkan validasi foto + pengecilan foto otomatis, dan perlindungan XSS/CSRF.
- Menautkan catatan ke GardenPlant (Kebun Saya) lewat garden_plant_id.
# Progress Minggu 3
- Memperbaiki bug validasi: __init__ di NoteForm ternyata berada di dalam class Meta, jadi tidak pernah dijalankan dan semua field tetap opsional di sisi server. Saat tambah catatan, kekosongan hanya ketahan oleh validasi JS di modal; saat edit, field kosong lolos dan tersimpan. __init__ dipindah sejajar Meta sehingga semua field wajib di server.
- Menambahkan toast gagal pada halaman tambah/edit (note_form.js + toast_error dari view). Toast muncul dari validasi sisi klien (form tidak dikirim) dan dari validasi sisi server (cadangan kalau JS mati).
- Menyeragamkan teks toast: "Gagal menambahkan catatan…" dan "Gagal menyimpan catatan…".
- Menambahkan n-err dan data-field ke semua field di form.html supaya pesan error tampil di bawah tiap input.
- Menulis 58 unit test (model, form, validasi foto, API, create, edit, delete, hak akses) dengan coverage 98%.

# AI Disclosure : 
Saya menggunakan AI untuk membantu memahami alur perbaikan validasi form, menyiapkan konsep implementasi toast notification, serta menyusun kerangka unit test. AI membantu memberikan gambaran awal tentang bagian kode yang perlu diperbaiki, terutama pada validasi form edit yang sebelumnya masih memungkinkan catatan dengan field kosong untuk disimpan. Setelah itu, saya mencoba menjalankan tes untuk memastikan perbaikannya berjalan sesuai harapan dan menyesuaikan implementasinya dengan struktur proyek yang saya gunakan.Beberapa hal yang saya temukan dan perbaiki sendiri:Saat mencoba fitur toast notification langsung di browser, saya menemukan beberapa pesan yang belum sesuai dengan kondisi yang terjadi, baik saat menambahkan catatan berhasil maupun ketika prosesnya gagal. Saya menyesuaikan kembali pesan-pesan tersebut supaya lebih jelas dan sesuai dengan aksi yang dilakukan pengguna.Selain itu, tampilan modal untuk menambahkan catatan sempat tidak berada di posisi yang saya inginkan. Seharusnya modal berada di tengah layar, tetapi tampilannya justru bergeser ke pinggir. Saya memperbaiki sendiri bagian CSS dan layoutnya sampai posisinya sesuai. Saya juga melakukan beberapa penyesuaian pada styling lain yang masih kurang sesuai dengan tampilan yang saya inginkan.Dalam proses pengujian, saya juga menemukan bahwa kode yang diberikan AI tidak langsung berjalan dengan baik karena belum sepenuhnya sesuai dengan struktur model User di proyek saya. Saya kemudian menyesuaikan bagian pembuatan user untuk kebutuhan tes dan menggunakan konfigurasi password hasher khusus testing agar proses pengujian berjalan lebih cepat. Saya juga menjalankan tes terhadap kode sebelum dan sesudah perbaikan untuk memastikan bug validasi yang ditemukan benar-benar sudah teratasi.Untuk JavaScript, pengujian yang dilakukan masih sebatas pemeriksaan sintaks, sehingga saya tetap perlu mencoba fitur toast, fokus pada field yang kosong, dan perilaku modal secara langsung di browser. Pengujian otomatis yang dilakukan juga masih menggunakan SQLite, sehingga belum mencakup kemungkinan perbedaan perilaku dengan PostgreSQL yang digunakan di lingkungan produksi.
Secara keseluruhan, AI membantu saya memahami alur pengerjaan dan memberikan kerangka awal implementasi, sedangkan penyesuaian pesan, layout, CSS, serta pemeriksaan hasil implementasi tetap saya lakukan sendiri berdasarkan hasil pengujian dan tampilan yang saya inginkan.

Sumber : https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/
https://docs.djangoproject.com/en/5.2/topics/testing/tools/


