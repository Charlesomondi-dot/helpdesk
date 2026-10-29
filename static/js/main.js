// Main JavaScript for STJTID IT Helpdesk

// Initialize tooltips and basic interactions
document.addEventListener('DOMContentLoaded', function() {
    console.log('STJTID IT Helpdesk loaded');
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
});

// Utility function to make API requests
async function makeRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        return {
            ok: response.ok,
            status: response.status,
            data: await response.json()
        };
    } catch (error) {
        console.error('API Request Error:', error);
        return {
            ok: false,
            status: 500,
            data: { error: 'Network error' }
        };
    }
}

// Format date to readable format
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Display notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('body');
    container.insertBefore(notification, container.firstChild);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Confirm action
function confirmAction(message) {
    return confirm(message);
}
