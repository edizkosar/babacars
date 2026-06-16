// BabaCars – main.js

// ─── CSRF helper ───────────────────────────────────────────────
function getCSRF() {
  return document.cookie.split(';').map(c => c.trim())
    .find(c => c.startsWith('csrftoken='))?.split('=')[1] || '';
}

// ─── AJAX helper ───────────────────────────────────────────────
async function apiPost(url, data = {}) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRF(),
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify(data),
  });
  return { ok: res.ok, data: await res.json() };
}

// ─── Toast helper ──────────────────────────────────────────────
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = {
    success: '<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>',
    error:   '<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>',
    info:    '<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
  };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `${icons[type] || icons.info}<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s, transform 0.4s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// ─── Favorite toggle ───────────────────────────────────────────
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-favorite-btn]');
  if (!btn) return;
  const listingId = btn.dataset.listingId;
  btn.disabled = true;
  try {
    const { ok, data } = await apiPost(`/${listingId}/favorite/`, {});
    // URL matches listings:toggle_favorite -> /<listing_id>/favorite/
    if (ok) {
      const icon = btn.querySelector('[data-fav-icon]');
      if (icon) icon.classList.toggle('fill-red-500', data.is_favorited);
      const count = btn.querySelector('[data-fav-count]');
      if (count) count.textContent = data.favorite_count;
      showToast(data.is_favorited ? 'Favorilere eklendi!' : 'Favorilerden çıkarıldı.', 'success');
    } else {
      showToast(data.error || 'Bir hata oluştu.', 'error');
    }
  } catch (err) {
    showToast('Bağlantı hatası.', 'error');
  } finally {
    btn.disabled = false;
  }
});

// ─── Offer AJAX buttons ─────────────────────────────────────────
async function handleOfferAction(url, onSuccess) {
  try {
    const { ok, data } = await apiPost(url);
    if (ok) {
      showToast(data.message, 'success');
      if (onSuccess) onSuccess(data);
    } else {
      showToast(data.error || 'Bir hata oluştu.', 'error');
    }
  } catch (err) {
    showToast('Bağlantı hatası.', 'error');
  }
}

// ─── GSAP animations (when GSAP available) ─────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);

    // Animate cards on scroll
    gsap.utils.toArray('[data-animate="card"]').forEach(el => {
      gsap.from(el, {
        scrollTrigger: { trigger: el, start: 'top 90%' },
        opacity: 0, y: 30, duration: 0.5, ease: 'power2.out',
      });
    });

    // Animate stat numbers
    gsap.utils.toArray('[data-count]').forEach(el => {
      const target = parseInt(el.dataset.count);
      gsap.from({ val: 0 }, {
        scrollTrigger: { trigger: el, start: 'top 85%' },
        val: target, duration: 1.2, ease: 'power1.out',
        onUpdate: function() { el.textContent = Math.round(this.targets()[0].val).toLocaleString('tr-TR'); }
      });
    });
  }

  // Image lazy loading polyfill
  document.querySelectorAll('img[loading="lazy"]').forEach(img => {
    if (!img.complete) img.style.opacity = '0';
    img.addEventListener('load', () => {
      img.style.transition = 'opacity 0.3s';
      img.style.opacity = '1';
    });
  });
});
