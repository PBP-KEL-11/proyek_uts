// notes/static/notes/js/note_form.js
// Halaman Tambah/Edit catatan (form biasa): semua field wajib terisi.
// Kalau ada yang kosong -> form TIDAK dikirim dan muncul toast gagal.
(function () {
  'use strict';

  const form = document.getElementById('note-page-form');
  const wrap = document.getElementById('toast-wrap');
  if (!form || !wrap) return;

  const REQUIRED = {
    plant_name: 'Nama tanaman',
    title: 'Judul catatan',
    category: 'Kategori',
    status: 'Status',
    planting_method: 'Metode tanam',
    planted_date: 'Tanggal tanam',
    location: 'Lokasi tanaman',
    content: 'Isi catatan',
    image: 'Foto tanaman',
  };

  function showToast(message, type) {
    const el = document.createElement('div');
    el.className = 'n-toast ' + (type === 'error' ? 'err' : 'ok');
    el.setAttribute('role', 'status');
    el.textContent = message;
    wrap.appendChild(el);
    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 300);
    }, 4000);
  }

  function isFilled(name, box) {
    if (name === 'category') return !!box.querySelector('input[name="category"]:checked');
    const input = box.querySelector('[name="' + name + '"]');
    if (!input) return false;
    if (input.type === 'file') {
      // Saat edit, foto lama dianggap sudah terisi.
      return input.files.length > 0 || form.dataset.hasImage === '1';
    }
    return input.value.trim() !== '';
  }

  form.addEventListener('submit', (e) => {
    const missing = [];
    let firstInput = null;

    Object.entries(REQUIRED).forEach(([name, label]) => {
      const box = form.querySelector('[data-field="' + name + '"]');
      if (!box) return;
      const err = box.querySelector('.n-err');
      if (err) err.textContent = '';
      if (!isFilled(name, box)) {
        if (err) err.textContent = label + ' wajib diisi.';
        missing.push(label);
        if (!firstInput) firstInput = box.querySelector('input, select, textarea');
      }
    });

    if (missing.length) {
      e.preventDefault();
      showToast('Gagal ' + form.dataset.actionLabel + '. Lengkapi: ' + missing.join(', ') + '.', 'error');
      if (firstInput) firstInput.focus();
    }
  });

  // Toast dari server (validasi sisi server gagal / JS dimatikan).
  const serverToast = document.getElementById('server-toast');
  if (serverToast) showToast(JSON.parse(serverToast.textContent), 'error');
})();