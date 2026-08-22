/**
 * Batch Operations Manager - Handles bulk actions on multiple items
 */

console.log('Batch.js loaded successfully');

(function() {
    'use strict';

    console.log('BatchManager IIFE executing');

    /**
     * BatchManager Class
     */
    class BatchManager {
        constructor(containerId, options = {}) {
            console.log(`Creating BatchManager for container: ${containerId}`);
            this.container = document.getElementById(containerId);
            if (!this.container) {
                console.warn(`Container #${containerId} not found`);
                return;
            }

            this.options = {
                itemSelector: options.itemSelector || '.batch-item',
                checkboxSelector: options.checkboxSelector || '.batch-checkbox',
                selectAllSelector: options.selectAllSelector || '#selectAll',
                deleteUrl: options.deleteUrl || '',
                itemType: options.itemType || 'items',
                onSelectionChange: options.onSelectionChange || null,
                csrfToken: options.csrfToken || this.getCSRFToken()
            };

            this.selectedItems = new Set();
            this.init();
        }

        /**
         * Initialize batch manager
         */
        init() {
            console.log(`Initializing BatchManager for ${this.container.id}`);
            this.setupEventListeners();
            this.createBatchControls();
            this.updateUI();
            console.log(`BatchManager initialized for ${this.container.id}`);
        }

        /**
         * Get CSRF token from cookie
         */
        getCSRFToken() {
            const name = 'csrftoken';
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

        /**
         * Setup event listeners
         */
        setupEventListeners() {
            // Select all checkbox
            const selectAll = document.querySelector(this.options.selectAllSelector);
            if (selectAll) {
                selectAll.addEventListener('change', (e) => this.handleSelectAll(e));
            }

            // Individual checkboxes
            const checkboxes = this.container.querySelectorAll(this.options.checkboxSelector);
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', (e) => this.handleCheckboxChange(e));
            });

            // Item rows (click to toggle)
            const items = this.container.querySelectorAll(this.options.itemSelector);
            items.forEach(item => {
                item.addEventListener('click', (e) => {
                    // Don't toggle if clicking on a button or link
                    if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || 
                        e.target.closest('button') || e.target.closest('a')) {
                        return;
                    }
                    const checkbox = item.querySelector(this.options.checkboxSelector);
                    if (checkbox && e.target !== checkbox) {
                        checkbox.checked = !checkbox.checked;
                        checkbox.dispatchEvent(new Event('change'));
                    }
                });
            });
        }

        /**
         * Create batch control buttons
         */
        createBatchControls() {
            // Create unique IDs based on container
            const containerId = this.container.id;
            const controlsId = `batchControls_${containerId}`;
            const deleteId = `batchDeleteBtn_${containerId}`;
            const deselectId = `batchDeselectBtn_${containerId}`;
            const infoId = `batchSelectionInfo_${containerId}`;
            
            // Check if controls already exist for this container
            if (document.getElementById(controlsId)) return;

            const controlsDiv = document.createElement('div');
            controlsDiv.id = controlsId;
            controlsDiv.className = 'batch-controls';
            controlsDiv.innerHTML = `
                <div class="batch-actions">
                    <button type="button" id="${deleteId}" class="batch-delete-btn" disabled>
                        <span class="btn-icon">🗑️</span>
                        <span class="btn-label">Delete Selected</span>
                        <span class="batch-count">(0)</span>
                    </button>
                    <button type="button" id="${deselectId}" class="batch-deselect-btn" disabled>
                        <span class="btn-icon">✕</span>
                        <span class="btn-label">Deselect All</span>
                    </button>
                </div>
                <div class="batch-info">
                    <span id="${infoId}"></span>
                </div>
            `;

            // Insert controls before the container
            this.container.parentNode.insertBefore(controlsDiv, this.container);

            // Add event listeners
            document.getElementById(deleteId).addEventListener('click', () => this.handleBatchDelete());
            document.getElementById(deselectId).addEventListener('click', () => this.deselectAll());
        }

        /**
         * Handle select all checkbox
         */
        handleSelectAll(e) {
            const isChecked = e.target.checked;
            const checkboxes = this.container.querySelectorAll(this.options.checkboxSelector);
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
                const itemId = checkbox.value;
                if (isChecked) {
                    this.selectedItems.add(itemId);
                } else {
                    this.selectedItems.delete(itemId);
                }
            });

            this.updateUI();
        }

        /**
         * Handle individual checkbox change
         */
        handleCheckboxChange(e) {
            const checkbox = e.target;
            const itemId = checkbox.value;

            if (checkbox.checked) {
                this.selectedItems.add(itemId);
            } else {
                this.selectedItems.delete(itemId);
            }

            // Update select all checkbox state
            this.updateSelectAllState();
            this.updateUI();
        }

        /**
         * Update select all checkbox state (checked/indeterminate)
         */
        updateSelectAllState() {
            const selectAll = document.querySelector(this.options.selectAllSelector);
            if (!selectAll) return;

            const checkboxes = this.container.querySelectorAll(this.options.checkboxSelector);
            const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;

            if (checkedCount === 0) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
            } else if (checkedCount === checkboxes.length) {
                selectAll.checked = true;
                selectAll.indeterminate = false;
            } else {
                selectAll.checked = false;
                selectAll.indeterminate = true;
            }
        }

        /**
         * Deselect all items
         */
        deselectAll() {
            const checkboxes = this.container.querySelectorAll(this.options.checkboxSelector);
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });

            const selectAll = document.querySelector(this.options.selectAllSelector);
            if (selectAll) {
                selectAll.checked = false;
                selectAll.indeterminate = false;
            }

            this.selectedItems.clear();
            this.updateUI();
        }

        /**
         * Update UI based on selection
         */
        updateUI() {
            const count = this.selectedItems.size;
            const containerId = this.container.id;
            console.log(`updateUI for ${containerId}: ${count} items selected`);
            const deleteBtn = document.getElementById(`batchDeleteBtn_${containerId}`);
            const deselectBtn = document.getElementById(`batchDeselectBtn_${containerId}`);
            const selectionInfo = document.getElementById(`batchSelectionInfo_${containerId}`);
            const controlsDiv = document.getElementById(`batchControls_${containerId}`);

            console.log(`Controls div found: ${controlsDiv ? 'yes' : 'no'}`);

            if (deleteBtn) {
                deleteBtn.disabled = count === 0;
                const batchCount = deleteBtn.querySelector('.batch-count');
                if (batchCount) {
                    batchCount.textContent = `(${count})`;
                }
            }

            if (deselectBtn) {
                deselectBtn.disabled = count === 0;
            }

            if (selectionInfo) {
                selectionInfo.textContent = count > 0 
                    ? `${count} ${this.options.itemType} selected` 
                    : '';
            }

            // Show/hide controls based on selection
            // Temporarily always show for debugging
            // if (controlsDiv) {
            //     controlsDiv.style.display = count > 0 ? 'flex' : 'none';
            //     console.log(`Set controls display to: ${controlsDiv.style.display}`);
            // }

            // Highlight selected rows
            const items = this.container.querySelectorAll(this.options.itemSelector);
            items.forEach(item => {
                const checkbox = item.querySelector(this.options.checkboxSelector);
                if (checkbox && checkbox.checked) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            });

            // Call custom callback
            if (this.options.onSelectionChange) {
                this.options.onSelectionChange(this.selectedItems);
            }
        }

        /**
         * Handle batch delete
         */
        async handleBatchDelete() {
            if (this.selectedItems.size === 0) return;

            const count = this.selectedItems.size;
            const itemType = this.options.itemType;

            // Show confirmation modal
            const confirmed = await this.showConfirmModal(
                `Delete ${count} ${itemType}?`,
                `Are you sure you want to delete ${count} selected ${itemType}? This action cannot be undone.`
            );

            if (!confirmed) return;

            // Show loading
            if (typeof showLoading === 'function') {
                showLoading('Deleting...', `Deleting ${count} ${itemType}`);
            }

            try {
                const response = await fetch(this.options.deleteUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.options.csrfToken
                    },
                    body: JSON.stringify({
                        ids: Array.from(this.selectedItems)
                    })
                });

                if (typeof hideLoading === 'function') {
                    hideLoading();
                }

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();

                if (result.success) {
                    // Show success message
                    if (typeof showToast === 'function') {
                        showToast(`Successfully deleted ${result.deleted_count} ${itemType}`, 'success');
                    }

                    // Remove deleted items from DOM
                    this.selectedItems.forEach(itemId => {
                        const checkbox = this.container.querySelector(`${this.options.checkboxSelector}[value="${itemId}"]`);
                        if (checkbox) {
                            const item = checkbox.closest(this.options.itemSelector);
                            if (item) {
                                item.style.opacity = '0';
                                setTimeout(() => item.remove(), 300);
                            }
                        }
                    });

                    this.selectedItems.clear();
                    this.updateUI();

                    // Reload page after animation
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    throw new Error(result.message || 'Delete failed');
                }
            } catch (error) {
                if (typeof hideLoading === 'function') {
                    hideLoading();
                }
                if (typeof showToast === 'function') {
                    showToast(`Error deleting ${itemType}: ${error.message}`, 'error');
                }
                console.error('Batch delete error:', error);
            }
        }

        /**
         * Show confirmation modal
         */
        showConfirmModal(title, message) {
            return new Promise((resolve) => {
                // Use existing modal if available
                if (typeof showConfirmModal === 'function') {
                    showConfirmModal(message, (confirmed) => {
                        resolve(confirmed);
                    });
                    return;
                }

                // Fallback to native confirm
                resolve(confirm(`${title}\n\n${message}`));
            });
        }

        /**
         * Get selected item IDs
         */
        getSelectedItems() {
            return Array.from(this.selectedItems);
        }

        /**
         * Get selection count
         */
        getSelectionCount() {
            return this.selectedItems.size;
        }
    }

    // Expose API
    window.BatchManager = BatchManager;

})();

console.log('Batch Operations Manager loaded');
