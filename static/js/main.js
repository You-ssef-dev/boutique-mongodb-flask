/**
 * Main JavaScript File for BoutiqueComplete1
 * Contains API helpers, Toast notifications, and utility functions.
 */

/* --- API Helper --- */
const api = {
    async request(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'API Request Failed');
            }

            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(url) { return this.request(url, 'GET'); },
    post(url, data) { return this.request(url, 'POST', data); },
    put(url, data) { return this.request(url, 'PUT', data); },
    delete(url, data) { return this.request(url, 'DELETE', data); }
};

/* --- Toast Notifications --- */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    // Icon
    const icon = type === 'success'
        ? "<i class='bx bxs-check-circle'></i>"
        : "<i class='bx bxs-error-circle'></i>";

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/* --- Modal Management --- */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.open');
        openModals.forEach(modal => closeModal(modal.id));
    }
});

/* --- Formatting Utilities --- */
const currencyFormatter = new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR'
});

function formatCurrency(amount) {
    return currencyFormatter.format(amount || 0);
}

/* --- Navigation Active State --- */
document.addEventListener('DOMContentLoaded', () => {
    // Current path highlighting is handled by Jinja2 in base.html

    // Theme Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = themeToggleBtn ? themeToggleBtn.querySelector('i') : null;
    const html = document.documentElement;

    // Initialize icon based on current theme
    const currentTheme = html.getAttribute('data-theme') || 'dark';
    if (themeIcon) {
        themeIcon.className = currentTheme === 'light' ? 'bx bxs-sun' : 'bx bxs-moon';
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const oldTheme = html.getAttribute('data-theme') || 'dark';
            const newTheme = oldTheme === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);

            // Update Icon
            if (themeIcon) {
                themeIcon.className = newTheme === 'light' ? 'bx bxs-sun' : 'bx bxs-moon';
            }

            // Show toast
            if (typeof showToast === 'function') {
                showToast(`Switched to ${newTheme === 'light' ? 'Light' : 'Dark'} Mode`, 'success');
            }
        });
    }
});
