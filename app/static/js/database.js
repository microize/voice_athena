/**
 * Database Query Interface JavaScript
 * Handles SQL query execution and results display
 */

class DatabaseQuery {
    constructor() {
        this.queryEditor = document.getElementById('queryEditor');
        this.executeBtn = document.getElementById('executeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.statusBar = document.getElementById('statusBar');
        this.resultsContent = document.getElementById('resultsContent');
        
        // New enhanced elements
        this.formatBtn = document.getElementById('formatBtn');
        this.historyBtn = document.getElementById('historyBtn');
        this.fullscreenBtn = document.getElementById('fullscreenBtn');
        this.exportCSVBtn = document.getElementById('exportCSV');
        this.exportJSONBtn = document.getElementById('exportJSON');
        this.copyResultsBtn = document.getElementById('copyResults');
        this.fullscreenResultsBtn = document.getElementById('fullscreenResults');
        
        // Schema sidebar elements
        this.collapseAllBtn = document.getElementById('collapseAllBtn');
        this.expandAllBtn = document.getElementById('expandAllBtn');
        this.schemaSearch = document.getElementById('schemaSearch');
        this.clearSearchBtn = document.getElementById('clearSearchBtn');
        
        // Sample queries elements
        this.categoryFilter = document.getElementById('categoryFilter');
        
        // Data storage
        this.currentResults = null;
        this.currentColumns = null;
        this.originalResults = null; // Store unsorted results for sorting
        this.sortState = { column: -1, direction: 'asc' }; // Track sort state
        this.queryHistory = JSON.parse(localStorage.getItem('queryHistory') || '[]');
        this.maxHistorySize = 20;
        
        // Syntax highlighter
        this.syntaxHighlighter = null;
        
        // Validate all required elements exist
        if (!this.queryEditor || !this.executeBtn || !this.clearBtn || !this.statusBar || !this.resultsContent) {
            console.error('DatabaseQuery: Required DOM elements not found');
            return;
        }
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeSyntaxHighlighter();
        this.initializeEnhancements();
    }
    
    initializeSyntaxHighlighter() {
        if (typeof SQLSyntaxHighlighter !== 'undefined') {
            this.syntaxHighlighter = new SQLSyntaxHighlighter('queryEditor');
        }
    }
    
    initializeEnhancements() {
        // Initialize any additional UI enhancements
        this.updateHistoryButton();
    }

    setupEventListeners() {
        // Original event listeners
        if (this.executeBtn) {
            this.executeBtn.addEventListener('click', () => this.executeQuery());
        }
        
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.clearQuery());
        }
        
        // Enhanced event listeners
        if (this.formatBtn) {
            this.formatBtn.addEventListener('click', () => this.formatSQL());
        }
        
        if (this.historyBtn) {
            this.historyBtn.addEventListener('click', () => this.showQueryHistory());
        }
        
        if (this.fullscreenBtn) {
            this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen('query'));
        }
        
        if (this.exportCSVBtn) {
            this.exportCSVBtn.addEventListener('click', () => this.exportResults('csv'));
        }
        
        if (this.exportJSONBtn) {
            this.exportJSONBtn.addEventListener('click', () => this.exportResults('json'));
        }
        
        if (this.copyResultsBtn) {
            this.copyResultsBtn.addEventListener('click', () => this.copyResults());
        }
        
        if (this.fullscreenResultsBtn) {
            this.fullscreenResultsBtn.addEventListener('click', () => this.toggleFullscreen('results'));
        }
        
        // Schema sidebar event listeners
        if (this.collapseAllBtn) {
            this.collapseAllBtn.addEventListener('click', () => this.collapseAllTables());
        }
        
        if (this.expandAllBtn) {
            this.expandAllBtn.addEventListener('click', () => this.expandAllTables());
        }
        
        if (this.schemaSearch) {
            this.schemaSearch.addEventListener('input', (e) => this.searchSchema(e.target.value));
        }
        
        if (this.clearSearchBtn) {
            this.clearSearchBtn.addEventListener('click', () => this.clearSchemaSearch());
        }
        
        // Sample queries event listeners
        if (this.categoryFilter) {
            this.categoryFilter.addEventListener('change', (e) => this.filterQueryCategories(e.target.value));
        }
        
        // Sample query clicks - safely handle NodeList
        const sampleQueries = document.querySelectorAll('.sample-query');
        if (sampleQueries && sampleQueries.length > 0) {
            sampleQueries.forEach(query => {
                if (query) {
                    query.addEventListener('click', (e) => {
                        const sql = e?.currentTarget?.getAttribute?.('data-query');
                        if (sql && this.queryEditor) {
                            this.queryEditor.value = sql;
                            if (this.syntaxHighlighter) {
                                this.syntaxHighlighter.highlightSyntax();
                            }
                        }
                    });
                }
            });
        }

        // Ctrl+Enter to execute - safely handle keydown
        if (this.queryEditor) {
            this.queryEditor.addEventListener('keydown', (e) => {
                if (e && e.ctrlKey && e.key === 'Enter') {
                    this.executeQuery();
                }
            });
        }
    }

    async executeQuery() {
        const query = this.queryEditor?.value?.trim?.() || '';
        
        if (!query) {
            this.showStatus('Please enter a SQL query', 'error');
            return;
        }

        this.executeBtn.disabled = true;
        this.executeBtn.textContent = 'Executing...';
        this.resultsContent.innerHTML = '<div class="loading">Executing query...</div>';
        
        // Track execution time
        const startTime = Date.now();

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            if (!response) {
                throw new Error('No response received from server');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data?.detail || data?.error || 'Query failed');
            }

            // Ultra-defensive validation - ensure data structure is correct
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }
            
            // Ensure we have safe arrays with fallbacks
            const results = (data && Array.isArray(data.data)) ? data.data : [];
            const columns = (data && Array.isArray(data.columns)) ? data.columns : [];
            
            // Additional safety check before accessing length
            const safeResults = Array.isArray(results) ? results : [];
            const resultCount = safeResults.length || 0;
            
            const executionTime = Date.now() - startTime;
            
            // Store results for export and sorting
            this.currentResults = safeResults;
            this.originalResults = [...safeResults]; // Deep copy for sorting
            this.currentColumns = columns;
            this.sortState = { column: -1, direction: 'asc' }; // Reset sort state
            
            // Add query to history
            this.addToHistory(query, resultCount);
            
            this.displayResults(safeResults, columns);
            this.showStatus(`Query executed successfully. ${resultCount} rows returned.`, 'success');
            this.updateResultsMeta(resultCount, executionTime);

        } catch (error) {
            const errorMessage = error?.message || 'Unknown error occurred';
            this.showStatus(`Error: ${errorMessage}`, 'error');
            this.resultsContent.innerHTML = `<div class="no-results">❌ ${errorMessage}</div>`;
        } finally {
            this.executeBtn.disabled = false;
            this.executeBtn.textContent = 'Execute Query';
        }
    }

    displayResults(results, columns) {
        // Ultra-defensive safety checks with null coalescing
        const safeResults = Array.isArray(results) ? results : [];
        const safeColumns = Array.isArray(columns) ? columns : [];
        
        if (!safeResults || safeResults.length === 0) {
            this.resultsContent.innerHTML = '<div class="no-results">No results found</div>';
            return;
        }

        let html = '<table class="results-table"><thead><tr>';
        
        // Headers - ultra-safely handle columns with sorting
        if (safeColumns && safeColumns.length > 0) {
            safeColumns.forEach((col, index) => {
                const columnName = (col !== null && col !== undefined) ? String(col) : `Column ${index + 1}`;
                html += `<th class="sortable-header" data-column="${index}" onclick="window.databaseQuery.sortColumn(${index})">
                    ${columnName}
                    <span class="sort-indicator"></span>
                </th>`;
            });
        } else {
            // If no columns provided, use generic column names based on first row
            const firstRow = safeResults[0];
            if (firstRow && Array.isArray(firstRow)) {
                const rowLength = firstRow.length || 0;
                for (let i = 0; i < rowLength; i++) {
                    html += `<th>Column ${i + 1}</th>`;
                }
            } else {
                // Fallback for non-array rows
                html += '<th>Value</th>';
            }
        }
        html += '</tr></thead><tbody>';

        // Rows - ultra-safely handle each row
        safeResults.forEach((row, rowIndex) => {
            if (row === null || row === undefined) {
                html += '<tr><td><em>NULL ROW</em></td></tr>';
                return;
            }
            
            html += '<tr>';
            if (Array.isArray(row)) {
                const safeRow = row || [];
                if (safeRow.length === 0) {
                    html += '<td><em>EMPTY ROW</em></td>';
                } else {
                    safeRow.forEach(cell => {
                        const cellValue = cell === null ? '<em>NULL</em>' : 
                                       cell === undefined ? '<em>UNDEFINED</em>' : 
                                       String(cell);
                        html += `<td>${cellValue}</td>`;
                    });
                }
            } else {
                // If row is not an array, display it as a single cell
                const cellValue = row === null ? '<em>NULL</em>' : 
                               row === undefined ? '<em>UNDEFINED</em>' : 
                               String(row);
                html += `<td>${cellValue}</td>`;
            }
            html += '</tr>';
        });

        html += '</tbody></table>';
        
        // Final safety check before setting innerHTML
        if (this.resultsContent) {
            this.resultsContent.innerHTML = html;
        }
    }

    showStatus(message, type) {
        if (!this.statusBar) return;
        
        const safeMessage = message || 'Unknown status';
        const safeType = type || 'info';
        
        this.statusBar.textContent = safeMessage;
        this.statusBar.className = `status-bar ${safeType}`;
        
        if (safeType === 'success') {
            setTimeout(() => {
                if (this.statusBar && this.statusBar.style) {
                    this.statusBar.style.display = 'none';
                }
            }, 3000);
        }
    }

    clearQuery() {
        if (this.queryEditor) {
            this.queryEditor.value = '';
        }
        
        if (this.resultsContent) {
            this.resultsContent.innerHTML = '<div class="no-results">Execute a query to see results here</div>';
        }
        
        if (this.statusBar && this.statusBar.style) {
            this.statusBar.style.display = 'none';
        }
        
        // Clear results metadata
        const resultsMeta = document.getElementById('resultsMeta');
        if (resultsMeta) {
            resultsMeta.textContent = '';
        }
    }

    updateResultsMeta(rowCount, executionTime) {
        const resultsMeta = document.getElementById('resultsMeta');
        if (resultsMeta) {
            resultsMeta.textContent = `${rowCount} rows • ${executionTime}ms`;
        }
    }
    
    // ==================== ENHANCED FEATURES ==================== //
    
    formatSQL() {
        const query = this.queryEditor.value;
        if (!query.trim()) return;
        
        // Basic SQL formatting
        let formatted = query
            .replace(/\s+/g, ' ')
            .replace(/,\s*/g, ',\n    ')
            .replace(/\bSELECT\b/gi, 'SELECT')
            .replace(/\bFROM\b/gi, '\nFROM')
            .replace(/\bWHERE\b/gi, '\nWHERE')
            .replace(/\bJOIN\b/gi, '\nJOIN')
            .replace(/\bINNER JOIN\b/gi, '\nINNER JOIN')
            .replace(/\bLEFT JOIN\b/gi, '\nLEFT JOIN')
            .replace(/\bRIGHT JOIN\b/gi, '\nRIGHT JOIN')
            .replace(/\bGROUP BY\b/gi, '\nGROUP BY')
            .replace(/\bORDER BY\b/gi, '\nORDER BY')
            .replace(/\bHAVING\b/gi, '\nHAVING')
            .replace(/\bLIMIT\b/gi, '\nLIMIT')
            .replace(/\bAND\b/gi, '\n    AND')
            .replace(/\bOR\b/gi, '\n    OR');
        
        this.queryEditor.value = formatted.trim();
        if (this.syntaxHighlighter) {
            this.syntaxHighlighter.highlightSyntax();
            this.syntaxHighlighter.updateLineNumbers();
        }
    }
    
    addToHistory(query, resultCount) {
        const historyItem = {
            query: query.trim(),
            timestamp: new Date().toISOString(),
            resultCount: resultCount
        };
        
        // Remove duplicate queries
        this.queryHistory = this.queryHistory.filter(item => item.query !== query.trim());
        
        // Add to beginning
        this.queryHistory.unshift(historyItem);
        
        // Limit size
        if (this.queryHistory.length > this.maxHistorySize) {
            this.queryHistory = this.queryHistory.slice(0, this.maxHistorySize);
        }
        
        // Save to localStorage
        localStorage.setItem('queryHistory', JSON.stringify(this.queryHistory));
        this.updateHistoryButton();
    }
    
    updateHistoryButton() {
        if (this.historyBtn && this.queryHistory.length > 0) {
            this.historyBtn.title = `Query History (${this.queryHistory.length} queries)`;
        }
    }
    
    showQueryHistory() {
        if (this.queryHistory.length === 0) {
            this.showMessage('No query history available', 'info');
            return;
        }
        
        // Create modal for query history
        const modal = this.createModal('Query History', this.renderQueryHistory());
        document.body.appendChild(modal);
    }
    
    renderQueryHistory() {
        const historyHTML = this.queryHistory.map((item, index) => {
            const date = new Date(item.timestamp).toLocaleString();
            const preview = item.query.length > 100 ? item.query.substring(0, 100) + '...' : item.query;
            
            return `
                <div class="history-item" data-index="${index}">
                    <div class="history-meta">
                        <span class="history-date">${date}</span>
                        <span class="history-results">${item.resultCount} rows</span>
                    </div>
                    <div class="history-query">${sanitizeInput(preview)}</div>
                </div>
            `;
        }).join('');
        
        return `
            <div class="query-history-container">
                ${historyHTML}
            </div>
        `;
    }
    
    exportResults(format) {
        if (!this.currentResults || !this.currentColumns) {
            this.showMessage('No results to export', 'warning');
            return;
        }
        
        let content = '';
        let filename = '';
        let mimeType = '';
        
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        
        if (format === 'csv') {
            content = this.generateCSV();
            filename = `query-results-${timestamp}.csv`;
            mimeType = 'text/csv';
        } else if (format === 'json') {
            content = this.generateJSON();
            filename = `query-results-${timestamp}.json`;
            mimeType = 'application/json';
        }
        
        this.downloadFile(content, filename, mimeType);
        this.showMessage(`Results exported as ${format.toUpperCase()}`, 'success');
    }
    
    generateCSV() {
        const headers = this.currentColumns.join(',');
        const rows = this.currentResults.map(row => 
            row.map(cell => {
                const cellStr = String(cell || '');
                // Escape quotes and wrap in quotes if contains comma, quote, or newline
                if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
                    return `"${cellStr.replace(/"/g, '""')}"`;
                }
                return cellStr;
            }).join(',')
        );
        
        return [headers, ...rows].join('\n');
    }
    
    generateJSON() {
        const data = this.currentResults.map(row => {
            const obj = {};
            this.currentColumns.forEach((col, index) => {
                obj[col] = row[index];
            });
            return obj;
        });
        
        return JSON.stringify({
            query_results: data,
            metadata: {
                columns: this.currentColumns,
                row_count: this.currentResults.length,
                exported_at: new Date().toISOString()
            }
        }, null, 2);
    }
    
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    async copyResults() {
        if (!this.currentResults || !this.currentColumns) {
            this.showMessage('No results to copy', 'warning');
            return;
        }
        
        const csv = this.generateCSV();
        
        try {
            await navigator.clipboard.writeText(csv);
            this.showMessage('Results copied to clipboard', 'success');
        } catch (err) {
            this.showMessage('Failed to copy to clipboard', 'error');
        }
    }
    
    toggleFullscreen(type) {
        const element = type === 'query' ? 
            document.querySelector('.query-panel') : 
            document.querySelector('.results-panel');
            
        if (!element) return;
        
        if (element.classList.contains('fullscreen')) {
            element.classList.remove('fullscreen');
            document.body.classList.remove('fullscreen-active');
        } else {
            element.classList.add('fullscreen');
            document.body.classList.add('fullscreen-active');
        }
    }
    
    createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
            </div>
        `;
        
        // Add click handler for history items
        modal.addEventListener('click', (e) => {
            const historyItem = e.target.closest('.history-item');
            if (historyItem) {
                const index = parseInt(historyItem.dataset.index);
                const query = this.queryHistory[index].query;
                this.queryEditor.value = query;
                if (this.syntaxHighlighter) {
                    this.syntaxHighlighter.highlightSyntax();
                    this.syntaxHighlighter.updateLineNumbers();
                }
                modal.remove();
            }
        });
        
        // Close modal on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }
    
    showMessage(message, type = 'info') {
        // Use the global showMessage function from utils.js
        if (typeof showMessage === 'function') {
            showMessage(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    sortColumn(columnIndex) {
        if (!this.originalResults || !this.currentColumns) return;
        
        // Determine sort direction
        if (this.sortState.column === columnIndex) {
            this.sortState.direction = this.sortState.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortState.column = columnIndex;
            this.sortState.direction = 'asc';
        }
        
        // Sort the results
        const sortedResults = [...this.originalResults].sort((a, b) => {
            const aVal = a[columnIndex];
            const bVal = b[columnIndex];
            
            // Handle null/undefined values
            if (aVal === null || aVal === undefined) return 1;
            if (bVal === null || bVal === undefined) return -1;
            
            // Determine if values are numeric
            const aNum = Number(aVal);
            const bNum = Number(bVal);
            const isNumeric = !isNaN(aNum) && !isNaN(bNum);
            
            let comparison = 0;
            if (isNumeric) {
                comparison = aNum - bNum;
            } else {
                comparison = String(aVal).localeCompare(String(bVal));
            }
            
            return this.sortState.direction === 'desc' ? -comparison : comparison;
        });
        
        // Update current results and re-display
        this.currentResults = sortedResults;
        this.displayResults(sortedResults, this.currentColumns);
        this.updateSortIndicators();
    }
    
    updateSortIndicators() {
        // Remove existing sort classes
        document.querySelectorAll('.sortable-header').forEach(header => {
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Add current sort class
        if (this.sortState.column >= 0) {
            const currentHeader = document.querySelector(`[data-column="${this.sortState.column}"]`);
            if (currentHeader) {
                currentHeader.classList.add(`sort-${this.sortState.direction}`);
            }
        }
    }
    
    // ==================== SCHEMA SIDEBAR FEATURES ==================== //
    
    collapseAllTables() {
        const allTableColumns = document.querySelectorAll('.table-columns');
        const allToggleIcons = document.querySelectorAll('.toggle-icon');
        
        allTableColumns.forEach(columns => {
            columns.classList.add('collapsed');
        });
        
        allToggleIcons.forEach(icon => {
            icon.textContent = '▲';
        });
    }
    
    expandAllTables() {
        const allTableColumns = document.querySelectorAll('.table-columns');
        const allToggleIcons = document.querySelectorAll('.toggle-icon');
        
        allTableColumns.forEach(columns => {
            columns.classList.remove('collapsed');
        });
        
        allToggleIcons.forEach(icon => {
            icon.textContent = '▼';
        });
    }
    
    searchSchema(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        const tableItems = document.querySelectorAll('.table-item');
        
        if (!term) {
            // Show all items and remove highlights
            tableItems.forEach(table => {
                table.classList.remove('search-hidden');
                const columns = table.querySelectorAll('.column-item');
                columns.forEach(column => {
                    column.classList.remove('search-hidden');
                    this.removeHighlights(column);
                });
            });
            return;
        }
        
        tableItems.forEach(table => {
            const tableName = table.querySelector('.table-name').textContent.toLowerCase();
            const columns = table.querySelectorAll('.column-item');
            let tableMatches = tableName.includes(term);
            let hasVisibleColumns = false;
            
            // Check columns
            columns.forEach(column => {
                const columnName = column.querySelector('.column-name').textContent.toLowerCase();
                const columnType = column.querySelector('.column-type').textContent.toLowerCase();
                const columnMatches = columnName.includes(term) || columnType.includes(term);
                
                if (columnMatches) {
                    column.classList.remove('search-hidden');
                    hasVisibleColumns = true;
                    this.highlightText(column, term);
                } else {
                    column.classList.add('search-hidden');
                    this.removeHighlights(column);
                }
            });
            
            // Show/hide table based on matches
            if (tableMatches || hasVisibleColumns) {
                table.classList.remove('search-hidden');
                // Expand table if it has matches
                const tableColumns = table.querySelector('.table-columns');
                if (tableColumns && (tableMatches || hasVisibleColumns)) {
                    tableColumns.classList.remove('collapsed');
                    const toggleIcon = table.querySelector('.toggle-icon');
                    if (toggleIcon) toggleIcon.textContent = '▼';
                }
                
                if (tableMatches) {
                    this.highlightText(table.querySelector('.table-name').parentNode, term);
                }
            } else {
                table.classList.add('search-hidden');
            }
        });
    }
    
    highlightText(element, term) {
        const textNodes = this.getTextNodes(element);
        textNodes.forEach(node => {
            const text = node.textContent;
            const index = text.toLowerCase().indexOf(term);
            if (index !== -1) {
                const span = document.createElement('span');
                span.className = 'search-highlight';
                span.textContent = text.substring(index, index + term.length);
                
                const before = text.substring(0, index);
                const after = text.substring(index + term.length);
                
                const parent = node.parentNode;
                if (before) parent.insertBefore(document.createTextNode(before), node);
                parent.insertBefore(span, node);
                if (after) parent.insertBefore(document.createTextNode(after), node);
                parent.removeChild(node);
            }
        });
    }
    
    removeHighlights(element) {
        const highlights = element.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.insertBefore(document.createTextNode(highlight.textContent), highlight);
            parent.removeChild(highlight);
            parent.normalize();
        });
    }
    
    getTextNodes(element) {
        const textNodes = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim()) {
                textNodes.push(node);
            }
        }
        
        return textNodes;
    }
    
    clearSchemaSearch() {
        if (this.schemaSearch) {
            this.schemaSearch.value = '';
            this.searchSchema('');
        }
    }
    
    // ==================== SAMPLE QUERIES FEATURES ==================== //
    
    filterQueryCategories(selectedCategory) {
        const categories = document.querySelectorAll('.query-category');
        
        categories.forEach(category => {
            const categoryName = category.getAttribute('data-category');
            
            if (selectedCategory === 'all' || selectedCategory === categoryName) {
                category.classList.remove('hidden');
            } else {
                category.classList.add('hidden');
            }
        });
    }
}

// Global function for toggling table schemas
function toggleTableSchema(tableName) {
    const schemaElement = document.getElementById(`${tableName}-schema`);
    const toggleIcon = document.querySelector(`[onclick="toggleTableSchema('${tableName}')"] .toggle-icon`);
    
    if (schemaElement && toggleIcon) {
        const isCollapsed = schemaElement.classList.contains('collapsed');
        
        if (isCollapsed) {
            schemaElement.classList.remove('collapsed');
            toggleIcon.textContent = '▼';
        } else {
            schemaElement.classList.add('collapsed');
            toggleIcon.textContent = '▲';
        }
    }
}

// Global function for copying column names
async function copyColumnName(columnName) {
    try {
        await navigator.clipboard.writeText(columnName);
        if (window.databaseQuery) {
            window.databaseQuery.showMessage(`Copied "${columnName}" to clipboard`, 'success');
        }
    } catch (err) {
        console.error('Failed to copy column name:', err);
        if (window.databaseQuery) {
            window.databaseQuery.showMessage('Failed to copy column name', 'error');
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', async () => {
    // Load navigation component
    await loadNavigation({activePage: 'database', rightContent: 'userInfo'});
    
    // Create global instance for sorting functionality
    window.databaseQuery = new DatabaseQuery();
});

// Make DatabaseQuery available globally
window.DatabaseQuery = DatabaseQuery;