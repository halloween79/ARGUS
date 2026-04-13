// Global utility functions for ARGUS

// Format a UTC date string to local time
function formatDate(isoString) {
    if (!isoString) return 'N/A';
    return new Date(isoString).toLocaleString();
}

// Show a temporary toast message
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: ${type === 'success' ? '#2e7d32' : '#c62828'};
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        z-index: 9999;
        transition: opacity 0.5s;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}