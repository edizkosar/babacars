// ════════════════════════════════════════════════════════════════
// BabaCars – effects.js
// Dinamik mikro-etkileşimler. main.js'ten bağımsız çalışır.
// ════════════════════════════════════════════════════════════════
(function () {
  'use strict';

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ─── 1. Buton ripple ──────────────────────────────────────────
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn, [data-ripple]');
    if (!btn || reduceMotion) return;
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const circle = document.createElement('span');
    circle.className = 'ripple-circle';
    circle.style.width = circle.style.height = size + 'px';
    circle.style.left = (e.clientX - rect.left - size / 2) + 'px';
    circle.style.top = (e.clientY - rect.top - size / 2) + 'px';
    btn.appendChild(circle);
    setTimeout(() => circle.remove(), 600);
  });

  // ─── 2. 3D tilt (kartlar) ─────────────────────────────────────
  function initTilt() {
    if (reduceMotion) return;
    document.querySelectorAll('[data-animate="card"]').forEach((card) => {
      if (card.dataset.tiltInit) return;
      card.dataset.tiltInit = '1';
      card.setAttribute('data-tilt', '');
      const MAX = 6; // derece
      card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width;
        const py = (e.clientY - r.top) / r.height;
        const rx = (py - 0.5) * -2 * MAX;
        const ry = (px - 0.5) * 2 * MAX;
        card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg)`;
        card.classList.add('tilt-active');
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
        card.classList.remove('tilt-active');
      });
    });
  }

  // ─── 3. Favori kalp pop + parçacık ────────────────────────────
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-favorite-btn]');
    if (!btn) return;
    const icon = btn.querySelector('[data-fav-icon]');
    if (icon && !reduceMotion) {
      icon.classList.remove('heart-pop');
      void icon.offsetWidth; // reflow → animasyonu tekrar tetikle
      icon.classList.add('heart-pop');
      spawnParticles(btn);
    }
  });

  function spawnParticles(anchor) {
    const rect = anchor.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    for (let i = 0; i < 6; i++) {
      const p = document.createElement('span');
      p.className = 'fav-particle';
      p.style.left = cx + 'px';
      p.style.top = cy + 'px';
      p.style.position = 'fixed';
      document.body.appendChild(p);
      const angle = (Math.PI * 2 * i) / 6;
      const dist = 22 + Math.random() * 14;
      p.animate(
        [
          { transform: 'translate(-50%,-50%) scale(1)', opacity: 1 },
          {
            transform: `translate(calc(-50% + ${Math.cos(angle) * dist}px), calc(-50% + ${Math.sin(angle) * dist}px)) scale(0)`,
            opacity: 0,
          },
        ],
        { duration: 550, easing: 'cubic-bezier(0.22,1,0.36,1)' }
      );
      setTimeout(() => p.remove(), 560);
    }
  }

  // ─── 4. Yukarı çık butonu ─────────────────────────────────────
  function initBackToTop() {
    if (document.getElementById('back-to-top')) return;
    const btn = document.createElement('button');
    btn.id = 'back-to-top';
    btn.title = 'Yukarı çık';
    btn.setAttribute('aria-label', 'Yukarı çık');
    btn.innerHTML = '<svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 15l7-7 7 7"/></svg>';
    document.body.appendChild(btn);
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    window.addEventListener('scroll', () => {
      btn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });
  }

  // ─── 5. Scroll reveal ─────────────────────────────────────────
  function initReveal() {
    const els = document.querySelectorAll('[data-reveal]');
    if (!els.length) return;
    if (reduceMotion || !('IntersectionObserver' in window)) {
      els.forEach((el) => el.classList.add('revealed'));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    els.forEach((el) => io.observe(el));
  }

  // ─── 6. Detay sayfası zoom-lens ───────────────────────────────
  function initZoomLens() {
    const main = document.getElementById('main-photo');
    if (!main || reduceMotion) return;
    const wrap = main.parentElement;
    wrap.classList.add('zoom-lens-wrap');
    wrap.addEventListener('mousemove', (e) => {
      const r = wrap.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width) * 100;
      const y = ((e.clientY - r.top) / r.height) * 100;
      main.style.transformOrigin = `${x}% ${y}%`;
    });
    wrap.addEventListener('mouseenter', () => wrap.classList.add('zooming'));
    wrap.addEventListener('mouseleave', () => wrap.classList.remove('zooming'));
  }

  // ─── 7. Hızlı bakış (quick-view) modal ────────────────────────
  function buildQuickViewOverlay() {
    if (document.getElementById('quickview-overlay')) return;
    const ov = document.createElement('div');
    ov.id = 'quickview-overlay';
    ov.innerHTML = '<div id="quickview-card"></div>';
    document.body.appendChild(ov);
    ov.addEventListener('click', (e) => {
      if (e.target === ov || e.target.closest('.quickview-btn')) closeQuickView();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeQuickView();
    });
  }

  function openQuickView(data) {
    buildQuickViewOverlay();
    const ov = document.getElementById('quickview-overlay');
    const card = document.getElementById('quickview-card');
    const badge = data.type === 'rental'
      ? '<span style="background:#7c3aed;color:#fff;font-size:.65rem;font-weight:700;padding:.25rem .6rem;border-radius:999px;">KİRALIK</span>'
      : '<span style="background:#2563eb;color:#fff;font-size:.65rem;font-weight:700;padding:.25rem .6rem;border-radius:999px;">SATILIK</span>';
    const img = data.img
      ? `<img src="${data.img}" alt="" style="width:100%;height:240px;object-fit:cover;">`
      : `<div style="width:100%;height:240px;background:#f1f5f9;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:.8rem;">Görsel yok</div>`;
    card.innerHTML = `
      <div style="position:relative;">
        <button class="quickview-btn" aria-label="Kapat">✕</button>
        ${img}
      </div>
      <div style="padding:1.25rem;">
        <div style="display:flex;gap:.5rem;margin-bottom:.6rem;">${badge}</div>
        <h3 style="font-size:1.15rem;font-weight:800;color:#111;margin:0 0 .4rem;line-height:1.3;">${data.title}</h3>
        <p style="font-size:.8rem;color:#6b7280;margin:0 0 .9rem;">${data.specs || ''}</p>
        <div style="display:flex;align-items:center;justify-content:space-between;">
          <span style="font-size:1.5rem;font-weight:900;color:#C9A84C;">${data.price}</span>
          <a href="${data.url}" style="background:#111;color:#FAF7F2;font-weight:700;font-size:.8rem;padding:.6rem 1.25rem;border-radius:8px;text-decoration:none;">Detayları Gör →</a>
        </div>
      </div>`;
    requestAnimationFrame(() => ov.classList.add('open'));
  }

  function closeQuickView() {
    const ov = document.getElementById('quickview-overlay');
    if (ov) ov.classList.remove('open');
  }

  document.addEventListener('click', function (e) {
    const trigger = e.target.closest('.quickview-trigger');
    if (!trigger) return;
    e.preventDefault();
    e.stopPropagation();
    openQuickView({
      title: trigger.dataset.title,
      price: trigger.dataset.price,
      specs: trigger.dataset.specs,
      img: trigger.dataset.img,
      url: trigger.dataset.url,
      type: trigger.dataset.type,
    });
  });

  // ════════════════════════════════════════════════════════════
  //  PREMIUM EK PAKET
  // ════════════════════════════════════════════════════════════

  // ─── 9. Scroll ilerleme çubuğu ────────────────────────────────
  function initScrollProgress() {
    const bar = document.createElement('div');
    bar.id = 'scroll-progress';
    document.body.appendChild(bar);
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const h = document.documentElement.scrollHeight - window.innerHeight;
        const p = h > 0 ? (window.scrollY / h) * 100 : 0;
        bar.style.width = p + '%';
        ticking = false;
      });
    }, { passive: true });
  }

  // ─── 10. Header shrink ────────────────────────────────────────
  function initHeaderShrink() {
    const header = document.querySelector('header');
    if (!header) return;
    window.addEventListener('scroll', () => {
      header.classList.toggle('shrink', window.scrollY > 30);
    }, { passive: true });
  }

  // ─── 11. İmleç ışıltısı ───────────────────────────────────────
  function initCursorGlow() {
    if (reduceMotion || window.matchMedia('(hover: none)').matches) return;
    const glow = document.createElement('div');
    glow.id = 'cursor-glow';
    document.body.appendChild(glow);
    let tx = 0, ty = 0, cx = 0, cy = 0;
    document.addEventListener('mousemove', (e) => {
      tx = e.clientX; ty = e.clientY;
      glow.style.opacity = '1';
    });
    document.addEventListener('mouseleave', () => { glow.style.opacity = '0'; });
    (function loop() {
      cx += (tx - cx) * 0.15;
      cy += (ty - cy) * 0.15;
      glow.style.transform = `translate(${cx}px, ${cy}px) translate(-50%,-50%)`;
      requestAnimationFrame(loop);
    })();
  }

  // ─── 12. Kart spotlight ───────────────────────────────────────
  function initSpotlight() {
    document.addEventListener('mousemove', (e) => {
      const card = e.target.closest('[data-animate="card"]');
      if (!card) return;
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      card.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }

  // ─── 13. Magnetic butonlar ────────────────────────────────────
  function initMagnetic() {
    if (reduceMotion) return;
    const targets = document.querySelectorAll('[data-magnetic], .btn-gold');
    targets.forEach((el) => {
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const x = e.clientX - r.left - r.width / 2;
        const y = e.clientY - r.top - r.height / 2;
        el.style.transform = `translate(${x * 0.25}px, ${y * 0.35}px)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });
  }

  // ─── 14. Gradient başlık (hero altın kelime) ──────────────────
  function initGradientTitle() {
    document.querySelectorAll('.hero-word.text-gold').forEach((el) => {
      el.classList.add('gradient-flow');
    });
  }

  // ─── 15. Hero parçacık canvas ─────────────────────────────────
  function initParticles() {
    if (reduceMotion) return;
    document.querySelectorAll('.hero-dark').forEach((hero) => {
      if (hero.querySelector('.hero-particles')) return;
      const canvas = document.createElement('canvas');
      canvas.className = 'hero-particles';
      hero.prepend(canvas);
      const ctx = canvas.getContext('2d');
      let particles = [];
      let w, h;

      function resize() {
        w = canvas.width = hero.offsetWidth;
        h = canvas.height = hero.offsetHeight;
        const count = Math.min(60, Math.floor((w * h) / 18000));
        particles = Array.from({ length: count }, () => ({
          x: Math.random() * w, y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          r: Math.random() * 1.8 + 0.6,
        }));
      }
      resize();
      window.addEventListener('resize', resize);

      function draw() {
        ctx.clearRect(0, 0, w, h);
        for (let i = 0; i < particles.length; i++) {
          const p = particles[i];
          p.x += p.vx; p.y += p.vy;
          if (p.x < 0 || p.x > w) p.vx *= -1;
          if (p.y < 0 || p.y > h) p.vy *= -1;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(201,168,76,0.6)';
          ctx.fill();
          // bağlantı çizgileri
          for (let j = i + 1; j < particles.length; j++) {
            const q = particles[j];
            const dx = p.x - q.x, dy = p.y - q.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 120) {
              ctx.beginPath();
              ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
              ctx.strokeStyle = `rgba(201,168,76,${0.12 * (1 - dist / 120)})`;
              ctx.lineWidth = 1;
              ctx.stroke();
            }
          }
        }
        requestAnimationFrame(draw);
      }
      draw();
    });
  }

  // ─── 16. Parallax ─────────────────────────────────────────────
  function initParallax() {
    if (reduceMotion) return;
    const els = document.querySelectorAll('[data-parallax]');
    if (!els.length) return;
    window.addEventListener('scroll', () => {
      const sy = window.scrollY;
      els.forEach((el) => {
        const speed = parseFloat(el.dataset.parallax) || 0.3;
        el.style.transform = `translateY(${sy * speed}px)`;
      });
    }, { passive: true });
  }

  // ─── 17. Konfeti ──────────────────────────────────────────────
  function fireConfetti(x, y) {
    if (reduceMotion) return;
    const colors = ['#C9A84C', '#E8C97A', '#111111', '#ffffff', '#A8872E'];
    for (let i = 0; i < 30; i++) {
      const piece = document.createElement('div');
      piece.className = 'confetti-piece';
      piece.style.background = colors[Math.floor(Math.random() * colors.length)];
      piece.style.left = x + 'px';
      piece.style.top = y + 'px';
      piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
      document.body.appendChild(piece);
      const angle = Math.random() * Math.PI * 2;
      const velocity = 60 + Math.random() * 120;
      const dx = Math.cos(angle) * velocity;
      const dy = Math.sin(angle) * velocity - 80;
      piece.animate(
        [
          { transform: 'translate(0,0) rotate(0deg)', opacity: 1 },
          { transform: `translate(${dx}px, ${dy + 220}px) rotate(${Math.random() * 720}deg)`, opacity: 0 },
        ],
        { duration: 1100 + Math.random() * 500, easing: 'cubic-bezier(0.22,1,0.36,1)' }
      );
      setTimeout(() => piece.remove(), 1700);
    }
  }
  window.fireConfetti = fireConfetti;

  // Favoriye eklendiğinde konfeti (başarılı toast yakala)
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-favorite-btn]');
    if (!btn) return;
    const r = btn.getBoundingClientRect();
    setTimeout(() => {
      // Sadece eklendiyse (kalp dolduysa) konfeti at
      const icon = btn.querySelector('[data-fav-icon]');
      if (icon && icon.classList.contains('fill-red-500')) {
        fireConfetti(r.left + r.width / 2, r.top + r.height / 2);
      }
    }, 250);
  });

  // ─── 18. Preloader ────────────────────────────────────────────
  function hidePreloader() {
    const pre = document.getElementById('preloader');
    if (pre) {
      pre.classList.add('done');
      setTimeout(() => pre.remove(), 700);
    }
  }

  // ─── 19. Sayaç animasyonu (gsap yoksa fallback) ───────────────
  function initCounters() {
    const els = document.querySelectorAll('[data-counter]');
    if (!els.length || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseFloat(el.dataset.counter) || 0;
        const dur = 1300; const start = performance.now();
        function tick(now) {
          const prog = Math.min((now - start) / dur, 1);
          const eased = 1 - Math.pow(1 - prog, 3);
          el.textContent = Math.round(target * eased).toLocaleString('tr-TR');
          if (prog < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        io.unobserve(el);
      });
    }, { threshold: 0.5 });
    els.forEach((el) => io.observe(el));
  }

  // ─── Başlat ───────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    initTilt();
    initBackToTop();
    initReveal();
    initZoomLens();
    initScrollProgress();
    initHeaderShrink();
    initCursorGlow();
    initSpotlight();
    initMagnetic();
    initGradientTitle();
    initParticles();
    initParallax();
    initCounters();
  });

  window.addEventListener('load', hidePreloader);
  // Güvenlik: load tetiklenmezse 2.5 sn sonra zorla kapat
  setTimeout(hidePreloader, 2500);
})();
