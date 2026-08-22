/**
 * Simple Batch Operations - Works directly with tables
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all tables with batch-table class
    const tables = document.querySelectorAll('.batch-table');
    
    tables.forEach(table => {
        initBatchOperations(table);
    });
});

function initBatchOperations(table) {
    const tableId = table.id;
    const selectAllCheckbox = table.querySelector('thead input[type="checkbox"]');
    const itemCheckboxes = table.querySelectorAll('tbody .batch-checkbox');
    
    if (!selectAllCheckbox || itemCheckboxes.length === 0) {
        return; // No checkboxes found
    }
    
    // Create batch controls div
    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'batch-controls';
    controlsDiv.id = `controls_${tableId}`;
    controlsDiv.style.display = 'none';
    controlsDiv.innerHTML = `
        <div class="batch-actions">
            <button type="button" class="batch-delete-btn">
                🗑️ Delete Selected <span class="count">(0)</span>
            </button>
            <button type="button" class="batch-clear-btn">
                ✕ Clear Selection
            </button>
        </div>
    `;
    
    // Insert before table
    table.parentNode.insertBefore(controlsDiv, table);
    
    const deleteBtn = controlsDiv.querySelector('.batch-delete-btn');
    const clearBtn = controlsDiv.querySelector('.batch-clear-btn');
    const countSpan = controlsDiv.querySelector('.count');
    
    // Update UI function
    function updateUI() {
        const checkedBoxes = Array.from(itemCheckboxes).filter(cb => cb.checked);
        const count = checkedBoxes.length;
        
        countSpan.textContent = `(${count})`;
        controlsDiv.style.display = count > 0 ? 'flex' : 'none';
        
        // Update select all state
        if (count === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (count === itemCheckboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
        
        // Highlight selected rows
        itemCheckboxes.forEach(cb => {
            const row = cb.closest('tr');
            if (cb.checked) {
                row.classList.add('selected');
            } else {
                row.classList.remove('selected');
            }
        });
    }
    
    // Select all handler
    selectAllCheckbox.addEventListener('change', function() {
        const isChecked = this.checked;
        itemCheckboxes.forEach(cb => {
            cb.checked = isChecked;
        });
        updateUI();
    });
    
    // Individual checkbox handlers
    itemCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateUI);
    });
    
    // Clear selection handler
    clearBtn.addEventListener('click', function() {
        itemCheckboxes.forEach(cb => {
            cb.checked = false;
        });
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        updateUI();
    });
    
    // Delete handler
    deleteBtn.addEventListener('click', function() {
        const checkedBoxes = Array.from(itemCheckboxes).filter(cb => cb.checked);
        const ids = checkedBoxes.map(cb => cb.value);
        
        if (ids.length === 0) return;
        
        if (confirm(`Delete ${ids.length} item(s)?`)) {
            // Get the delete URL from table data attribute or construct it
            const deleteUrl = table.dataset.deleteUrl;
            if (!deleteUrl) {
                alert('Delete URL not configured');
                return;
            }
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Send delete request
            fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ ids: ids })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload page to show updated data
                    location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Error deleting items: ' + error);
            });
        }
    });
    
    // Initial update
    updateUI();
}
