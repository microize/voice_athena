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
        
        // Validate all required elements exist
        if (!this.queryEditor || !this.executeBtn || !this.clearBtn || !this.statusBar || !this.resultsContent) {
            console.error('DatabaseQuery: Required DOM elements not found');
            return;
        }
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.executeBtn) {
            this.executeBtn.addEventListener('click', () => this.executeQuery());
        }
        
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => this.clearQuery());
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
        
        // Headers - ultra-safely handle columns
        if (safeColumns && safeColumns.length > 0) {
            safeColumns.forEach((col, index) => {
                const columnName = (col !== null && col !== undefined) ? String(col) : `Column ${index + 1}`;
                html += `<th>${columnName}</th>`;
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
}

// Global function for toggling table schemas
function toggleTableSchema(tableName) {
    const schemaElement = document.getElementById(`${tableName}-schema`);
    const toggleIcon = document.querySelector(`[onclick="toggleTableSchema('${tableName}')"] .toggle-icon`);
    
    if (schemaElement && toggleIcon) {
        const isExpanded = schemaElement.classList.contains('expanded');
        
        if (isExpanded) {
            schemaElement.classList.remove('expanded');
            toggleIcon.textContent = '▼';
        } else {
            schemaElement.classList.add('expanded');
            toggleIcon.textContent = '▲';
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', async () => {
    // Load navigation component
    await loadNavigation({activePage: 'database', rightContent: 'userInfo'});
    
    new DatabaseQuery();
});

// Make DatabaseQuery available globally
window.DatabaseQuery = DatabaseQuery;