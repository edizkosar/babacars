{% load static %}/* ════════════════════════════════════════════════════════════════
   BabaCars – Service Worker (PWA)
   Strateji: app shell precache + network-first (HTML) + cache-first (statik)
   ════════════════════════════════════════════════════════════════ */
const CACHE = 'babacars-v1';
const OFFLINE_URL = '/offline/';

const PRECACHE = [
  OFFLINE_URL,
  '{% static "css/main.css" %}',
  '{% static "css/effects.css" %}',
  '{% static "js/main.js" %}',
  '{% static "js/effects.js" %}',
  '{% static "icons/icon-192.png" %}',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  // Sadece kendi origin'imiz
  if (url.origin !== self.location.origin) return;
  // Admin / API / harita verisi cache'lenmesin
  if (url.pathname.startsWith('/admin') ||
      url.pathname.startsWith('/api') ||
      url.pathname.startsWith('/control-panel') ||
      url.pathname.startsWith('/chatbot') ||
      url.pathname.includes('/map/data')) {
    return;
  }

  // HTML sayfaları → network-first, çevrimdışıysa offline sayfası
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // Statik varlıklar → cache-first
  event.respondWith(
    caches.match(req).then((cached) =>
      cached ||
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      }).catch(() => cached)
    )
  );
});
