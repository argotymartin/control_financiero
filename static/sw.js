var CACHE = 'control-financiero-v1';
var URLS = ['/', '/login', '/static/icon-192.png', '/static/icon-512.png'];

self.addEventListener('install', function(e) {
    e.waitUntil(caches.open(CACHE).then(function(cache) {
        return cache.addAll(URLS);
    }));
});

self.addEventListener('fetch', function(e) {
    e.respondWith(
        fetch(e.request).catch(function() {
            return caches.match(e.request);
        })
    );
});

// Manejar push notifications
self.addEventListener('push', function(e) {
    var data = {};
    try {
        data = e.data ? e.data.json() : {};
    } catch(err) {
        data = { body: e.data ? e.data.text() : 'Nuevo pago registrado' };
    }

    var opciones = {
        body: data.body || 'Se ha registrado un nuevo movimiento',
        icon: '/static/icon-192.png',
        badge: '/static/icon-192.png',
        tag: 'pago-notificacion',
        requireInteraction: true
    };

    e.waitUntil(
        self.registration.showNotification(data.title || 'Control Financiero', opciones)
    );
});

// Manejar click en notificación
self.addEventListener('notificationclick', function(e) {
    e.notification.close();
    e.waitUntil(
        clients.matchAll({ type: 'window' }).then(function(windowClients) {
            for (var i = 0; i < windowClients.length; i++) {
                var client = windowClients[i];
                if (client.url === '/' && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow('/');
            }
        })
    );
});
