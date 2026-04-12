/**
 * گالری تصاویر و ویدیو - همیار فرش
 * Mobile First | Drawer | Sort | Lazy Load
 */

document.addEventListener('DOMContentLoaded', function () {

    // ========== فیلتر Drawer موبایل ==========
    var btnMobileFilter = document.getElementById('btnMobileFilter');
    var filterDrawer = document.getElementById('filterDrawer');
    var drawerOverlay = document.getElementById('drawerOverlay');
    var btnCloseDrawer = document.getElementById('btnCloseDrawer');

    function openDrawer() {
        if (filterDrawer) filterDrawer.classList.add('active');
        if (drawerOverlay) drawerOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    function closeDrawer() {
        if (filterDrawer) filterDrawer.classList.remove('active');
        if (drawerOverlay) drawerOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (btnMobileFilter) btnMobileFilter.addEventListener('click', openDrawer);
    if (btnCloseDrawer) btnCloseDrawer.addEventListener('click', closeDrawer);
    if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);

    // ESC برای بستن drawer
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeDrawer();
    });


    // ========== Lazy Load تصاویر ==========
    if ('IntersectionObserver' in window) {
        var lazyImages = document.querySelectorAll('img[loading="lazy"]');
        var imageObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '200px 0px'
        });

        lazyImages.forEach(function (img) {
            imageObserver.observe(img);
        });
    }


    // ========== Skeleton loader (حذف بعد از لود) ==========
    document.querySelectorAll('.image-card-img, .video-card-thumb img').forEach(function (img) {
        if (img.complete) {
            img.parentElement.classList.remove('loading');
        } else {
            img.addEventListener('load', function () {
                this.parentElement.classList.remove('loading');
            });
        }
    });

});


// ========== مرتب‌سازی ==========
function applySort(value) {
    var url = new URL(window.location);
    url.searchParams.set('sort', value);
    url.searchParams.delete('page'); // ریست صفحه‌بندی
    window.location.href = url.toString();
}


// ========== کپی لینک ==========
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
    }
}
