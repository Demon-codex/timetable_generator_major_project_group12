/**
 * Undo/Redo Manager - Handles history tracking for form changes
 */

(function() {
    'use strict';

    const HISTORY_KEY_PREFIX = 'timetable_history_';
    const MAX_HISTORY_SIZE = 50; // Maximum number of undo states

    /**
     * UndoRedo Manager Class
     */
    class UndoRedoManager {
        constructor(formId) {
            this.formId = formId;
            this.historyKey = HISTORY_KEY_PREFIX + formId;
            this.history = [];
            this.currentIndex = -1;
            this.isRestoring = false;
            this.suppressObserverSnapshots = false;
            this.mutationObservers = [];
            
            this.init();
        }

        /**
         * Initialize undo/redo manager
         */
        init() {
            // Load history from localStorage
            this.loadHistory();
            
            // Create undo/redo controls
            this.createControls();
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();

            // Observe dynamic row containers (formsets)
            this.setupDynamicObservers();
            
            // Update UI state
            this.updateUI();
        }

        /**
         * Load history from localStorage
         */
        loadHistory() {
            try {
                const stored = localStorage.getItem(this.historyKey);
                if (stored) {
                    const data = JSON.parse(stored);
                    this.history = data.history || [];
                    this.currentIndex = typeof data.currentIndex === 'number' ? data.currentIndex : -1;
                }
            } catch (e) {
                console.warn('Failed to load undo/redo history:', e);
                this.history = [];
                this.currentIndex = -1;
            }
        }

        /**
         * Save history to localStorage
         */
        saveHistory() {
            try {
                localStorage.setItem(this.historyKey, JSON.stringify({
                    history: this.history,
                    currentIndex: this.currentIndex
                }));
            } catch (e) {
                console.warn('Failed to save undo/redo history:', e);
            }
        }

        /**
         * Push a new state to history
         */
        pushState(state, description = 'Change') {
            if (this.isRestoring) return;

            // Remove any states after current index (redo states)
            this.history = this.history.slice(0, this.currentIndex + 1);

            // Add new state
            this.history.push({
                state: state,
                description: description,
                timestamp: Date.now()
            });

            // Limit history size
            if (this.history.length > MAX_HISTORY_SIZE) {
                this.history = this.history.slice(-MAX_HISTORY_SIZE);
            }

            this.currentIndex = this.history.length - 1;
            this.saveHistory();
            this.updateUI();
        }

        /**
         * Undo to previous state
         */
        undo() {
            if (!this.canUndo()) return false;

            this.currentIndex--;
            const previousState = this.history[this.currentIndex];
            this.restoreState(previousState.state);
            this.updateUI();

            // Show toast notification
            if (typeof showToast === 'function') {
                showToast(`Undone: ${previousState.description}`, 'info', 2000);
            }

            return true;
        }

        /**
         * Redo to next state
         */
        redo() {
            if (!this.canRedo()) return false;

            this.currentIndex++;
            const nextState = this.history[this.currentIndex];
            this.restoreState(nextState.state);
            this.updateUI();

            // Show toast notification
            if (typeof showToast === 'function') {
                showToast(`Redone: ${nextState.description}`, 'info', 2000);
            }

            return true;
        }

        /**
         * Check if undo is available
         */
        canUndo() {
            return this.currentIndex > 0;
        }

        /**
         * Check if redo is available
         */
        canRedo() {
            return this.currentIndex < this.history.length - 1;
        }

        /**
         * Restore a state to the form
         */
        restoreState(state) {
            this.isRestoring = true;
            this.suppressObserverSnapshots = true;

            // Restore dynamic formset container HTML first (if configured).
            if (state.__undoContainers && typeof state.__undoContainers === 'object') {
                Object.entries(state.__undoContainers).forEach(([containerId, html]) => {
                    const container = document.getElementById(containerId);
                    if (container) {
                        container.innerHTML = html;
                    }
                });
            }

            // Restore form values
            Object.keys(state).forEach(key => {
                if (key === '__undoContainers') return;

                const element = document.querySelector(`[name="${key}"]`);
                if (element) {
                    if (element.type === 'checkbox' || element.type === 'radio') {
                        element.checked = state[key];
                    } else {
                        element.value = state[key];
                    }
                    
                    // Trigger change event for validation
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            this.isRestoring = false;

            // MutationObserver callbacks are async; keep snapshots suppressed briefly.
            setTimeout(() => {
                this.suppressObserverSnapshots = false;
            }, 100);
        }

        /**
         * Parse dynamic container ids from data-undo-containers attribute.
         */
        getDynamicContainerIds(form) {
            if (!form) return [];

            const raw = form.getAttribute('data-undo-containers');
            if (!raw) return [];

            return raw
                .split(',')
                .map(item => item.trim())
                .filter(Boolean);
        }

        /**
         * Observe dynamic containers for add/remove row changes.
         */
        setupDynamicObservers() {
            const form = document.getElementById(this.formId);
            if (!form) return;

            const containerIds = this.getDynamicContainerIds(form);
            if (!containerIds.length) return;

            let observerDebounce;

            containerIds.forEach(containerId => {
                const container = document.getElementById(containerId);
                if (!container) return;

                const observer = new MutationObserver((mutations) => {
                    const hasStructureChange = mutations.some(m => m.type === 'childList');
                    if (!hasStructureChange) return;
                    if (this.isRestoring || this.suppressObserverSnapshots) return;

                    clearTimeout(observerDebounce);
                    observerDebounce = setTimeout(() => {
                        this.snapshot('Updated form rows');
                    }, 250);
                });

                observer.observe(container, { childList: true });
                this.mutationObservers.push(observer);
            });
        }

        /**
         * Create undo/redo control buttons
         */
        createControls() {
            const form = document.getElementById(this.formId);
            if (!form) return;

            // Check if controls already exist
            if (document.getElementById('undoRedoControls')) return;

            const controlsDiv = document.createElement('div');
            controlsDiv.id = 'undoRedoControls';
            controlsDiv.className = 'undo-redo-controls';
            controlsDiv.innerHTML = `
                <div class="undo-redo-buttons">
                    <button type="button" id="undoBtn" class="undo-btn" title="Undo (Ctrl+Z)" disabled>
                        <span class="btn-icon">↶</span>
                        <span class="btn-label">Undo</span>
                    </button>
                    <button type="button" id="redoBtn" class="redo-btn" title="Redo (Ctrl+Y)" disabled>
                        <span class="btn-icon">↷</span>
                        <span class="btn-label">Redo</span>
                    </button>
                    <div class="history-info">
                        <span id="historyPosition"></span>
                    </div>
                </div>
            `;

            // Insert controls at the top of the form
            form.insertBefore(controlsDiv, form.firstChild);

            // Add event listeners
            document.getElementById('undoBtn').addEventListener('click', () => this.undo());
            document.getElementById('redoBtn').addEventListener('click', () => this.redo());
        }

        /**
         * Setup keyboard shortcuts
         */
        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl+Z for Undo
                if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
                    e.preventDefault();
                    this.undo();
                }
                // Ctrl+Y or Ctrl+Shift+Z for Redo
                else if ((e.ctrlKey && e.key === 'y') || (e.ctrlKey && e.shiftKey && e.key === 'z')) {
                    e.preventDefault();
                    this.redo();
                }
            });
        }

        /**
         * Update UI state (enable/disable buttons)
         */
        updateUI() {
            const undoBtn = document.getElementById('undoBtn');
            const redoBtn = document.getElementById('redoBtn');
            const historyPosition = document.getElementById('historyPosition');

            if (undoBtn) {
                undoBtn.disabled = !this.canUndo();
                if (this.canUndo()) {
                    const prevState = this.history[this.currentIndex - 1];
                    undoBtn.title = `Undo: ${prevState.description} (Ctrl+Z)`;
                } else {
                    undoBtn.title = 'Undo (Ctrl+Z)';
                }
            }

            if (redoBtn) {
                redoBtn.disabled = !this.canRedo();
                if (this.canRedo()) {
                    const nextState = this.history[this.currentIndex + 1];
                    redoBtn.title = `Redo: ${nextState.description} (Ctrl+Y)`;
                } else {
                    redoBtn.title = 'Redo (Ctrl+Y)';
                }
            }

            if (historyPosition && this.history.length > 0) {
                historyPosition.textContent = `${this.currentIndex + 1}/${this.history.length}`;
            } else if (historyPosition) {
                historyPosition.textContent = '';
            }
        }

        /**
         * Clear all history
         */
        clearHistory() {
            this.history = [];
            this.currentIndex = -1;
            this.saveHistory();
            this.updateUI();
        }

        /**
         * Get current state from form
         */
        getCurrentState() {
            const form = document.getElementById(this.formId);
            if (!form) return {};

            const state = {};
            const formData = new FormData(form);

            for (const [key, value] of formData.entries()) {
                state[key] = value;
            }

            // Handle checkboxes separately (they're not in formData when unchecked)
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => {
                state[cb.name] = cb.checked;
            });

            // Include dynamic formset container structure so undo can restore added/removed rows.
            const dynamicContainerIds = this.getDynamicContainerIds(form);
            if (dynamicContainerIds.length) {
                state.__undoContainers = {};
                dynamicContainerIds.forEach(containerId => {
                    const container = document.getElementById(containerId);
                    if (container) {
                        state.__undoContainers[containerId] = container.innerHTML;
                    }
                });
            }

            return state;
        }

        /**
         * Take a snapshot of current form state
         */
        snapshot(description = 'Form change') {
            const state = this.getCurrentState();
            this.pushState(state, description);
        }
    }

    /**
     * Initialize undo/redo for forms with data-undo-redo attribute
     */
    function initUndoRedo() {
        document.addEventListener('DOMContentLoaded', function() {
            const forms = document.querySelectorAll('[data-undo-redo="true"]');
            
            forms.forEach(form => {
                const formId = form.id;
                if (!formId) {
                    console.warn('Form needs an ID for undo/redo:', form);
                    return;
                }

                const manager = new UndoRedoManager(formId);
                
                // Store manager reference on form
                form.undoRedoManager = manager;

                // Take initial snapshot
                setTimeout(() => {
                    manager.snapshot('Initial state');
                }, 500);

                // Track changes with debounce
                let changeTimeout;
                form.addEventListener('change', function(e) {
                    clearTimeout(changeTimeout);
                    changeTimeout = setTimeout(() => {
                        const fieldName = e.target.name || 'field';
                        manager.snapshot(`Changed ${fieldName}`);
                    }, 1000);
                });
            });
        });
    }

    // Auto-initialize
    initUndoRedo();

    // Expose API
    window.UndoRedoManager = UndoRedoManager;

})();

console.log('Undo/Redo Manager loaded');
