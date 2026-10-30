// notes/static/notes/js/notes.js
// AJAX untuk modul Notes: daftar, pencarian (debounce), tambah lewat modal, toast.
(function () {
  'use strict';

  const cfg = document.getElementById('notes-config').dataset;
  const grid = document.getElementById('notes-grid');
  const stateBox = document.getElementById('notes-state');
  const searchInput = document.getElementById('q');
  const chips = document.getElementById('chips');
  const modal = document.getElementById('note-modal');
  const form = document.getElementById('note-form');
  const submitBtn = document.getElementById('submit-btn');

  let currentCategory = '';
  let controller = null;   // untuk membatalkan permintaan lama (AbortController)

  // ---------- Perlindungan XSS: semua teks dari pengguna lewat escapeHtml ----------
  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // ---------- Toast ----------
    // ---------- Toast ----------
  function showToast(message, type) {
    const modalWrap = document.getElementById('modal-toast-wrap');
    const globalWrap = document.getElementById('toast-wrap');
    const wrap = modal.open && modalWrap ? modalWrap : globalWrap;

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

  // ---------- Tiga kondisi: loading, kosong, error ----------
  function showLoading() {
    stateBox.innerHTML = '';
    grid.innerHTML = Array.from({ length: 6 }, () =>
      '<div class="n-card n-skel" aria-hidden="true">' +
        '<div class="n-photo"></div>' +
        '<div class="n-body"><div class="n-skel-line w60"></div>' +
        '<div class="n-skel-line w40"></div><div class="n-skel-line"></div></div>' +
      '</div>'
    ).join('');
    stateBox.innerHTML = '<span class="sr-only">Memuat catatan...</span>';
  }

  function showEmpty() {
    grid.innerHTML = '';
    const searching = searchInput.value.trim() || currentCategory;
    stateBox.innerHTML = searching
      ? '<div class="n-empty">Tidak ada catatan yang cocok dengan pencarianmu.</div>'
      : '<div class="n-empty">Belum ada catatan. Klik <b>Tambah Catatan</b> untuk mulai menulis jurnal tanamanmu.</div>';
  }

  function showError(message) {
    grid.innerHTML = '';
    stateBox.innerHTML =
      '<div class="n-empty n-error"><p>' + escapeHtml(message) + '</p>' +
      '<button type="button" class="n-btn p" id="retry-btn">Coba lagi</button></div>';
    document.getElementById('retry-btn').addEventListener('click', loadNotes);
  }

  // ---------- Render kartu (semua teks pengguna di-escape) ----------
  function cardHtml(n) {
    const photo = n.image_url
      ? '<img src="' + escapeHtml(n.image_url) + '" alt="Foto ' + escapeHtml(n.plant_name) + '">'
      : '';
    const loc = n.location ? '<span class="n-pill n-loc">' + escapeHtml(n.location) + '</span>' : '';
    const content = n.content
      ? '<p>' + escapeHtml(n.content.length > 110 ? n.content.slice(0, 107) + '...' : n.content) + '</p>'
      : '';
    return (
      '<div class="n-card" data-id="' + n.id + '">' +
        '<div class="n-photo">' + photo + loc +
          '<span class="n-pill n-status st-' + escapeHtml(n.status) + '">' + escapeHtml(n.status_label) + '</span>' +
        '</div>' +
        '<div class="n-body">' +
          '<h3>' + escapeHtml(n.title) + '</h3>' +
          '<div class="n-meta">' + escapeHtml(n.plant_name) + ' &middot; ' + escapeHtml(n.category_label) + '</div>' +
          content +
          '<div class="n-foot">' +
            '<div><b>Tanam: ' + escapeHtml(n.planted_date) + '</b><br>' + escapeHtml(n.planting_method_label) + '</div>' +
            '<div class="n-act">' +
              '<a href="' + escapeHtml(n.edit_url) + '" class="n-ib" style="background:#4F7A55" aria-label="Edit catatan">&#9998;</a>' +
              '<a href="' + escapeHtml(n.delete_url) + '" class="n-ib" style="background:#C62828" aria-label="Hapus catatan">&#10005;</a>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }

  // ---------- Ambil data (daftar + pencarian + kategori) ----------
  async function loadNotes() {
    if (controller) controller.abort();     // batalkan permintaan sebelumnya
    controller = new AbortController();

    const params = new URLSearchParams();
    const q = searchInput.value.trim();
    if (q) params.set('q', q);
    if (currentCategory) params.set('category', currentCategory);

    showLoading();
    try {
      const res = await fetch(cfg.listUrl + (params.toString() ? '?' + params : ''), {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        signal: controller.signal,
      });
      if (res.status === 403) {
        showError('Sesi kamu berakhir. Silakan login lagi.');
        return;
      }
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();

      stateBox.innerHTML = '';
      if (!data.notes.length) {
        showEmpty();
        return;
      }
      grid.innerHTML = data.notes.map(cardHtml).join('');
    } catch (err) {
      if (err.name === 'AbortError') return;   // diganti permintaan baru, abaikan
      showError('Gagal memuat catatan. Periksa koneksi lalu coba lagi.');
    }
  }

  // ---------- Pencarian dengan debouncing (400 ms) ----------
  let timer;
  searchInput.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(loadNotes, 400);
  });

  chips.addEventListener('click', (e) => {
    const chip = e.target.closest('.n-chip');
    if (!chip) return;
    currentCategory = chip.dataset.category;
    chips.querySelectorAll('.n-chip').forEach((c) => c.classList.toggle('on', c === chip));
    loadNotes();
  });

  // ---------- Modal ----------
  function clearErrors() {
    form.querySelectorAll('.n-err').forEach((s) => (s.textContent = ''));
  }
    // ---------- Validasi semua field wajib diisi ----------
  function validateRequiredFields() {
    clearErrors();

    const requiredFields = {
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

    const missingFields = [];
    let firstInvalid = null;

    Object.entries(requiredFields).forEach(([name, label]) => {
      const fieldBox = form.querySelector(`[data-field="${name}"]`);
      const errorBox = fieldBox.querySelector('.n-err');

      let input;
      let isFilled = false;

      if (name === 'category') {
        input = fieldBox.querySelector('input[name="category"]');
        isFilled = !!fieldBox.querySelector('input[name="category"]:checked');
      } else {
        input = fieldBox.querySelector(`[name="${name}"]`);

        if (input && input.type === 'file') {
          isFilled = input.files.length > 0;
        } else if (input) {
          isFilled = input.value.trim() !== '';
        }
      }

      if (!isFilled) {
        errorBox.textContent = label + ' wajib diisi.';
        missingFields.push(label);

        if (!firstInvalid) {
          firstInvalid = input;
        }
      }
    });

    if (missingFields.length > 0) {
      showToast(
        'Gagal menambahkan catatan. Lengkapi: ' + missingFields.join(', ') + '.',
        'error'
      );

      if (firstInvalid) {
        firstInvalid.focus();
      }

      return false;
    }

    return true;
  }

  function openModal() {
    clearErrors();
    modal.showModal();
  }
  function closeModal() {
    modal.close();
  }
  document.getElementById('open-modal').addEventListener('click', openModal);
  document.getElementById('close-modal').addEventListener('click', closeModal);
  document.getElementById('cancel-modal').addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); }); // klik latar

  // ---------- Kirim form lewat fetch + FormData ----------
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateRequiredFields()) return;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Menyimpan...';

    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    try {
      const res = await fetch(cfg.addUrl, {
        method: 'POST',
        // JANGAN set Content-Type: browser mengaturnya sendiri untuk FormData (beserta boundary)
        headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(form),
      });

      let data = {};
      try { data = await res.json(); } catch (_) { /* bukan JSON */ }

      if (res.status === 201) {
        closeModal();
        form.reset();
        showToast(data.message || 'Catatan berhasil ditambahkan.', 'success');
        addCardToTop(data.note);
      } else if (res.status === 400) {
        // tampilkan error per field + ringkasan di toast
        const messages = [];
        Object.entries(data.errors || {}).forEach(([field, errs]) => {
          const box = form.querySelector('[data-field="' + field + '"] .n-err');
          if (box) box.textContent = errs.join(' ');
          messages.push(errs.join(' '));
        });
        showToast('Gagal menambahkan catatan. ' + (messages[0] || ''), 'error');
      } else if (res.status === 403) {
        showToast(data.message || 'Silakan login terlebih dahulu.', 'error');
      } else {
        showToast('Terjadi kesalahan pada server. Coba lagi nanti.', 'error');
      }
    } catch (err) {
      showToast('Tidak bisa terhubung ke server.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Simpan Catatan';
    }
  });

  // ---------- Perbarui daftar tanpa reload ----------
  function addCardToTop(note) {
    // Kalau sedang menampilkan filter/pencarian, muat ulang saja supaya hasilnya konsisten
    if (searchInput.value.trim() || currentCategory) {
      loadNotes();
      return;
    }
    stateBox.innerHTML = '';                       // hilangkan pesan "kosong" bila ada
    grid.insertAdjacentHTML('afterbegin', cardHtml(note));
  }

  loadNotes();
})();