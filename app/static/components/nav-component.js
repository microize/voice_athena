/**
 * Navigation Component Loader
 * Creates a reusable navigation component system for Athena voice interview application
 */

// Global navigation component functions
window.NavComponent = {
    /**
     * Loads navigation component into specified container
     * @param {Object} config - Configuration object
     * @param {string} config.containerId - ID of container element (default: 'navigation-container')
     * @param {string} config.activePage - Page to highlight as active ('interview', 'database', 'problems')
     * @param {string} config.rightContent - Type of right content ('userInfo', 'userInfoWithDebug', 'backButton', 'employeeForm')
     */
    async load(config = {}) {
        const {
            containerId = 'navigation-container',
            activePage = '',
            rightContent = 'userInfo'
        } = config;

        try {
            // Load CSS
            await this.loadCSS();
            
            // Load HTML
            await this.loadHTML(containerId);
            
            // Configure active page
            this.setActivePage(activePage);
            
            // Configure right content
            this.configureRightContent(rightContent);
            
            // Load user info and setup authentication
            await this.loadUserInfo();
            
        } catch (error) {
            console.error('Error loading navigation component:', error);
        }
    },

    /**
     * Loads navigation CSS if not already loaded
     */
    async loadCSS() {
        const existingLink = document.querySelector('link[href*="nav-component.css"]');
        if (existingLink) return;

        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/components/nav-component.css';
            link.onload = resolve;
            link.onerror = reject;
            document.head.appendChild(link);
        });
    },

    /**
     * Loads navigation HTML into container
     */
    async loadHTML(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            throw new Error(`Container with id '${containerId}' not found`);
        }

        const response = await fetch('/static/components/nav-component.html');
        if (!response.ok) {
            throw new Error(`Failed to load navigation HTML: ${response.statusText}`);
        }
        
        const html = await response.text();
        container.innerHTML = html;
    },

    /**
     * Sets the active page in navigation
     */
    setActivePage(activePage) {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === activePage) {
                link.classList.add('active');
            }
        });
    },

    /**
     * Configures right-side content based on type
     */
    configureRightContent(contentType) {
        const navRight = document.getElementById('navRightContent');
        if (!navRight) return;

        let content = '';
        
        switch (contentType) {
            case 'userInfo':
                content = `
                    <div class="user-info">
                        <span id="userName">Loading...</span>
                    </div>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                `;
                break;

            case 'userInfoWithDebug':
                content = `
                    <div class="user-info">
                        <span id="userName">Loading...</span>
                    </div>
                    <div class="debug-toggle-container">
                        <span class="debug-label">Debug</span>
                        <label class="debug-switch">
                            <input type="checkbox" id="debugToggle">
                            <span class="debug-slider"></span>
                        </label>
                    </div>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                `;
                break;

            case 'backButton':
                content = `
                    <button class="back-btn" onclick="goBack()">← Back to Problems</button>
                `;
                break;

            case 'employeeForm':
                content = `
                    <div class="employee-id-form">
                        <input type="text" id="employeeId" class="employee-id-input" placeholder="Employee ID" maxlength="10">
                        <button id="submitEmployeeBtn" class="button primary" disabled>Submit</button>
                    </div>
                    <div class="debug-toggle-container">
                        <span class="debug-label">Debug</span>
                        <label class="debug-switch">
                            <input type="checkbox" id="debugToggle">
                            <span class="debug-slider"></span>
                        </label>
                    </div>
                    <div class="user-info">
                        <span id="userName">Loading...</span>
                    </div>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                `;
                break;

            default:
                content = `
                    <div class="user-info">
                        <span id="userName">Loading...</span>
                    </div>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                `;
        }

        navRight.innerHTML = content;

        // Setup employee ID form if present
        if (contentType === 'employeeForm') {
            this.setupEmployeeForm();
        }
    },

    /**
     * Sets up employee ID form functionality
     */
    setupEmployeeForm() {
        const employeeIdInput = document.getElementById('employeeId');
        const submitBtn = document.getElementById('submitEmployeeBtn');

        if (employeeIdInput && submitBtn) {
            employeeIdInput.addEventListener('input', function() {
                const value = this.value.trim();
                submitBtn.disabled = value.length === 0;
            });

            submitBtn.addEventListener('click', function() {
                const employeeId = employeeIdInput.value.trim();
                if (employeeId) {
                    // Emit custom event for parent page to handle
                    window.dispatchEvent(new CustomEvent('employeeIdSubmit', {
                        detail: { employeeId }
                    }));
                }
            });
        }
    },

    /**
     * Loads user information and handles authentication
     */
    async loadUserInfo() {
        try {
            const response = await fetch('/api/user');
            const data = await response.json();
            
            if (data.authenticated) {
                const userNameElement = document.getElementById('userName');
                if (userNameElement) {
                    userNameElement.textContent = data.user.name || data.user.username;
                }
            } else {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error loading user info:', error);
            window.location.href = '/login';
        }
    }
};

/**
 * Global logout function
 */
async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('Error logging out:', error);
        window.location.href = '/login';
    }
}

/**
 * Global back button function (for problem detail pages)
 */
function goBack() {
    window.location.href = '/problems';
}

/**
 * Convenience function for easy integration
 */
async function loadNavigation(config) {
    await window.NavComponent.load(config);
}

// Make functions globally available
window.logout = logout;
window.goBack = goBack;
window.loadNavigation = loadNavigation;