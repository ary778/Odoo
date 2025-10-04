document.addEventListener('DOMContentLoaded', () => {
    // --- GLOBAL ELEMENTS & STATE ---
    const app = document.getElementById('app');
    const loader = document.getElementById('loader');
    const toast = document.getElementById('toast');
    const modal = document.getElementById('modal');
    const State = { currentUser: null, workflows: [] };

    // --- UI HELPER FUNCTIONS ---
    const showLoader = () => loader.classList.remove('hidden');
    const hideLoader = () => loader.classList.add('hidden');
    const showToast = (message, type = 'success') => {
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        setTimeout(() => toast.classList.remove('show'), 3000);
    };
    const showModal = (content) => {
        document.getElementById('modal-body').innerHTML = content;
        modal.classList.remove('hidden');
    };
    const hideModal = () => modal.classList.add('hidden');

    // --- THE APP OBJECT (CONTROLLER) ---
    const App = {
        init() {
            // Setup event listeners
            window.addEventListener('hashchange', () => this.router());
            document.body.addEventListener('submit', (e) => this.handleFormSubmit(e));
            
            // THE FIX: Use .bind(this) to permanently lock the context of 'this'
            document.body.addEventListener('click', this.handleGlobalClick.bind(this));
            
            this.router(); // Initial page load
        },

        async router() {
            const hash = window.location.hash || '#login';
            const token = localStorage.getItem('accessToken');
            
            if (token && hash !== '#login' && hash !== '#signup') {
                app.className = 'dashboard-mode';
                if (!State.currentUser) this.loadUserFromToken();

                if (State.currentUser.role !== 'employee' && (hash === '#dashboard' || hash === '')) {
                    const newHash = '#approvals';
                    if (window.location.hash !== newHash) {
                        window.location.hash = newHash;
                        return; // The hash change will trigger the router again
                    }
                }
                
                await this.renderDashboardLayout(hash);
            } else {
                app.className = 'auth-mode';
                State.currentUser = null;
                localStorage.clear();
                this.renderAuth(hash);
            }
        },

        loadUserFromToken() {
            const token = localStorage.getItem('accessToken');
            if (token) {
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    State.currentUser = { username: payload.username, role: payload.role };
                } catch (e) {
                    console.error("Invalid token:", e);
                    localStorage.clear();
                    window.location.hash = '#login';
                }
            }
        },

        renderAuth(hash) {
            let template;
            if (hash === '#signup') {
                template = `
                <div class="auth-container">
                    <h2>Create Company Account</h2>
                    <p>This will create your company and the first admin user.</p>
                    <form id="signup-form">
                        <div class="form-group"><label for="signup-company">Company Name</label><input type="text" id="signup-company" required></div>
                        <div class="form-group"><label for="signup-currency">Default Currency (e.g., USD)</label><input type="text" id="signup-currency" maxlength="3" required></div>
                        <div class="form-group"><label for="signup-username">Admin Username</label><input type="text" id="signup-username" required></div>
                        <div class="form-group"><label for="signup-email">Admin Email</label><input type="email" id="signup-email" required></div>
                        <div class="form-group"><label for="signup-password">Password</label><input type="password" id="signup-password" required></div>
                        <button type="submit" class="button-primary">Create Account</button>
                        <p class="form-switch">Already have an account? <a href="#login">Log In</a></p>
                    </form>
                </div>`;
            } else {
                template = `
                <div class="auth-container">
                    <h2>Welcome Back</h2>
                    <p>Login to access your dashboard.</p>
                    <form id="login-form">
                        <div class="form-group"><label for="login-username">Username</label><input type="text" id="login-username" required></div>
                        <div class="form-group"><label for="login-password">Password</label><input type="password" id="login-password" required></div>
                        <button type="submit" class="button-primary">Login</button>
                        <p class="form-switch">No account? <a href="#signup">Sign Up</a></p>
                    </form>
                </div>`;
            }
            app.innerHTML = template;
        },

        async renderDashboardLayout(hash) {
            app.innerHTML = `
            <div class="dashboard-layout">
                <aside class="sidebar">
                    <h2 class="sidebar-logo">E</h2>
                    <nav class="sidebar-nav"></nav>
                    <button id="logout-btn" class="nav-link" title="Logout"><svg class="icon"><use href="#icon-logout"></use></svg></button>
                </aside>
                <main class="main-content">
                    <header class="main-header"><h1 id="page-title"></h1></header>
                    <div id="page-content" class="page-content"></div>
                </main>
            </div>`;
            await this.renderNav(hash);
            await this.renderDashboardPage(hash.substring(1));
        },

        async renderNav(currentHash) {
            const nav = document.querySelector('.sidebar-nav');
            if (!State.currentUser) this.loadUserFromToken();
            const { role } = State.currentUser;
            
            let links = [];
            if (role === 'employee') {
                links.push({ hash: '#dashboard', icon: 'icon-dashboard', title: 'Dashboard' });
                links.push({ hash: '#expenses', icon: 'icon-expenses', title: 'My Expenses' });
            } else {
                links.push({ hash: '#approvals', icon: 'icon-approvals', title: 'Approvals' });
            }
            if (role === 'admin') {
                links.push({ hash: '#users', icon: 'icon-users', title: 'Manage Users' });
            }
            
            nav.innerHTML = links.map(l => `<a href="${l.hash}" class="nav-link ${currentHash === l.hash ? 'active' : ''}" title="${l.title}"><svg class="icon"><use href="#${l.icon}"></use></svg></a>`).join('');
        },

        async renderDashboardPage(page) {
            const content = document.getElementById('page-content');
            const title = document.getElementById('page-title');
            content.innerHTML = `<div class="spinner"></div>`;

            try {
                if (page === 'expenses' && State.currentUser.role === 'employee') {
                    title.textContent = 'My Expenses';
                    const data = await expenses.getAll();
                    const tableRows = data.map(exp => `
                        <tr>
                            <td>${exp.description}</td>
                            <td>${exp.amount} ${exp.currency}</td>
                            <td><span class="status-badge status-${exp.status.replace('_','')}">${exp.status}</span></td>
                            <td>${new Date(exp.created_at).toLocaleDateString()}</td>
                        </tr>`).join('');
                    content.innerHTML = `
                        <div class="page-content-header"><h2>All My Expenses</h2><button class="button-primary" id="new-expense-btn">New Expense</button></div>
                        <div class="table-wrapper"><table><thead><tr><th>Description</th><th>Amount</th><th>Status</th><th>Created</th></tr></thead><tbody>${tableRows}</tbody></table></div>`;
                    if (!data.length) content.querySelector('tbody').innerHTML = `<tr><td colspan="4"><div class="empty-state"><p>No expenses found. Click 'New Expense' to start.</p></div></td></tr>`;
                } else if (page === 'approvals' && (State.currentUser.role === 'manager' || State.currentUser.role === 'admin')) {
                    if (State.currentUser.username.toLowerCase().includes('cfo')) { title.textContent = 'Chief Officer Portal'; } 
                    else { title.textContent = 'Team Approvals'; }
                    const data = await approvals.getAll();
                    const pending = data.filter(a => a.status === 'pending');
                    const tableRows = pending.map(appr => `
                        <tr>
                            <td>${appr.expense.employee.username}</td>
                            <td>${appr.expense.description}</td>
                            <td>${appr.expense.amount} ${appr.expense.currency}</td>
                            <td>
                                <button class="button-primary button-success approve-btn" data-id="${appr.id}">Approve</button>
                                <button class="button-primary button-danger reject-btn" data-id="${appr.id}">Reject</button>
                            </td>
                        </tr>`).join('');
                    content.innerHTML = `<div class="page-content-header"><h2>Pending Approvals</h2></div><div class="table-wrapper"><table><thead><tr><th>Employee</th><th>Description</th><th>Amount</th><th>Actions</th></tr></thead><tbody>${tableRows}</tbody></table></div>`;
                    if (!pending.length) content.innerHTML = `<div class="page-content-header"><h2>Pending Approvals</h2></div><div class="empty-state"><p>No pending approvals. Great job!</p></div>`;
                } else if (page === 'users' && State.currentUser.role === 'admin') {
                    title.textContent = 'User Management';
                    const data = await users.getAll();
                    const tableRows = data.map(user => `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.first_name || ''} ${user.last_name || ''}</td>
                            <td>${user.email}</td>
                            <td><span class="status-badge status-pending">${user.role}</span></td>
                        </tr>`).join('');
                    content.innerHTML = `<div class="page-content-header"><h2>Company Users</h2><button class="button-primary" id="new-user-btn">Add User</button></div>
                    <div class="table-wrapper"><table><thead><tr><th>Username</th><th>Name</th><th>Email</th><th>Role</th></tr></thead><tbody>${tableRows}</tbody></table></div>`;
                } else {
                    title.textContent = 'Dashboard';
                    content.innerHTML = `<h2>Welcome, ${State.currentUser.username}!</h2><p>Select an option from the sidebar to get started.</p>`;
                }
            } catch (error) {
                showToast(error.message, 'error');
                content.innerHTML = `<div class="empty-state"><p>Failed to load data. Please try again.</p></div>`;
            }
        },

        async renderNewExpenseModal() {
            showLoader();
            try {
                // Fetch workflows dynamically for the modal
                const workflows = await apiFetch('/workflows/');
                const workflowOptions = workflows.map(wf => `<option value="${wf.id}">${wf.name}</option>`).join('');
                showModal(`
                    <div class="modal-form-container">
                        <h2>New Expense</h2>
                        <form id="expense-form">
                            <div class="form-group"><label for="exp-desc">Description</label><input type="text" id="exp-desc" required></div>
                            <div class="form-group"><label for="exp-amount">Amount</label><input type="number" step="0.01" id="exp-amount" required></div>
                            <div class="form-group"><label for="exp-category">Category</label><input type="text" id="exp-category" required></div>
                            <div class="form-group"><label for="exp-currency">Currency</label><input type="text" id="exp-currency" required maxlength="3" placeholder="e.g., USD"></div>
                            <div class="form-group"><label for="exp-workflow">Approval Workflow (Optional)</label><select id="exp-workflow"><option value="">Default (Manager Only)</option>${workflowOptions}</select></div>
                            <button type="submit" class="button-primary">Submit Expense</button>
                        </form>
                    </div>`);
            } catch (error) { showToast('Could not load workflows.', 'error'); } 
            finally { hideLoader(); }
        },
        
        renderNewUserModal() {
            showModal(`
                <div class="modal-form-container">
                    <h2>Create New User</h2>
                    <form id="user-form">
                        <div class="form-group"><label for="user-username">Username</label><input type="text" id="user-username" required></div>
                        <div class="form-group"><label for="user-password">Password</label><input type="password" id="user-password" required></div>
                        <div class="form-group"><label for="user-email">Email</label><input type="email" id="user-email" required></div>
                        <div class="form-group">
                            <label for="user-role">Role</label>
                            <select id="user-role"><option value="employee">Employee</option><option value="manager">Manager</option></select>
                        </div>
                        <button type="submit" class="button-primary">Create User</button>
                    </form>
                </div>`);
        },

        async handleGlobalClick(e) {
            const target = e.target;
            if (target.matches('.modal-close-btn') || target.matches('.modal-overlay')) { hideModal(); return; }
            if (target.closest('#logout-btn')) { window.location.hash = '#login'; return; }
            if (target.closest('.nav-link')) { return; } // Let the hashchange event handle navigation
            if (target.id === 'new-expense-btn') { this.renderNewExpenseModal(); return; }
            if (target.id === 'new-user-btn') { this.renderNewUserModal(); return; }

            const approvalId = target.dataset.id;
            if (target.classList.contains('approve-btn')) {
                showLoader();
                try {
                    await approvals.act(approvalId, 'approved', 'Approved via web UI.');
                    showToast('Expense Approved!');
                    await this.renderDashboardPage('approvals');
                } catch (error) { showToast(error.message, 'error'); }
                finally { hideLoader(); }
            } else if (target.classList.contains('reject-btn')) {
                const comment = prompt("Please provide a reason for rejection:");
                if (comment) {
                    showLoader();
                    try {
                        await approvals.act(approvalId, 'rejected', comment);
                        showToast('Expense Rejected!');
                        await this.renderDashboardPage('approvals');
                    } catch (error) { showToast(error.message, 'error'); }
                    finally { hideLoader(); }
                }
            }
        },

        async handleFormSubmit(e) {
            e.preventDefault();
            const formId = e.target.id;
            showLoader();
            try {
                if (formId === 'login-form') {
                    const data = await auth.login(e.target.querySelector('#login-username').value, e.target.querySelector('#login-password').value);
                    localStorage.setItem('accessToken', data.access);
                    this.loadUserFromToken(); // Load user right after login
                    window.location.hash = State.currentUser.role === 'employee' ? '#dashboard' : '#approvals';
                    showToast('Login successful!');
                } else if (formId === 'signup-form') {
                    const data = {
                        company_name: e.target.querySelector('#signup-company').value, default_currency: e.target.querySelector('#signup-currency').value,
                        username: e.target.querySelector('#signup-username').value, email: e.target.querySelector('#signup-email').value,
                        password: e.target.querySelector('#signup-password').value, first_name: 'Admin', last_name: 'User'
                    };
                    await auth.signup(data);
                    showToast('Signup successful! Please log in.');
                    window.location.hash = '#login';
                } else if (formId === 'expense-form') {
                    const expenseData = {
                        description: document.getElementById('exp-desc').value,
                        amount: document.getElementById('exp-amount').value,
                        category: document.getElementById('exp-category').value,
                        currency: document.getElementById('exp-currency').value,
                    };
                    const workflowId = document.getElementById('exp-workflow').value;
                    if (workflowId) { expenseData.workflow = workflowId; }
                    
                    await expenses.create(expenseData);
                    hideModal();
                    showToast('Expense submitted!');
                    await this.renderDashboardPage('expenses');
                } else if (formId === 'user-form') {
                    const data = {
                        username: e.target.querySelector('#user-username').value, password: e.target.querySelector('#user-password').value,
                        email: e.target.querySelector('#user-email').value, role: e.target.querySelector('#user-role').value
                    };
                    await users.create(data);
                    hideModal();
                    showToast('User created successfully!');
                    await this.renderDashboardPage('users');
                }
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                hideLoader();
            }
        }
    };

    App.init();
});