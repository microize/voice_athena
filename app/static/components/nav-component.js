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

        console.log('🚀 Loading navigation component...', config);

        try {
            // Load CSS
            console.log('📄 Loading CSS...');
            await this.loadCSS();
            
            // Load HTML
            console.log('🔄 Loading HTML...');
            await this.loadHTML(containerId);
            
            // Configure active page
            console.log('🎯 Setting active page:', activePage);
            this.setActivePage(activePage);
            
            // Configure right content - enable debug by default for all pages
            const debugRightContent = rightContent === 'userInfo' ? 'userInfoWithDebug' : rightContent;
            console.log('⚙️ Configuring content:', debugRightContent);
            this.configureRightContent(debugRightContent);
            
            // Load user info and setup authentication
            console.log('👤 Loading user info...');
            await this.loadUserInfo();
            
            // Setup mobile functionality
            console.log('📱 Setting up mobile menu...');
            this.setupMobileMenu();
            
            // Initialize sidebar state
            console.log('🔄 Initializing sidebar state...');
            initializeSidebarState();
            
            // Initialize Lucide icons after a short delay to ensure DOM is ready
            console.log('🎨 Initializing Lucide icons...');
            setTimeout(() => {
                this.initializeLucideIcons();
            }, 100);
            
            console.log('✅ Navigation component loaded successfully!');
            
        } catch (error) {
            console.error('❌ Error loading navigation component:', error);
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
     * Configures bottom content based on type (for sidebar)
     */
    configureRightContent(contentType) {
        const navBottom = document.getElementById('navBottomContent');
        if (!navBottom) return;

        let content = '';
        
        switch (contentType) {
            case 'userInfo':
                content = `
                    <div class="user-info">
                        <i data-lucide="user" class="nav-icon"></i>
                        <span id="userName">Loading...</span>
                    </div>
                    <button class="logout-btn" onclick="logout()">
                        <i data-lucide="log-out" class="nav-icon"></i>
                        <span>Logout</span>
                    </button>
                `;
                break;

            case 'userInfoWithDebug':
                content = `
                    <div class="user-info">
                        <i data-lucide="user" class="nav-icon"></i>
                        <span id="userName">Loading...</span>
                    </div>
                    <div class="debug-toggle-container">
                        <span class="debug-label">Debug</span>
                        <label class="debug-switch">
                            <input type="checkbox" id="debugToggle">
                            <span class="debug-slider"></span>
                        </label>
                    </div>
                    <button class="logout-btn" onclick="logout()">
                        <i data-lucide="log-out" class="nav-icon"></i>
                        <span>Logout</span>
                    </button>
                `;
                break;

            case 'backButton':
                content = `
                    <button class="back-btn" onclick="goBack()">
                        <i data-lucide="arrow-left" class="nav-icon"></i>
                        <span>Back to Problems</span>
                    </button>
                `;
                break;

            case 'employeeForm':
                content = `
                    <div class="employee-id-form">
                        <input type="text" id="employeeId" class="employee-id-input" placeholder="Employee ID" maxlength="10">
                        <button id="submitEmployeeBtn" class="button primary" disabled>
                            <i data-lucide="send" class="nav-icon"></i>
                            <span>Submit</span>
                        </button>
                    </div>
                    <div class="debug-toggle-container">
                        <span class="debug-label">Debug</span>
                        <label class="debug-switch">
                            <input type="checkbox" id="debugToggle">
                            <span class="debug-slider"></span>
                        </label>
                    </div>
                    <div class="user-info">
                        <i data-lucide="user" class="nav-icon"></i>
                        <span id="userName">Loading...</span>
                    </div>
                    <button class="logout-btn" onclick="logout()">
                        <i data-lucide="log-out" class="nav-icon"></i>
                        <span>Logout</span>
                    </button>
                `;
                break;

            default:
                content = `
                    <div class="user-info">
                        <i data-lucide="user" class="nav-icon"></i>
                        <span id="userName">Loading...</span>
                    </div>
                    <button class="logout-btn" onclick="logout()">
                        <i data-lucide="log-out" class="nav-icon"></i>
                        <span>Logout</span>
                    </button>
                `;
        }

        navBottom.innerHTML = content;

        // Initialize Lucide icons for the new content after a short delay
        setTimeout(() => {
            this.initializeLucideIcons();
        }, 100);

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
     * Sets up mobile menu functionality
     */
    setupMobileMenu() {
        // Create mobile menu toggle button if it doesn't exist
        let mobileToggle = document.querySelector('.mobile-menu-toggle');
        if (!mobileToggle) {
            mobileToggle = document.createElement('button');
            mobileToggle.className = 'mobile-menu-toggle';
            mobileToggle.innerHTML = '≡';
            mobileToggle.setAttribute('aria-label', 'Toggle navigation menu');
            document.body.appendChild(mobileToggle);
        }

        // Get sidebar element
        const sidebar = document.querySelector('.nav-sidebar');
        if (!sidebar) return;

        // Toggle mobile menu
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
            mobileToggle.innerHTML = sidebar.classList.contains('mobile-open') ? '×' : '≡';
        });

        // Close mobile menu when clicking on links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('mobile-open');
                    mobileToggle.innerHTML = '≡';
                }
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                sidebar.classList.contains('mobile-open') &&
                !sidebar.contains(e.target) && 
                !mobileToggle.contains(e.target)) {
                sidebar.classList.remove('mobile-open');
                mobileToggle.innerHTML = '☰';
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('mobile-open');
                mobileToggle.innerHTML = '☰';
            }
        });
    },

    /**
     * Initialize Lucide icons
     */
    initializeLucideIcons() {
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            try {
                console.log('Initializing Lucide icons...');
                lucide.createIcons();
                console.log('Lucide icons initialized successfully');
            } catch (error) {
                console.warn('Failed to initialize Lucide icons:', error);
            }
        } else {
            console.warn('Lucide icons library not loaded');
        }
    },

    /**
     * Loads user information and handles authentication
     */
    async loadUserInfo() {
        try {
            const response = await fetch('/api/user/me');
            if (response.ok) {
                const data = await response.json();
                
                if (data.authenticated) {
                    const userNameElement = document.getElementById('userName');
                    if (userNameElement) {
                        userNameElement.textContent = data.username || 'User';
                    }
                } else {
                    window.location.href = '/login';
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

/**
 * Toggle sidebar collapse/expand functionality
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.nav-sidebar');
    const container = document.querySelector('.container');
    
    if (sidebar && container) {
        sidebar.classList.toggle('collapsed');
        container.classList.toggle('sidebar-collapsed');
        
        // Store the sidebar state in localStorage
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed.toString());
    }
}

/**
 * Initialize sidebar state from localStorage
 */
function initializeSidebarState() {
    // Default to collapsed if no preference is stored
    const isCollapsed = localStorage.getItem('sidebarCollapsed') !== 'false';
    if (isCollapsed) {
        const sidebar = document.querySelector('.nav-sidebar');
        const container = document.querySelector('.container');
        
        if (sidebar && container) {
            sidebar.classList.add('collapsed');
            container.classList.add('sidebar-collapsed');
        }
    }
}

// Make functions globally available
window.logout = logout;
window.goBack = goBack;
window.loadNavigation = loadNavigation;
window.toggleSidebar = toggleSidebar;

// Initialize sidebar state when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSidebarState);