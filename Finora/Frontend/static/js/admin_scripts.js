// Admin Panel JavaScript Functions

// Initialize DataTable
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any data tables if they exist
    if (document.getElementById('dataTable')) {
        initializeDataTable();
    }
    if (document.getElementById('usersTable')) {
        initializeUsersTable();
    }
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// DataTable initialization
function initializeDataTable() {
    // Add any DataTable specific initialization here
    console.log('DataTable initialized');
}

function initializeUsersTable() {
    // Add any users table specific initialization here
    console.log('Users table initialized');
}

// Send Password Function
function sendPassword(userId) {
    if (confirm('Are you sure you want to send a password reset email to this user?')) {
        // Show loading state
        const button = event.target.closest('button');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Sending...';
        button.disabled = true;
        
        // Make AJAX request
        fetch(`/admin/send-password/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Password reset email sent successfully!', 'success');
            } else {
                showAlert('Error sending password reset email: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            showAlert('Error sending password reset email: ' + error, 'danger');
        })
        .finally(() => {
            // Reset button state
            button.innerHTML = originalText;
            button.disabled = false;
        });
    }
}

// View Rules Function
function viewRules(userId) {
    // Redirect to approval rules page with user pre-selected
    window.location.href = `/admin/approval-rules/?user=${userId}`;
}

// Edit User Function
function editUser(userId) {
    // Open edit modal or redirect to edit page
    console.log('Edit user:', userId);
    // Implementation for edit user functionality
}

// Delete User Function
function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        // Show loading state
        const button = event.target.closest('button');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Deleting...';
        button.disabled = true;
        
        // Make AJAX request
        fetch(`/admin/delete-user/${userId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('User deleted successfully!', 'success');
                // Remove row from table
                button.closest('tr').remove();
            } else {
                showAlert('Error deleting user: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            showAlert('Error deleting user: ' + error, 'danger');
        })
        .finally(() => {
            // Reset button state
            button.innerHTML = originalText;
            button.disabled = false;
        });
    }
}

// Load User Rules
function loadUserRules() {
    const userId = document.getElementById('userSelect').value;
    if (userId) {
        // Show the rules form
        document.getElementById('rulesForm').style.display = 'block';
        document.getElementById('selectedUserId').value = userId;
        
        // Load existing rules for this user
        loadExistingRules(userId);
        
        // Set the manager for this user
        setUserManager(userId);
    } else {
        document.getElementById('rulesForm').style.display = 'none';
        document.getElementById('existingRules').style.display = 'none';
    }
}

// Load Existing Rules
function loadExistingRules(userId) {
    fetch(`/admin/get-user-rules/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.rules) {
                displayExistingRules(data.rules);
                document.getElementById('existingRules').style.display = 'block';
            } else {
                document.getElementById('existingRules').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error loading rules:', error);
        });
}

// Display Existing Rules
function displayExistingRules(rules) {
    const tbody = document.getElementById('rulesTableBody');
    tbody.innerHTML = '';
    
    rules.forEach(rule => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${rule.description}</td>
            <td>${rule.manager_name}</td>
            <td><span class="badge bg-${rule.manager_approval ? 'success' : 'secondary'}">${rule.manager_approval ? 'Yes' : 'No'}</span></td>
            <td>${rule.approvers.map(a => a.name).join(', ')}</td>
            <td><span class="badge bg-${rule.approval_sequence ? 'info' : 'secondary'}">${rule.approval_sequence ? 'Sequential' : 'Parallel'}</span></td>
            <td>${rule.min_approval_percentage}%</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editRule(${rule.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteRule(${rule.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Set User Manager
function setUserManager(userId) {
    fetch(`/admin/get-user-manager/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.manager_id) {
                document.getElementById('manager').value = data.manager_id;
            }
        })
        .catch(error => {
            console.error('Error loading manager:', error);
        });
}

// Add Approver
function addApprover() {
    const tbody = document.getElementById('approversTable');
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>
            <select class="form-select" name="approver_ids">
                <option value="">Select Approver</option>
                ${getApproversOptions()}
            </select>
        </td>
        <td>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" name="approver_required">
            </div>
        </td>
        <td>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeApprover(this)">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    tbody.appendChild(row);
}

// Remove Approver
function removeApprover(button) {
    button.closest('tr').remove();
}

// Get Approvers Options
function getApproversOptions() {
    // This would typically be populated from a server response
    // For now, we'll use a placeholder
    return `
        <option value="1">John Doe</option>
        <option value="2">Jane Smith</option>
        <option value="3">Bob Johnson</option>
    `;
}

// Reset Form
function resetForm() {
    document.getElementById('rulesForm').reset();
    document.getElementById('approversTable').innerHTML = '';
    document.getElementById('existingRules').style.display = 'none';
}

// Edit Rule
function editRule(ruleId) {
    console.log('Edit rule:', ruleId);
    // Implementation for editing rules
}

// Delete Rule
function deleteRule(ruleId) {
    if (confirm('Are you sure you want to delete this approval rule?')) {
        fetch(`/admin/delete-rule/${ruleId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Rule deleted successfully!', 'success');
                loadUserRules(); // Reload rules
            } else {
                showAlert('Error deleting rule: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            showAlert('Error deleting rule: ' + error, 'danger');
        });
    }
}

// Show Alert
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of main content
    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Get CSRF Token
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

// Sidebar Toggle for Mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebarMenu');
    sidebar.classList.toggle('show');
}

// Search Functionality
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                found = true;
                break;
            }
        }
        
        row.style.display = found ? '' : 'none';
    }
}

// Export Functions
function exportToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    let csv = [];
    
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const cols = row.querySelectorAll('td, th');
        let rowData = [];
        
        for (let j = 0; j < cols.length; j++) {
            let cellText = cols[j].textContent.trim();
            // Remove action buttons text
            if (cellText.includes('Send Password') || cellText.includes('Rules') || cellText.includes('Edit') || cellText.includes('Delete')) {
                cellText = '';
            }
            rowData.push('"' + cellText + '"');
        }
        
        csv.push(rowData.join(','));
    }
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here
    console.log('Admin panel initialized');
});
