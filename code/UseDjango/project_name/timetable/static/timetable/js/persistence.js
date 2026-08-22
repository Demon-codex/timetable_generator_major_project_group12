/* ===================================
   FORM AUTO-SAVE WITH LOCALSTORAGE
   ===================================
   Automatically save form data as user types
   Restore on page reload to prevent data loss
*/

// Auto-save configuration
const AUTO_SAVE_CONFIG = {
    debounceDelay: 1000, // Save 1 second after user stops typing
    storagePrefix: 'smarttimetable_form_',
    excludeFields: ['csrfmiddlewaretoken', 'DELETE'], // Fields to skip
};

function shouldSkipAutoSaveField(input) {
    const name = input.name || '';

    if (!name || AUTO_SAVE_CONFIG.excludeFields.includes(name)) {
        return true;
    }

    // Hidden formset identity/management fields should never be restored.
    if (input.type === 'hidden') {
        return true;
    }

    if (/(^|-)id$/.test(name) ||
        name.endsWith('-TOTAL_FORMS') ||
        name.endsWith('-INITIAL_FORMS') ||
        name.endsWith('-MIN_NUM_FORMS') ||
        name.endsWith('-MAX_NUM_FORMS')) {
        return true;
    }

    return false;
}

// Debounce function to limit save frequency
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Check if localStorage is available
function isLocalStorageAvailable() {
    try {
        const test = '__localStorage_test__';
        localStorage.setItem(test, test);
        localStorage.removeItem(test);
        return true;
    } catch (e) {
        return false;
    }
}

// Get form identifier (use form action or id)
function getFormIdentifier(form) {
    return form.getAttribute('data-autosave-key') || 
           form.id || 
           form.action.split('/').filter(Boolean).join('_');
}

function shouldRestoreDraft(form) {
    return form.getAttribute('data-autosave-restore') !== 'false';
}

// Save form data to localStorage
function saveFormData(form) {
    if (!isLocalStorageAvailable()) return;
    
    const formId = getFormIdentifier(form);
    const storageKey = AUTO_SAVE_CONFIG.storagePrefix + formId;
    const formData = {};
    
    // Show saving indicator
    showAutoSaveIndicator('saving');
    
    // Get all form inputs
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        const name = input.name;

        // Skip excluded, hidden and management fields
        if (shouldSkipAutoSaveField(input)) return;
        
        // Handle different input types
        if (input.type === 'checkbox') {
            formData[name] = input.checked;
        } else if (input.type === 'radio') {
            if (input.checked) {
                formData[name] = input.value;
            }
        } else if (input.type === 'file') {
            // Skip file inputs (can't be saved to localStorage)
            return;
        } else {
            formData[name] = input.value;
        }
    });
    
    // Save to localStorage with timestamp
    const saveData = {
        timestamp: Date.now(),
        data: formData
    };
    
    try {
        localStorage.setItem(storageKey, JSON.stringify(saveData));
        console.log('Form data auto-saved:', formId);
        // Show saved indicator
        showAutoSaveIndicator('saved');
    } catch (e) {
        console.error('Failed to save form data:', e);
        showAutoSaveIndicator('error');
    }
}

// Restore form data from localStorage
function restoreFormData(form) {
    if (!isLocalStorageAvailable()) return false;
    
    const formId = getFormIdentifier(form);
    const storageKey = AUTO_SAVE_CONFIG.storagePrefix + formId;
    
    try {
        const savedData = localStorage.getItem(storageKey);
        if (!savedData) return false;
        
        const { timestamp, data } = JSON.parse(savedData);
        
        // Check if data is not too old (7 days)
        const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
        if (Date.now() - timestamp > maxAge) {
            localStorage.removeItem(storageKey);
            return false;
        }
        
        // Restore data to form
        let restoredCount = 0;
        Object.entries(data).forEach(([name, value]) => {
            const inputs = form.querySelectorAll(`[name="${name}"]`);
            
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    input.checked = value;
                    restoredCount++;
                } else if (input.type === 'radio') {
                    if (input.value === value) {
                        input.checked = true;
                        restoredCount++;
                    }
                } else {
                    input.value = value;
                    restoredCount++;
                }
            });
        });
        
        if (restoredCount > 0) {
            console.log('Form data restored:', formId, restoredCount, 'fields');
            return true;
        }
        
        return false;
    } catch (e) {
        console.error('Failed to restore form data:', e);
        return false;
    }
}

// Clear saved form data
function clearFormData(form) {
    if (!isLocalStorageAvailable()) return;
    
    const formId = getFormIdentifier(form);
    const storageKey = AUTO_SAVE_CONFIG.storagePrefix + formId;
    localStorage.removeItem(storageKey);
    console.log('Form data cleared:', formId);
}

// Show notification that data was restored
function showRestoreNotification() {
    // Use existing toast system if available
    if (typeof showToast === 'function') {
        showToast('Previous form data restored', 'info', 4000);
    }
}

// Show auto-save indicator
let autoSaveIndicator = null;
let autoSaveTimeout = null;

function showAutoSaveIndicator(status = 'saving') {
    // Create indicator if it doesn't exist
    if (!autoSaveIndicator) {
        autoSaveIndicator = document.createElement('div');
        autoSaveIndicator.className = 'autosave-indicator';
        document.body.appendChild(autoSaveIndicator);
    }
    
    // Clear any existing timeout
    if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
    }
    
    // Update indicator content based on status
    if (status === 'saving') {
        autoSaveIndicator.innerHTML = '<div class="spinner-small"></div><span>Saving...</span>';
        autoSaveIndicator.className = 'autosave-indicator show';
    } else if (status === 'saved') {
        autoSaveIndicator.innerHTML = '<svg class="checkmark" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg><span>Saved</span>';
        autoSaveIndicator.className = 'autosave-indicator saved show';
        
        // Hide after 2 seconds
        autoSaveTimeout = setTimeout(() => {
            autoSaveIndicator.classList.remove('show');
        }, 2000);
    } else if (status === 'error') {
        autoSaveIndicator.innerHTML = '<span>⚠️ Save failed</span>';
        autoSaveIndicator.className = 'autosave-indicator show';
        
        // Hide after 3 seconds
        autoSaveTimeout = setTimeout(() => {
            autoSaveIndicator.classList.remove('show');
        }, 3000);
    }
}

// Initialize auto-save for a form
function initAutoSave(form) {
    if (!form || !isLocalStorageAvailable()) return;
    
    // Restore data on page load
    if (shouldRestoreDraft(form)) {
        const wasRestored = restoreFormData(form);
        if (wasRestored) {
            showRestoreNotification();
        }
    }
    
    // Create debounced save function
    const debouncedSave = debounce(() => saveFormData(form), AUTO_SAVE_CONFIG.debounceDelay);
    
    // Attach event listeners to all form inputs
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        // Skip excluded fields
        if (shouldSkipAutoSaveField(input)) return;
        
        // Save on input change
        input.addEventListener('input', debouncedSave);
        input.addEventListener('change', debouncedSave);
    });
    
    // Clear saved data on successful form submission
    form.addEventListener('submit', function() {
        clearFormData(form);
    });
    
    console.log('Auto-save initialized for form:', getFormIdentifier(form));
}

// Initialize auto-save for all forms with data-autosave attribute
function initAllAutoSaveForms() {
    document.addEventListener('DOMContentLoaded', function() {
        const autoSaveForms = document.querySelectorAll('form[data-autosave="true"]');
        autoSaveForms.forEach(form => initAutoSave(form));
    });
}

// Manual trigger functions (can be called from other scripts)
window.formAutoSave = {
    init: initAutoSave,
    save: saveFormData,
    restore: restoreFormData,
    clear: clearFormData,
};

// Auto-initialize
initAllAutoSaveForms();

/* ===================================
   UI STATE PERSISTENCE
   ===================================
   Remember collapsed/expanded sections, view preferences
*/

const UI_STATE_KEY = 'smarttimetable_ui_state';

// Save UI state
function saveUIState(key, value) {
    if (!isLocalStorageAvailable()) return;
    
    try {
        const currentState = JSON.parse(localStorage.getItem(UI_STATE_KEY) || '{}');
        currentState[key] = value;
        localStorage.setItem(UI_STATE_KEY, JSON.stringify(currentState));
    } catch (e) {
        console.error('Failed to save UI state:', e);
    }
}

// Get UI state
function getUIState(key, defaultValue = null) {
    if (!isLocalStorageAvailable()) return defaultValue;
    
    try {
        const currentState = JSON.parse(localStorage.getItem(UI_STATE_KEY) || '{}');
        return currentState[key] !== undefined ? currentState[key] : defaultValue;
    } catch (e) {
        console.error('Failed to get UI state:', e);
        return defaultValue;
    }
}

// Initialize collapsible sections with state persistence
function initCollapsibleSections() {
    document.addEventListener('DOMContentLoaded', function() {
        const collapsibles = document.querySelectorAll('[data-collapsible]');
        
        collapsibles.forEach(element => {
            const key = element.getAttribute('data-collapsible');
            const isCollapsed = getUIState(`collapsed_${key}`, false);
            
            if (isCollapsed) {
                element.classList.add('collapsed');
            }
            
            // Save state on toggle
            element.addEventListener('click', function() {
                const nowCollapsed = element.classList.contains('collapsed');
                saveUIState(`collapsed_${key}`, nowCollapsed);
            });
        });
    });
}

initCollapsibleSections();

// Export UI state functions
window.uiState = {
    save: saveUIState,
    get: getUIState,
};

/* ===================================
   RECENT ITEMS TRACKING
   ===================================
   Track recently visited departments/years
*/

const RECENT_ITEMS_KEY = 'smarttimetable_recent_items';
const MAX_RECENT_ITEMS = 5;

// Add item to recent list
function addRecentItem(type, id, name) {
    if (!isLocalStorageAvailable()) return;
    
    try {
        const recentItems = JSON.parse(localStorage.getItem(RECENT_ITEMS_KEY) || '{}');
        
        if (!recentItems[type]) {
            recentItems[type] = [];
        }
        
        // Remove if already exists
        recentItems[type] = recentItems[type].filter(item => item.id !== id);
        
        // Add to beginning
        recentItems[type].unshift({
            id: id,
            name: name,
            timestamp: Date.now()
        });
        
        // Limit to MAX_RECENT_ITEMS
        recentItems[type] = recentItems[type].slice(0, MAX_RECENT_ITEMS);
        
        localStorage.setItem(RECENT_ITEMS_KEY, JSON.stringify(recentItems));
    } catch (e) {
        console.error('Failed to save recent item:', e);
    }
}

// Get recent items of a type
function getRecentItems(type) {
    if (!isLocalStorageAvailable()) return [];
    
    try {
        const recentItems = JSON.parse(localStorage.getItem(RECENT_ITEMS_KEY) || '{}');
        return recentItems[type] || [];
    } catch (e) {
        console.error('Failed to get recent items:', e);
        return [];
    }
}

// Export recent items functions
window.recentItems = {
    add: addRecentItem,
    get: getRecentItems,
};
