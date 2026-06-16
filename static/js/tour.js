// ════════════════════════════════════════════════════════════════
// BabaCars – tour.js
// Bağımsız tanıtım / onboarding turu. Kütüphane gerektirmez.
// ════════════════════════════════════════════════════════════════
(function () {
  'use strict';

  // ─── Tur tanımları ────────────────────────────────────────────
  // selector boş/null ise ekran ortasında "hedefsiz" gösterilir.
  // Hedef bulunamayan adımlar otomatik atlanır.

  // 1) Genel site turu (ana sayfa / her yerde)
  const HOME_STEPS = [
    {
      selector: null,
      title: 'BabaCars\'a Hoş Geldiniz! 👋',
      body: 'Size platformu 30 saniyede tanıtalım. Araç alım, satım ve kiralama burada çok kolay. Başlayalım!',
    },
    {
      selector: 'header nav a[href$="/"]',
      title: 'İlanlara Göz Atın',
      body: 'Buradan tüm araç ilanlarını görebilirsiniz. Vitrindeki en yeni araçlar ana sayfada listelenir.',
    },
    {
      selector: 'header nav a[href*="listing_type=sale"]',
      title: 'Satılık & Kiralık',
      body: 'Aradığınız ne? Satılık veya kiralık araçları tek tıkla filtreleyin.',
    },
    {
      selector: 'form[action*="search"]',
      title: 'Hızlı Arama',
      body: 'Marka, şehir ve ilan tipine göre saniyeler içinde arama yapın. Örneğin "BMW, İstanbul".',
    },
    {
      selector: '#chat-bubble',
      title: 'Yapay Zekâ Asistanı 🤖',
      body: '"300 bin altında BMW var mı?" gibi doğal cümlelerle sorun, asistan size uygun ilanları getirsin.',
    },
    {
      selector: '#theme-toggle-btn',
      title: 'Açık / Koyu Tema',
      body: 'Gözünüzü yormayalım. Buradan istediğiniz an aydınlık veya karanlık moda geçebilirsiniz.',
    },
    {
      selector: '#user-menu-wrapper, header a[href*="login"]',
      title: 'Hesabınız',
      body: 'Profiliniz, favorileriniz, tekliflileriniz ve rezervasyonlarınız hep burada. Satıcı olup ilan da verebilirsiniz!',
    },
    {
      selector: null,
      title: 'Hazırsınız! 🚗',
      body: 'Artık BabaCars\'ı keşfedebilirsiniz. Bu turu istediğiniz zaman sağ üstteki "?" butonundan tekrar başlatabilirsiniz.',
    },
  ];

  // 2) Filtreleme / arama turu (arama sayfası)
  const SEARCH_STEPS = [
    {
      selector: 'aside form, form[method="get"], form[method="GET"]',
      title: 'Gelişmiş Filtreleme 🔍',
      body: 'Bu panelden aradığınız aracı en ince ayrıntısına kadar filtreleyebilirsiniz. Birlikte göz atalım.',
    },
    {
      selector: '#id_listing_type',
      title: 'İlan Türü',
      body: 'Önce ne aradığınızı seçin: Satılık mı, Kiralık mı? Boş bırakırsanız ikisi de listelenir.',
    },
    {
      selector: '#id_make',
      title: 'Marka & Model',
      body: 'Belirli bir marka (BMW, Toyota...) veya model arıyorsanız buraya yazın. Kısmi yazım da çalışır.',
    },
    {
      selector: '#id_year_min',
      title: 'Yıl Aralığı',
      body: 'Min ve Max yıl girerek aracın model yılını sınırlayın. Örneğin 2018 – 2023 arası.',
    },
    {
      selector: '#id_price_min',
      title: 'Fiyat Aralığı 💰',
      body: 'Bütçenize göre alt ve üst fiyat sınırı belirleyin. Sadece üst sınır da girebilirsiniz.',
    },
    {
      selector: '#id_fuel_type',
      title: 'Yakıt, Vites & Kasa',
      body: 'Dizel mi benzin mi? Otomatik mi manuel mi? SUV mu sedan mı? Teknik tercihlerinizi buradan daraltın.',
    },
    {
      selector: '#id_city',
      title: 'Şehir',
      body: 'Size yakın araçları görmek için şehir girin. Örneğin "İstanbul".',
    },
    {
      selector: '#id_ordering',
      title: 'Sıralama',
      body: 'Sonuçları fiyata, tarihe veya popülerliğe göre sıralayın. En uygunu en üste gelsin.',
    },
    {
      selector: 'aside form button[type="submit"]',
      title: 'Filtrele & Sıfırla',
      body: 'Seçimlerinizi uygulamak için "Filtrele"ye basın. Tüm filtreleri temizlemek için hemen altındaki "Sıfırla" bağlantısını kullanın.',
    },
    {
      selector: null,
      title: 'İşte bu kadar! ✅',
      body: 'Artık aradığınız aracı saniyeler içinde bulabilirsiniz. Bu turu "?" butonundan tekrar açabilirsiniz.',
    },
  ];

  const TOURS = {
    home:   { key: 'babacars-tour-done',        steps: HOME_STEPS },
    search: { key: 'babacars-tour-search-done', steps: SEARCH_STEPS },
  };

  // Hangi tur bu sayfaya ait? Arama sayfasında benzersiz olan
  // #id_ordering alanına bakarak karar veriyoruz.
  function detectTourName() {
    if (document.querySelector('#id_ordering') && document.querySelector('#id_make')) {
      return 'search';
    }
    return 'home';
  }

  let current = 0;
  let activeSteps = [];
  let activeKey = 'babacars-tour-done';
  let overlay, spotlight, tooltip;

  // ─── DOM kurulum ──────────────────────────────────────────────
  function buildDom() {
    if (overlay) return;
    overlay = document.createElement('div');
    overlay.id = 'tour-overlay';
    spotlight = document.createElement('div');
    spotlight.id = 'tour-spotlight';
    tooltip = document.createElement('div');
    tooltip.id = 'tour-tooltip';
    overlay.appendChild(spotlight);
    overlay.appendChild(tooltip);
    document.body.appendChild(overlay);

    // Boş alana tıklayınca kapatma (sadece overlay zemini)
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) { /* zemine tıklama turu kapatmasın */ }
    });
    document.addEventListener('keydown', onKey);
  }

  function onKey(e) {
    if (!overlay || !overlay.classList.contains('active')) return;
    if (e.key === 'Escape') endTour(true);
    else if (e.key === 'ArrowRight') next();
    else if (e.key === 'ArrowLeft') prev();
  }

  // ─── Adım gösterimi ───────────────────────────────────────────
  function showStep(i) {
    const step = activeSteps[i];
    if (!step) return;
    const target = step.selector ? document.querySelector(step.selector) : null;

    // Spotlight konumu
    if (target) {
      const r = target.getBoundingClientRect();
      const pad = 8;
      spotlight.classList.remove('no-target');
      spotlight.style.top = (r.top - pad) + 'px';
      spotlight.style.left = (r.left - pad) + 'px';
      spotlight.style.width = (r.width + pad * 2) + 'px';
      spotlight.style.height = (r.height + pad * 2) + 'px';
      // Görünür değilse kaydır
      if (r.top < 0 || r.bottom > window.innerHeight) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else {
      spotlight.classList.add('no-target');
      spotlight.style.top = '50%';
      spotlight.style.left = '50%';
      spotlight.style.width = '0px';
      spotlight.style.height = '0px';
    }

    // Tooltip içeriği
    const dots = activeSteps.map((_, idx) =>
      `<span class="tt-dot ${idx === i ? 'active' : ''}"></span>`).join('');
    const isFirst = i === 0;
    const isLast = i === activeSteps.length - 1;
    tooltip.innerHTML = `
      <div class="tt-step">Adım ${i + 1} / ${activeSteps.length}</div>
      <h3 class="tt-title">${step.title}</h3>
      <p class="tt-body">${step.body}</p>
      <div class="tt-dots">${dots}</div>
      <div class="tt-actions">
        <button class="tt-skip" data-tour="skip">Turu Atla</button>
        <div class="tt-nav">
          ${isFirst ? '' : '<button class="tt-btn tt-btn-ghost" data-tour="prev">Geri</button>'}
          <button class="tt-btn tt-btn-primary" data-tour="next">${isLast ? 'Bitir' : 'İleri →'}</button>
        </div>
      </div>`;

    // Tooltip konumlandırma
    positionTooltip(target);
  }

  function positionTooltip(target) {
    // Önce ölçmek için geçici görünür yap
    const tw = 320, th = tooltip.offsetHeight || 200;
    const margin = 16;
    let top, left;

    if (!target) {
      top = (window.innerHeight - th) / 2;
      left = (window.innerWidth - tw) / 2;
    } else {
      const r = target.getBoundingClientRect();
      const spaceBelow = window.innerHeight - r.bottom;
      const spaceAbove = r.top;
      if (spaceBelow > th + margin || spaceBelow > spaceAbove) {
        top = r.bottom + margin;          // altına
      } else {
        top = r.top - th - margin;        // üstüne
      }
      left = r.left + r.width / 2 - tw / 2;
    }

    // Ekran içinde kal
    left = Math.max(margin, Math.min(left, window.innerWidth - tw - margin));
    top = Math.max(margin, Math.min(top, window.innerHeight - th - margin));
    tooltip.style.top = top + 'px';
    tooltip.style.left = left + 'px';
  }

  // ─── Navigasyon ───────────────────────────────────────────────
  function next() {
    if (current < activeSteps.length - 1) { current++; showStep(current); }
    else endTour(true);
  }
  function prev() {
    if (current > 0) { current--; showStep(current); }
  }

  // ─── Başlat / bitir ───────────────────────────────────────────
  function startTour(tourName) {
    buildDom();
    const name = (tourName && TOURS[tourName]) ? tourName : detectTourName();
    const tour = TOURS[name];
    activeKey = tour.key;
    // Hedefi bulunamayan (ve hedefsiz olmayan) adımları ele
    activeSteps = tour.steps.filter(s => !s.selector || document.querySelector(s.selector));
    if (!activeSteps.length) return;
    current = 0;
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    showStep(0);
  }

  function endTour(markDone) {
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
    if (markDone) {
      try { localStorage.setItem(activeKey, '1'); } catch (e) {}
    }
  }

  // Tooltip buton tıklamaları
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-tour]');
    if (!btn) return;
    const action = btn.dataset.tour;
    if (action === 'next') next();
    else if (action === 'prev') prev();
    else if (action === 'skip') endTour(true);
    else if (action === 'start') { e.preventDefault(); startTour(); }
  });

  // Pencere yeniden boyutlanınca konumları tazele
  window.addEventListener('resize', () => {
    if (overlay && overlay.classList.contains('active')) showStep(current);
  });

  // Global erişim
  window.startTour = startTour;

  // İlk ziyarette otomatik başlat (preloader bitince)
  // Her sayfa türünün kendi "görüldü" kaydı vardır.
  document.addEventListener('DOMContentLoaded', () => {
    const name = detectTourName();
    let done = false;
    try { done = localStorage.getItem(TOURS[name].key) === '1'; } catch (e) {}
    if (!done) {
      setTimeout(() => startTour(name), 1400); // preloader + giriş animasyonu sonrası
    }
  });
})();
