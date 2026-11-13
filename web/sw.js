const CACHE_NAME = 'holygust-v65';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/header-logo.png',
  '/icon.png',
  '/icon-192.png',
  '/icon-512.png',
  '/apple-touch-icon.png',
  '/favicon.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Never cache dynamic API calls or admin routes
  if (event.request.url.includes('/api/') || event.request.url.includes('/admin')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // APP NAVIGATION: Serve cached HolyGust app shell instantly (0.01s).
  // Completely shields riders from EVER seeing Render's cold-start "Starting the Instance" screen!
  if (event.request.mode === 'navigate' || event.request.destination === 'document') {
    event.respondWith(
      caches.match('/').then((cached) => {
        const networkFetch = fetch(event.request).then((res) => {
          if (res && res.status === 200) {
            const resClone = res.clone();
            resClone.text().then((text) => {
              // Only update cache if response is authentic HolyGust and NOT Render's cold-start screen
              if (text && text.includes('HolyGust') && !text.includes('STARTING THE INSTANCE') && !text.includes('WELCOME TO RENDER')) {
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, res.clone()));
              }
            }).catch(() => {});
          }
          return res;
        }).catch(() => null);

        // Instant return of cached HolyGust app shell
        if (cached) {
          return cached;
        }
        return networkFetch.then((nRes) => nRes || caches.match('/'));
      })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request);
    })
  );
});

// ==============================================================================
// 🔔 PWA NATIVE WEB PUSH NOTIFICATIONS (Beta Wind Alarms)
// ==============================================================================
self.addEventListener('push', (event) => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data = { title: 'HolyGust Wind Alarm', body: event.data.text() };
    }
  }

  const title = data.title || '🚨 HolyGust Wind Alarm';
  const options = {
    body: data.body || 'Prime wind detected matching your quiver!',
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    vibrate: [250, 100, 250, 100, 250],
    data: {
      url: data.url || '/'
    },
    actions: [
      { action: 'view', title: (data.url && data.url.includes('open_admin')) ? 'Open Admin Profile' : 'Open Spot Forecast' }
    ]
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = (event.notification.data && event.notification.data.url) || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      // Focus existing window if open
      for (let client of windowClients) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(targetUrl);
          return client.focus();
        }
      }
      // Otherwise open fresh window
      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }
    })
  );
});
