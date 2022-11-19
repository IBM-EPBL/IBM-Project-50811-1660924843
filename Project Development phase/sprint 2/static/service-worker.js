// This is based on the First Progressive Web App Tutorial by Google
// https://codelabs.developers.google.com/codelabs/your-first-pwapp/
const cacheName = 'flask-PWA-v1';
const filesToCache = [
    '/',
    '/static/app.js',
    '/static/styles.css',
    '/offline.html',
    '/static/images/pwa-light.png'
];

// When the 'install' event is fired we will cache
// the html, javascript, css, images and any other files important
// to the operation of the application shell
self.addEventListener('install', (e) => {
  console.log('[ServiceWorker] Install');
  e.waitUntil((async () => {
    const cache = await caches.open(cacheName)
    console.log('[ServiceWorker] Caching app shell');
    await cache.addAll(filesToCache);
  })());
});

// We then listen for the service worker to be activated/started. Once it is
// ensures that your service worker updates its cache whenever any of the app shell files change.
// In order for this to work, you'd need to increment the cacheName variable at the top of this service worker file.
self.addEventListener('activate', (e) => {
  console.log('[ServiceWorker] Activate');
  e.waitUntil((async () => {
    const cacheKeys = await caches.keys();
    cacheKeys.map(async (key) => {
      if (key !== cacheName) {
        console.log('[ServiceWorker] Removing old cache', key);
        await caches.delete(key);
      }
    });
  })());
  return self.clients.claim();
});

