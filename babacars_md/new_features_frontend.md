# new_features_frontend.md

## Reference
See PROJECT_OVERVIEW.md, AI_CONSTRAINTS.md, template_redesign.md.

## Purpose
Frontend-only features. No backend changes. Pure template + JS.
Token-efficient: minimal code, reuses existing endpoints.

## Features in this file
1. Photo Gallery (Fullscreen, swipe, zoom)
2. Listing Share (WhatsApp + copy link)

---

## 1. Photo Gallery — listings/detail.html

Add a fullscreen gallery overlay. Pure JS, no backend.

### HTML (add to detail.html, after main photo gallery):
```html
<!-- Fullscreen Gallery Overlay -->
<div id="galleryOverlay" class="fixed inset-0 z-[100] bg-black/95 hidden items-center justify-center">
  <button id="galleryClose" class="absolute top-6 right-6 text-white text-3xl font-light hover:text-gold">&times;</button>
  <button id="galleryPrev" class="absolute left-4 md:left-8 text-white text-5xl font-light hover:text-gold select-none">&#8249;</button>
  <button id="galleryNext" class="absolute right-4 md:right-8 text-white text-5xl font-light hover:text-gold select-none">&#8250;</button>
  <img id="galleryImg" src="" class="max-h-[85vh] max-w-[90vw] object-contain transition-transform duration-200" style="cursor: zoom-in;">
  <div id="galleryCounter" class="absolute bottom-6 left-1/2 -translate-x-1/2 text-white text-sm font-medium tracking-wide"></div>
</div>
```

### JS (add to detail.html script block):
```javascript
(function() {
  const photos = Array.from(document.querySelectorAll('[data-gallery-photo]')).map(el => el.dataset.src);
  if (!photos.length) return;
  let current = 0, zoomed = false;
  const overlay = document.getElementById('galleryOverlay');
  const img = document.getElementById('galleryImg');
  const counter = document.getElementById('galleryCounter');

  function show(i) {
    current = (i + photos.length) % photos.length;
    img.src = photos[current];
    counter.textContent = `${current + 1} / ${photos.length}`;
    img.style.transform = 'scale(1)';
    img.style.cursor = 'zoom-in';
    zoomed = false;
  }
  function open(i) {
    show(i);
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    overlay.classList.add('hidden');
    overlay.classList.remove('flex');
    document.body.style.overflow = '';
  }

  document.querySelectorAll('[data-gallery-open]').forEach((el, idx) => {
    el.addEventListener('click', () => open(parseInt(el.dataset.galleryOpen) || idx));
  });
  document.getElementById('galleryClose').addEventListener('click', close);
  document.getElementById('galleryPrev').addEventListener('click', () => show(current - 1));
  document.getElementById('galleryNext').addEventListener('click', () => show(current + 1));
  img.addEventListener('click', () => {
    zoomed = !zoomed;
    img.style.transform = zoomed ? 'scale(2)' : 'scale(1)';
    img.style.cursor = zoomed ? 'zoom-out' : 'zoom-in';
  });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', (e) => {
    if (overlay.classList.contains('hidden')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  // Touch swipe
  let startX = 0;
  overlay.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; });
  overlay.addEventListener('touchend', (e) => {
    const diff = e.changedTouches[0].clientX - startX;
    if (Math.abs(diff) > 50) show(diff > 0 ? current - 1 : current + 1);
  });
})();
```

### Requirement:
- Main photo and each thumbnail must have `data-gallery-open="INDEX"` attribute
- A hidden list of all photo URLs with `data-gallery-photo data-src="URL"` for JS to read
```html
{% for photo in photos %}
  <span data-gallery-photo data-src="{{ photo.image.url }}" class="hidden"></span>
{% endfor %}
```

---

## 2. Listing Share — listings/detail.html

Add share buttons. WhatsApp + copy link. Pure JS.

### HTML (add to detail.html info panel):
```html
<div class="flex items-center gap-2 mt-4">
  <span class="form-label mb-0">Paylaş</span>
  <a id="shareWhatsapp" href="#" target="_blank" rel="noopener"
     class="btn btn-outline btn-sm" title="WhatsApp'ta paylaş">
    WhatsApp
  </a>
  <button id="shareCopy" class="btn btn-outline btn-sm" title="Linki kopyala">
    Linki Kopyala
  </button>
</div>
```

### JS (add to detail.html script block):
```javascript
(function() {
  const url = window.location.href;
  const title = document.title;
  const wa = document.getElementById('shareWhatsapp');
  if (wa) {
    wa.href = `https://wa.me/?text=${encodeURIComponent(title + ' - ' + url)}`;
  }
  const copyBtn = document.getElementById('shareCopy');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(url);
        if (window.showToast) showToast('Link kopyalandı.', 'success');
        else copyBtn.textContent = 'Kopyalandı!';
      } catch {
        if (window.showToast) showToast('Kopyalanamadı.', 'error');
      }
    });
  }
})();
```

---

## Healthcheck
After implementation run:
```bash
python manage.py runserver
```
Manually verify in browser:
- Click photo → fullscreen gallery opens
- Arrow keys / swipe navigate photos
- Click image → zoom toggle
- Escape closes gallery
- WhatsApp share opens with listing link
- Copy link button copies URL and shows toast
Expected: gallery and share work, no console errors.

---

## PROMPT

### Context Files (read before coding)
- PROJECT_OVERVIEW.md
- AI_CONSTRAINTS.md
- template_redesign.md

### Task
Add photo gallery and share features to listings/detail.html. Frontend only. No backend changes.

### Rules
1. Pure JS + HTML. No Python changes.
2. Reuse existing showToast() if present.
3. Gallery must support: click-to-open, prev/next, keyboard, swipe, zoom toggle, escape close.
4. Share: WhatsApp link + copy-to-clipboard.
5. Match Warm Luxury Minimal theme (gold accents, square buttons).

### Output
Updated detail.html sections only. No explanations.
