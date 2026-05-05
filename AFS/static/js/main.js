/**
 * Faculty Scheduling System - Main JavaScript
 * Handle client-side functionality and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentElement) {
                alert.style.display = 'none';
            }
        }, 5000);
    });
});

/**
 * Autofill demo credentials
 */
function autofillDemo() {
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    if (usernameInput && passwordInput) {
        usernameInput.value = 'admin';
        passwordInput.value = 'admin123';
        usernameInput.focus();
    }
}

/**
 * Validate login form
 */
function validateLoginForm(e) {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !password) {
        e.preventDefault();
        alert('Please fill in all fields');
        return false;
    }

    if (username.length < 3) {
        e.preventDefault();
        alert('Username must be at least 3 characters long');
        return false;
    }

    if (password.length < 6) {
        e.preventDefault();
        alert('Password must be at least 6 characters long');
        return false;
    }

    return true;
}

/**
 * Add CSRF token to fetch requests
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getCsrfToken() {
    return getCookie('csrftoken');
}

/**
 * Make API call with CSRF token
 */
function makeRequest(url, options = {}) {
    const csrftoken = getCsrfToken();
    const headers = {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
        ...options.headers
    };

    return fetch(url, {
        ...options,
        headers: headers
    });
}

/**
 * Format date to readable format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format time in 12-hour format
 */
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));

    return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

// Export functions for use in templates
window.autofillDemo = autofillDemo;
window.validateLoginForm = validateLoginForm;
window.makeRequest = makeRequest;
window.formatDate = formatDate;
window.formatTime = formatTime;
