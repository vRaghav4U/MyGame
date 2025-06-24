// API Pagination Manager - Custom JavaScript

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeFormValidation();
    initializeAutoRefresh();
    initializeClipboard();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation for JSON fields
function initializeFormValidation() {
    const jsonFields = document.querySelectorAll('textarea[name="headers"], textarea[name="pagination_params"]');
    
    jsonFields.forEach(function(field) {
        field.addEventListener('input', function() {
            validateJsonField(this);
        });
        
        field.addEventListener('blur', function() {
            validateJsonField(this);
        });
    });
}

// Validate JSON field
function validateJsonField(field) {
    const value = field.value.trim();
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    if (value === '') {
        return; // Empty is valid
    }
    
    try {
        JSON.parse(value);
        field.classList.add('is-valid');
        hideFieldError(field);
    } catch (e) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Invalid JSON format: ' + e.message);
    }
}

// Show field error
function showFieldError(field, message) {
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

// Hide field error
function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

// Auto-refresh for running jobs
function initializeAutoRefresh() {
    // Check if we're on a page that needs auto-refresh
    const runningJobs = document.querySelectorAll('.badge.bg-primary');
    const statusRunning = document.querySelectorAll('.status-running');
    
    if (runningJobs.length > 0 || statusRunning.length > 0) {
        // Set up auto-refresh every 10 seconds
        setInterval(function() {
            const currentRunningJobs = document.querySelectorAll('.badge.bg-primary');
            if (currentRunningJobs.length > 0) {
                window.location.reload();
            }
        }, 10000);
    }
}

// Clipboard functionality
function initializeClipboard() {
    // Add click handlers for copy buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-copy]') || e.target.closest('[data-copy]')) {
            const button = e.target.matches('[data-copy]') ? e.target : e.target.closest('[data-copy]');
            const targetSelector = button.getAttribute('data-copy');
            const targetElement = document.querySelector(targetSelector);
            
            if (targetElement) {
                copyToClipboard(targetElement.textContent, button);
            }
        }
    });
}

// Copy text to clipboard
function copyToClipboard(text, button) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(button);
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
            fallbackCopyToClipboard(text, button);
        });
    } else {
        fallbackCopyToClipboard(text, button);
    }
}

// Fallback copy method for older browsers
function fallbackCopyToClipboard(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopySuccess(button);
    } catch (err) {
        console.error('Fallback copy failed: ', err);
    }
    
    document.body.removeChild(textArea);
}

// Show copy success feedback
function showCopySuccess(button) {
    const originalHTML = button.innerHTML;
    const originalClasses = button.className;
    
    button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
    button.className = button.className.replace(/btn-outline-\w+/, 'btn-success');
    
    setTimeout(function() {
        button.innerHTML = originalHTML;
        button.className = originalClasses;
    }, 2000);
}

// Format JSON in textareas
function formatJson(textareaId) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;
    
    try {
        const value = textarea.value.trim();
        if (value) {
            const parsed = JSON.parse(value);
            textarea.value = JSON.stringify(parsed, null, 2);
            validateJsonField(textarea);
        }
    } catch (e) {
        // Invalid JSON, don't format
        validateJsonField(textarea);
    }
}

// Confirm deletion
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Show loading state
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
    }
}

// Hide loading state
function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
    }
}

// Format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Format duration
function formatDuration(seconds) {
    if (seconds < 60) {
        return seconds + 's';
    } else if (seconds < 3600) {
        return Math.floor(seconds / 60) + 'm ' + (seconds % 60) + 's';
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return hours + 'h ' + minutes + 'm';
    }
}

// Add pagination type change handler for config forms
document.addEventListener('change', function(e) {
    if (e.target.id === 'pagination_type') {
        updatePaginationHelp(e.target.value);
    }
});

// Update pagination help text based on selected type
function updatePaginationHelp(type) {
    const helpExamples = {
        'page': '{"page_param": "page", "page_size_param": "per_page", "page_size": 20, "start_page": 1}',
        'offset': '{"offset_param": "offset", "limit_param": "limit", "limit": 20, "start_offset": 0}',
        'cursor': '{"cursor_param": "cursor", "cursor_field": "next_cursor", "page_size_param": "limit", "page_size": 20}'
    };
    
    const textarea = document.querySelector('textarea[name="pagination_params"]');
    if (textarea && textarea.value.trim() === '') {
        textarea.value = helpExamples[type] || '';
        textarea.placeholder = helpExamples[type] || '';
    }
}

// Global functions for templates
window.formatJson = formatJson;
window.confirmDelete = confirmDelete;
window.formatBytes = formatBytes;
window.formatDuration = formatDuration;
