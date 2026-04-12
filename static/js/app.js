/* همیار فرش - app.js */
document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Format numbers with Persian comma separator
    function formatPrice(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    // Expose globally for later use
    window.HF = {
        formatPrice: formatPrice,
    };
});
