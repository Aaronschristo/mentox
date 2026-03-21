// Toast Notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'bx-check-circle' : 'bx-x-circle';
    const color = type === 'success' ? 'var(--success)' : 'var(--danger)';
    
    toast.innerHTML = `
        <i class='bx ${icon}' style='font-size: 24px; color: ${color}'></i>
        <div style="font-weight: 500;">${message}</div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Modal Handle
function toggleModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = modal.style.display === 'flex' ? 'none' : 'flex';
    }
}

// Download QR
function downloadQR() {
    const img = document.getElementById('qr-image');
    if(img.src) {
        let a = document.createElement('a');
        a.href = img.src;
        a.download = `QR_${document.getElementById('qr-customer-name').innerText}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// Formatting
const formatCurrency = (val) => '₹' + parseFloat(val).toFixed(2);

// Theme Toggle
function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if(isDark) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        document.getElementById('theme-toggle-icon').className = 'bx bx-moon';
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        document.getElementById('theme-toggle-icon').className = 'bx bx-sun';
    }
}

// Load theme icon on load
document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem('theme');
    const icon = document.getElementById('theme-toggle-icon');
    if(savedTheme === 'dark' && icon) {
        icon.className = 'bx bx-sun';
    }
});

// Global customers cache for autocomplete
window.allCustomers = [];

// API Interactions & Page Loaders
document.addEventListener('DOMContentLoaded', () => {
    
    // Sidebar Toggle
    const sidebar = document.querySelector(".sidebar");
    const sidebarBtn = document.querySelector(".sidebarBtn");
    
    if(sidebarBtn) {
        sidebarBtn.addEventListener("click", () => {
            sidebar.classList.toggle("active");
        });
    }

    // Dashboard Stats
    if(document.getElementById('total-customers')) {
        loadDashboardStats();
    }
    
    // Customers Table
    if(document.getElementById('customers-table-body')) {
        loadCustomers();
    }

    // Recharge Autocomplete
    if(document.getElementById('recharge-customer-name')) {
        setupRechargeAutocomplete();
    }
});

function setupRechargeAutocomplete() {
    fetch('/api/customers')
        .then(res => res.json())
        .then(data => {
            window.allCustomers = data;
        });

    const nameInput = document.getElementById('recharge-customer-name');
    const idInput = document.getElementById('recharge-customer-id');
    const autocompleteList = document.getElementById('customer-autocomplete-list');

    if(!nameInput) return;

    nameInput.addEventListener('input', function() {
        const val = this.value.toLowerCase();
        autocompleteList.innerHTML = '';
        if (!val) {
            autocompleteList.style.display = 'none';
            // Also blank out the ID
            idInput.value = '';
            return;
        }

        let hasMatches = false;
        window.allCustomers.forEach(c => {
            if (c.name.toLowerCase().includes(val)) {
                hasMatches = true;
                const div = document.createElement('div');
                div.style.padding = '10px 15px';
                div.style.cursor = 'pointer';
                div.style.borderBottom = '1px solid #e2e8f0';
                div.style.color = 'var(--text-dark)';
                div.innerHTML = `<strong>${c.name}</strong> <small style="color: var(--text-light); float: right;">${c.id.substring(0,8)}...</small>`;
                
                div.addEventListener('click', function() {
                    nameInput.value = c.name;
                    idInput.value = c.id;
                    autocompleteList.style.display = 'none';
                });
                
                div.addEventListener('mouseenter', function() {
                    this.style.background = 'var(--secondary-color)';
                });
                div.addEventListener('mouseleave', function() {
                    this.style.background = 'transparent';
                });

                autocompleteList.appendChild(div);
            }
        });

        if (hasMatches) {
            autocompleteList.style.display = 'block';
        } else {
            autocompleteList.style.display = 'none';
        }
    });

    // Close autocomplete when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target !== nameInput && e.target !== autocompleteList) {
            autocompleteList.style.display = 'none';
        }
    });
}

function loadDashboardStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            document.getElementById('total-customers').innerText = data.total_customers;
            document.getElementById('total-revenue').innerText = data.total_revenue.toFixed(2);
            
            const tbody = document.getElementById('transactions-table-body');
            tbody.innerHTML = '';
            
            if(data.recent_transactions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--text-light)">No recent transactions</td></tr>';
            } else {
                data.recent_transactions.forEach(tx => {
                    const isCheckin = tx.type === 'checkin';
                    const badgeClass = tx.type;
                    const amountDisplay = isCheckin ? `-₹${tx.amount.toFixed(2)}` : `+₹${tx.amount.toFixed(2)}`;
                    const amountColor = isCheckin ? 'var(--text-dark)' : 'var(--success)';
                    const icon = isCheckin ? 'bx-up-arrow-alt' : 'bx-down-arrow-alt';
                    const iconColor = isCheckin ? 'var(--danger)' : 'var(--success)';
                    tbody.innerHTML += `
                        <tr class="table-row">
                            <td>
                                <div class="user-info">
                                    <strong>${tx.customer_name}</strong>
                                </div>
                            </td>
                            <td><span class="badge ${badgeClass}">${tx.type}</span></td>
                            <td style="font-weight:600; color: ${amountColor};">
                                <div style="display:flex; align-items:center; gap: 4px;">
                                    <i class='bx ${icon}' style="color: ${iconColor}; font-size: 18px;"></i>
                                    ${amountDisplay}
                                </div>
                            </td>
                            <td class="text-light">${tx.created_at}</td>
                        </tr>
                    `;
                });
            }
        })
        .catch(err => console.error("Could not load stats", err));
}

function loadCustomers() {
    fetch('/api/customers')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('customers-table-body');
            tbody.innerHTML = '';
            
            if(data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color: var(--text-light)">No customers found</td></tr>';
            } else {
                data.forEach(c => {
                    tbody.innerHTML += `
                        <tr class="table-row">
                            <td>
                                <div class="user-info">
                                    <strong>${c.name}</strong>
                                    <span class="user-id-truncate" title="${c.id}">${c.id}</span>
                                </div>
                            </td>
                            <td style="font-weight:600; color:var(--text-dark)">${formatCurrency(c.balance)}</td>
                            <td class="text-light">${c.created_at}</td>
                            <td>
                                <button class="btn btn-amount" style="padding: 6px 12px; font-size: 13px;" onclick="showQR('${c.id}', '${c.name}')">
                                    <i class='bx bx-qr'></i> View
                                </button>
                            </td>
                        </tr>
                    `;
                });
            }
        });
}

function handleIssueQR(e) {
    e.preventDefault();
    const name = document.getElementById('customer-name').value;
    const balance = document.getElementById('initial-balance').value;
    
    fetch('/api/customers', {
        method: 'POST',
        headers : { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, initial_balance: balance })
    })
    .then(res => res.json().then(data => ({status: res.status, body: data})))
    .then(res => {
        if(res.status === 201) {
            showToast('Customer created successfully!');
            document.getElementById('issue-qr-form').reset();
            toggleModal('issueQrModal');
            loadCustomers();
            
            // Show the newly generated QR
            showQR(res.body.id, name);
        } else {
            showToast(res.body.error, 'error');
        }
    });
}

function showQR(id, name) {
    document.getElementById('qr-customer-name').innerText = name;
    document.getElementById('qr-customer-id').innerText = id;
    document.getElementById('qr-image').src = `/qrcode/${id}.png`;
    toggleModal('viewQrModal');
}

function handleRecharge(e) {
    e.preventDefault();
    const customer_id = document.getElementById('recharge-customer-id').value;
    const amount = document.getElementById('recharge-amount').value;
    
    fetch('/api/recharge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: customer_id, amount: amount })
    })
    .then(res => res.json().then(data => ({status: res.status, body: data})))
    .then(res => {
        if(res.status === 200) {
            showToast(`Recharge successful! New balance: ${formatCurrency(res.body.new_balance)}`);
            document.getElementById('recharge-form').reset();
        } else {
            showToast(res.body.error, 'error');
        }
    })
    .catch(err => {
        showToast('System Error', 'error');
    });
}


function handleAssignExistingQR(e) {
    e.preventDefault();
    const qr_id = document.getElementById('assign-qr-id').value;
    const name = document.getElementById('assign-customer-name').value;
    const balance = document.getElementById('assign-initial-balance').value;
    
    fetch('/api/customers', {
        method: 'POST',
        headers : { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, initial_balance: balance, qr_id: qr_id })
    })
    .then(res => res.json().then(data => ({status: res.status, body: data})))
    .then(res => {
        if(res.status === 201 || res.status === 200) {
            showToast('Existing QR assigned successfully!');
            document.getElementById('assign-qr-form').reset();
            closeAssignQRFlow();
            loadCustomers();
        } else {
            showToast(res.body.error, 'error');
        }
    });
}
