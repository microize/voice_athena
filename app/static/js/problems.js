/**
 * Problems page functionality
 * Handles fetching and displaying coding problems in LeetCode-style interface
 */

class ProblemsManager {
    constructor() {
        this.problems = [];
        this.filteredProblems = [];
        this.currentFilter = 'all';
        this.searchTerm = '';
        this.loading = false;
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.totalPages = 1;
        this.init();
    }

    async init() {
        await this.loadProblems();
        this.setupEventListeners();
        this.calculatePagination();
        this.renderProblems();
        this.updatePagination();
    }

    async loadProblems() {
        try {
            this.setLoading(true);
            const response = await fetch('/api/problems', {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.problems = data.problems || [];
            this.filteredProblems = [...this.problems];
            this.currentPage = 1;
            
        } catch (error) {
            console.error('Error loading problems:', error);
            this.showMessage('Failed to load problems. Please refresh the page.', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    setupEventListeners() {
        const filterTabs = document.querySelectorAll('.filter-tab');
        const searchInput = document.getElementById('searchInput');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        // Filter tab listeners
        filterTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const filterValue = e.target.dataset.value;
                const filterType = e.target.closest('.filter-tabs').dataset.filter;
                
                // Update active state
                const tabGroup = e.target.parentElement;
                tabGroup.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                this.currentPage = 1; // Reset to first page when filtering
                this.applyFilter(filterValue);
            });
        });
        
        // Search input listener
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase().trim();
                this.currentPage = 1; // Reset to first page when searching
                this.applyFilter(this.currentFilter);
            });
        }
        
        // Pagination listeners
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.renderProblems();
                    this.updatePagination();
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (this.currentPage < this.totalPages) {
                    this.currentPage++;
                    this.renderProblems();
                    this.updatePagination();
                }
            });
        }
        
        // Update problem count
        this.updateProblemCount();
    }

    applyFilter(filter) {
        this.currentFilter = filter;
        
        this.filteredProblems = this.problems.filter(problem => {
            // Apply search filter first
            let matchesSearch = true;
            if (this.searchTerm) {
                const title = problem.title?.toLowerCase() || '';
                const category = problem.category?.toLowerCase() || '';
                matchesSearch = title.includes(this.searchTerm) || category.includes(this.searchTerm);
            }
            
            // Apply category/difficulty filter
            let matchesFilter = true;
            if (filter !== 'all') {
                const difficulty = problem.difficulty?.toLowerCase();
                const category = problem.category?.toLowerCase();
                const tags = Array.isArray(problem.tags) ? 
                    problem.tags.map(tag => tag.toLowerCase()) : 
                    (typeof problem.tags === 'string' ? JSON.parse(problem.tags).map(tag => tag.toLowerCase()) : []);
                
                matchesFilter = difficulty === filter.toLowerCase() || 
                               category === filter.toLowerCase() || 
                               tags.includes(filter.toLowerCase());
            }
            
            return matchesSearch && matchesFilter;
        });
        
        this.calculatePagination();
        this.renderProblems();
        this.updateProblemCount();
        this.updatePagination();
    }

    calculatePagination() {
        this.totalPages = Math.ceil(this.filteredProblems.length / this.itemsPerPage);
        if (this.currentPage > this.totalPages) {
            this.currentPage = Math.max(1, this.totalPages);
        }
    }

    getPaginatedProblems() {
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        return this.filteredProblems.slice(startIndex, endIndex);
    }

    renderProblems() {
        const problemsList = document.getElementById('problemsList');
        
        if (!problemsList) {
            console.error('Problems list element not found');
            return;
        }

        if (this.loading) {
            problemsList.innerHTML = this.getLoadingHTML();
            return;
        }

        if (this.filteredProblems.length === 0) {
            problemsList.innerHTML = this.getEmptyStateHTML();
            return;
        }

        const paginatedProblems = this.getPaginatedProblems();
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        
        const problemsHTML = paginatedProblems.map((problem, index) => 
            this.renderProblemRow(problem, startIndex + index + 1)
        ).join('');

        problemsList.innerHTML = problemsHTML;
        
        // Initialize Lucide icons for bookmark icons
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    }

    renderProblemRow(problem, index) {
        // Use the solved status from the database
        const isSolved = problem.solved === true;
        const statusClass = isSolved ? 'solved' : '';
        
        // Check if problem is bookmarked (from localStorage)
        const bookmarkedProblems = JSON.parse(localStorage.getItem('bookmarkedProblems') || '[]');
        const isBookmarked = bookmarkedProblems.some(bookmark => bookmark.id === problem.id);
        const bookmarkClass = isBookmarked ? 'bookmarked' : '';
        
        return `
            <tr data-problem-id="${problem.id}">
                <td>
                    <div class="problem-title-container">
                        <span class="problem-status-indicator ${statusClass}"></span>
                        <i data-lucide="bookmark" class="problem-bookmark-icon ${bookmarkClass}" 
                           onclick="toggleBookmark(${problem.id}, '${sanitizeInput(problem.title)}', '${problem.difficulty}')"></i>
                        <a href="/problem/${problem.id}" class="problem-title">
                            ${sanitizeInput(problem.title)}
                        </a>
                    </div>
                </td>
                <td>
                    <span class="category-text">${sanitizeInput(problem.category)}</span>
                </td>
                <td>
                    <span class="difficulty-text">${sanitizeInput(problem.difficulty)}</span>
                </td>
                <td>
                    <a href="/problem/${problem.id}" class="solve-link">Solve</a>
                </td>
            </tr>
        `;
    }

    truncateDescription(description, maxLength) {
        if (description.length <= maxLength) {
            return description;
        }
        return description.substring(0, maxLength) + '...';
    }

    getLoadingHTML() {
        return `
            <tr class="loading">
                <td colspan="4">Loading problems...</td>
            </tr>
        `;
    }

    getEmptyStateHTML() {
        return `
            <tr class="empty-state">
                <td colspan="4">No problems found. Try adjusting your filters.</td>
            </tr>
        `;
    }

    setLoading(loading) {
        this.loading = loading;
        const problemsList = document.getElementById('problemsList');
        if (loading && problemsList) {
            problemsList.innerHTML = this.getLoadingHTML();
        }
    }
    
    updateProblemCount() {
        const countElement = document.getElementById('problemCount');
        if (countElement && this.problems.length > 0) {
            countElement.textContent = `${this.problems.length} problems`;
        }
    }

    updatePagination() {
        this.updatePaginationInfo();
        this.updatePaginationButtons();
        this.generatePageNumbers();
    }

    updatePaginationInfo() {
        const paginationInfo = document.getElementById('paginationInfo');
        if (paginationInfo) {
            const startItem = this.filteredProblems.length === 0 ? 0 : (this.currentPage - 1) * this.itemsPerPage + 1;
            const endItem = Math.min(this.currentPage * this.itemsPerPage, this.filteredProblems.length);
            const totalItems = this.filteredProblems.length;
            
            paginationInfo.textContent = `Showing ${startItem}-${endItem} of ${totalItems} problems`;
        }
    }

    updatePaginationButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentPage <= 1;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= this.totalPages;
        }
    }

    generatePageNumbers() {
        const paginationNumbers = document.getElementById('paginationNumbers');
        if (!paginationNumbers) return;

        const maxVisiblePages = 7;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

        // Adjust start page if we're near the end
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        let html = '';

        // First page and ellipsis
        if (startPage > 1) {
            html += `<button class="page-number" data-page="1">1</button>`;
            if (startPage > 2) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
        }

        // Page numbers
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === this.currentPage ? 'active' : '';
            html += `<button class="page-number ${activeClass}" data-page="${i}">${i}</button>`;
        }

        // Last page and ellipsis
        if (endPage < this.totalPages) {
            if (endPage < this.totalPages - 1) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
            html += `<button class="page-number" data-page="${this.totalPages}">${this.totalPages}</button>`;
        }

        paginationNumbers.innerHTML = html;

        // Add click listeners to page numbers
        paginationNumbers.querySelectorAll('.page-number').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = parseInt(e.target.dataset.page);
                if (page !== this.currentPage) {
                    this.currentPage = page;
                    this.renderProblems();
                    this.updatePagination();
                }
            });
        });
    }

    showMessage(message, type = 'info') {
        // Use the global showMessage function from utils.js
        if (typeof showMessage === 'function') {
            showMessage(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Bookmark functionality
function toggleBookmark(problemId, problemTitle, problemDifficulty) {
    const bookmarkedProblems = JSON.parse(localStorage.getItem('bookmarkedProblems') || '[]');
    const existingIndex = bookmarkedProblems.findIndex(bookmark => bookmark.id === problemId);
    
    if (existingIndex >= 0) {
        // Remove bookmark
        bookmarkedProblems.splice(existingIndex, 1);
        showMessage('Bookmark removed', 'info');
    } else {
        // Add bookmark
        bookmarkedProblems.push({
            id: problemId,
            title: problemTitle,
            difficulty: problemDifficulty,
            bookmarkedAt: new Date().toISOString()
        });
        showMessage('Problem bookmarked', 'success');
    }
    
    // Save to localStorage
    localStorage.setItem('bookmarkedProblems', JSON.stringify(bookmarkedProblems));
    
    // Update the bookmark icon
    const bookmarkIcon = document.querySelector(`tr[data-problem-id="${problemId}"] .problem-bookmark-icon`);
    if (bookmarkIcon) {
        if (existingIndex >= 0) {
            bookmarkIcon.classList.remove('bookmarked');
        } else {
            bookmarkIcon.classList.add('bookmarked');
        }
    }
}

// Initialize problems manager when DOM is loaded
let problemsManager = null;

document.addEventListener('DOMContentLoaded', () => {
    problemsManager = new ProblemsManager();
});