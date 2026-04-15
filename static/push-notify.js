// Push Notifications - Web Push API
const VAPID_PUBLIC_KEY = 'BCzFQUfKsgTTvEHJAf0nab14ePgbp_A42PqxSbbtEradsTO8vkssn_fEszWLp500nV35STGjezTkqUwTeBQtegk';

async function registerPushNotifications() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.log('Push notifications no soportadas');
        return;
    }

    try {
        // Registrar service worker
        const registration = await navigator.serviceWorker.register('/static/sw.js');
        console.log('Service Worker registrado:', registration);

        // Solicitar permisos
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log('Permiso de notificación:', permission);
        }

        // Si permiso es granted, suscribirse a push
        if (Notification.permission === 'granted') {
            await subscribeToPush(registration);
        }
    } catch (error) {
        console.error('Error registrando push notifications:', error);
    }
}

async function subscribeToPush(registration) {
    try {
        // Verificar si ya está suscrito
        let subscription = await registration.pushManager.getSubscription();

        if (!subscription) {
            // Crear suscripción
            const vapidPublicKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: vapidPublicKey
            });
            console.log('Suscripción creada:', subscription);
        }

        // Enviar suscripción al servidor
        await savePushSubscription(subscription);
    } catch (error) {
        console.error('Error suscribiendo a push:', error);
    }
}

async function savePushSubscription(subscription) {
    try {
        const response = await fetch('/api/push-subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                endpoint: subscription.endpoint,
                auth: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('auth')))),
                p256dh: btoa(String.fromCharCode.apply(null, new Uint8Array(subscription.getKey('p256dh'))))
            })
        });

        if (response.ok) {
            console.log('Suscripción guardada en servidor');
        } else {
            console.error('Error guardando suscripción:', response.statusText);
        }
    } catch (error) {
        console.error('Error enviando suscripción:', error);
    }
}

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }

    return outputArray;
}

// Ejecutar al cargar la página
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', registerPushNotifications);
} else {
    registerPushNotifications();
}
