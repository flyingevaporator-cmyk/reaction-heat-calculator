/* Reaction Heat Energy Calculator — Service Worker
 * Strategy:
 *   - App shell (HTML/icons/manifest): cache-first, update in background
 *   - Google Fonts: stale-while-revalidate
 * Bump CACHE_VERSION on every release so clients refresh.
 */
const CACHE_VERSION = 'rxn-heat-v2';
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const FONT_CACHE = `${CACHE_VERSION}-fonts`;

const SHELL_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon_32x32.png',
  './icons/icon_150x150.png',
  './icons/icon_256x256.png',
  './icons/icon_300x300.svg',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => !k.startsWith(CACHE_VERSION))
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Google Fonts — stale-while-revalidate
  if (
    url.hostname === 'fonts.googleapis.com' ||
    url.hostname === 'fonts.gstatic.com'
  ) {
    event.respondWith(
      caches.open(FONT_CACHE).then(async (cache) => {
        const cached = await cache.match(req);
        const network = fetch(req)
          .then((res) => {
            if (res.ok) cache.put(req, res.clone());
            return res;
          })
          .catch(() => cached);
        return cached || network;
      })
    );
    return;
  }

  // Same-origin app shell — cache-first, fall back to network, then to shell
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(req).then(
        (cached) =>
          cached ||
          fetch(req)
            .then((res) => {
              if (res.ok && res.type === 'basic') {
                const clone = res.clone();
                caches.open(SHELL_CACHE).then((c) => c.put(req, clone));
              }
              return res;
            })
            .catch(() => caches.match('./index.html'))
      )
    );
  }
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});
