/**
 * Service Worker — همیار فرش PWA
 * کش استاتیک + صفحه آفلاین + استراتژی Network-First
 */
const CACHE_NAME = 'hamyarfarsh-v1';
const OFFLINE_URL = '/offline/';

// فایل‌هایی که باید کش بشن
const PRECACHE_URLS = [
    '/',
    '/offline/',
    '/static/css/bootstrap.rtl.min.css',
    '/static/css/bootstrap-icons.min.css',
    '/static/css/style.css',
    '/static/js/bootstrap.bundle.min.js',
    '/static/manifest.json',
];

// نصب — کش فایل‌های اولیه
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(PRECACHE_URLS);
        }).then(function() {
            return self.skipWaiting();
        })
    );
});

// فعال‌سازی — حذف کش‌های قدیمی
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(name) {
                    return name !== CACHE_NAME;
                }).map(function(name) {
                    return caches.delete(name);
                })
            );
        }).then(function() {
            return self.clients.claim();
        })
    );
});

// درخواست — استراتژی Network-First
self.addEventListener('fetch', function(event) {
    var request = event.request;

    // فقط GET
    if (request.method !== 'GET') return;

    // API و admin رو کش نکن
    if (request.url.includes('/api/') ||
        request.url.includes('/admin/') ||
        request.url.includes('/dashboard/') ||
        request.url.includes('/cms/')) {
        return;
    }

    // استاتیک‌ها — Cache-First
    if (request.url.includes('/static/') || request.url.includes('/media/')) {
        event.respondWith(
            caches.match(request).then(function(cached) {
                if (cached) return cached;
                return fetch(request).then(function(response) {
                    if (response.ok) {
                        var clone = response.clone();
                        caches.open(CACHE_NAME).then(function(cache) {
                            cache.put(request, clone);
                        });
                    }
                    return response;
                });
            })
        );
        return;
    }

    // صفحات HTML — Network-First + Offline fallback
    if (request.headers.get('Accept') && request.headers.get('Accept').includes('text/html')) {
        event.respondWith(
            fetch(request).then(function(response) {
                // کش صفحات موفق
                if (response.ok) {
                    var clone = response.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(request, clone);
                    });
                }
                return response;
            }).catch(function() {
                // آفلاین — اول از کش، بعد صفحه آفلاین
                return caches.match(request).then(function(cached) {
                    return cached || caches.match(OFFLINE_URL);
                });
            })
        );
        return;
    }
});
