// FaceMark FRCAS Service Worker
const CACHE_NAME = 'facemark-pwa-v1.1';
const STATIC_ASSETS = [
  '/',
  '/professor',
  '/student',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/icon-maskable-512.png',
  '/static/icons/apple-touch-icon.png'
];

// Install: Cache core shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Activate: Clean up stale caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Network-First for API and dynamic POST/PUT, Cache-First for static assets
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Skip non-GET requests (attendance process, confirm, registration)
  if (req.method !== 'GET') {
    return;
  }

  // Bypass API and dynamic endpoints from static caching
  if (
    url.pathname.startsWith('/auth') ||
    url.pathname.startsWith('/attendance') ||
    url.pathname.startsWith('/reports') ||
    url.pathname.startsWith('/classes') ||
    url.pathname.startsWith('/students')
  ) {
    return;
  }

  // For app pages (/ or /student or /professor): Network first, falling back to cache
  if (req.mode === 'navigate' || url.pathname === '/' || url.pathname === '/professor' || url.pathname === '/student') {
    event.respondWith(
      fetch(req)
        .then((networkRes) => {
          const resClone = networkRes.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
          return networkRes;
        })
        .catch(() => caches.match(req).then((cached) => cached || caches.match('/')))
    );
    return;
  }

  // For static assets (images, fonts, scripts): Cache first, fallback to network
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((networkRes) => {
        if (!networkRes || networkRes.status !== 200 || networkRes.type !== 'basic') {
          return networkRes;
        }
        const resClone = networkRes.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
        return networkRes;
      });
    })
  );
});
