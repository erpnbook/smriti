/* ============================================================
   SMRITI Retail OS — PWA Service Worker
   Caches critical dark glassmorphism theme files, fonts, and
   essential logo assets to ensure instant checkout rendering.
   ============================================================ */

const CACHE_NAME = 'smriti-cache-v1';
const OFFLINE_URL = '/login';

const ASSETS_TO_CACHE = [
    OFFLINE_URL,
    '/assets/smriti_retail_os/css/smriti_theme.css',
    '/assets/smriti_retail_os/css/smriti_sidebar.css',
    '/assets/smriti_retail_os/css/smriti_branding.css',
    '/assets/smriti_retail_os/js/smriti_sidebar.js',
    '/assets/smriti_retail_os/js/main.js',
    '/assets/smriti_retail_os/images/logo.svg'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SMRITI SW] Pre-caching offline pages and CSS assets');
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        console.log('[SMRITI SW] Clearing old UI cache');
                        return caches.delete(cache);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    // Only intercept requests for static files or standard page templates
    const url = new URL(event.request.url);
    
    // Ignore API calls, transactions, and desk backend methods
    if (url.pathname.startsWith('/api') || url.pathname.startsWith('/app')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(cachedResponse => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                
                // Fallback to network
                return fetch(event.request).then(response => {
                    // Cache newly fetched static assets dynamically
                    if (response && response.status === 200 && response.type === 'basic' && 
                        (url.pathname.includes('/assets/') || url.pathname.includes('/fonts.gstatic.com'))) {
                        let responseClone = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return response;
                }).catch(() => {
                    // Offline fallback
                    if (event.request.mode === 'navigate') {
                        return caches.match(OFFLINE_URL);
                    }
                });
            })
    );
});
