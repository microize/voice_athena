/**
 * SQL Syntax Highlighter
 * Provides syntax highlighting and auto-completion for SQL queries
 */

class SQLSyntaxHighlighter {
    constructor(textareaId) {
        this.textarea = document.getElementById(textareaId);
        this.highlightContainer = null;
        this.lineNumbers = null;
        
        // SQL Keywords
        this.keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER',
            'ON', 'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'LIMIT', 'OFFSET',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE',
            'ALTER', 'DROP', 'INDEX', 'VIEW', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN',
            'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL', 'EXISTS',
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'IF', 'UNION', 'ALL', 'INTERSECT', 'EXCEPT'
        ];
        
        // Data types
        this.dataTypes = [
            'INTEGER', 'VARCHAR', 'TEXT', 'CHAR', 'BOOLEAN', 'DATE', 'DATETIME', 'TIMESTAMP',
            'REAL', 'FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC', 'BLOB', 'PRIMARY', 'KEY',
            'FOREIGN', 'UNIQUE', 'NOT', 'NULL', 'DEFAULT', 'AUTO_INCREMENT'
        ];
        
        // Functions
        this.functions = [
            'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'UPPER', 'LOWER', 'LENGTH', 'SUBSTRING',
            'CONCAT', 'TRIM', 'LTRIM', 'RTRIM', 'REPLACE', 'COALESCE', 'IFNULL', 'ROUND',
            'CEIL', 'FLOOR', 'ABS', 'NOW', 'CURRENT_DATE', 'CURRENT_TIME', 'DATE_FORMAT'
        ];
        
        // Table and column names from schema
        this.tableNames = ['employees', 'interview_sessions', 'interview_questions'];
        this.columnNames = [
            'id', 'employee_id', 'name', 'department', 'role', 'session_id', 'start_time',
            'end_time', 'status', 'overall_score', 'question_text', 'category', 'difficulty', 'score'
        ];
        
        this.init();
    }
    
    init() {
        if (!this.textarea) return;
        
        this.createHighlightContainer();
        this.createLineNumbers();
        this.setupEventListeners();
        this.highlightSyntax();
        this.updateLineNumbers();
    }
    
    createHighlightContainer() {
        // Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'query-editor-wrapper';
        
        // Insert wrapper before textarea
        this.textarea.parentNode.insertBefore(wrapper, this.textarea);
        
        // Create highlight container
        this.highlightContainer = document.createElement('div');
        this.highlightContainer.className = 'query-highlight-overlay';
        
        // Move textarea into wrapper and add highlight container
        wrapper.appendChild(this.highlightContainer);
        wrapper.appendChild(this.textarea);
        
        // Make textarea transparent background
        this.textarea.style.background = 'transparent';
        this.textarea.style.position = 'relative';
        this.textarea.style.zIndex = '2';
    }
    
    createLineNumbers() {
        this.lineNumbers = document.createElement('div');
        this.lineNumbers.className = 'query-line-numbers';
        
        // Insert line numbers before the wrapper
        const wrapper = this.textarea.closest('.query-editor-wrapper');
        wrapper.parentNode.insertBefore(this.lineNumbers, wrapper);
    }
    
    setupEventListeners() {
        this.textarea.addEventListener('input', () => {
            this.highlightSyntax();
            this.updateLineNumbers();
        });
        
        this.textarea.addEventListener('scroll', () => {
            this.syncScroll();
        });
        
        this.textarea.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
    }
    
    highlightSyntax() {
        const text = this.textarea.value;
        const highlightedText = this.processText(text);
        this.highlightContainer.innerHTML = highlightedText;
        this.syncScroll();
    }
    
    processText(text) {
        let processed = text;
        
        // Escape HTML
        processed = processed.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        
        // Highlight strings (single and double quotes)
        processed = processed.replace(/'([^']*(?:''[^']*)*)'/g, '<span class="sql-string">\'$1\'</span>');
        processed = processed.replace(/"([^"]*(?:""[^"]*)*)"/g, '<span class="sql-string">"$1"</span>');
        
        // Highlight numbers
        processed = processed.replace(/\\b\\d+(\\.\\d+)?\\b/g, '<span class="sql-number">$&</span>');
        
        // Highlight comments
        processed = processed.replace(/--.*$/gm, '<span class="sql-comment">$&</span>');
        processed = processed.replace(/\\/\\*[\\s\\S]*?\\*\\//g, '<span class="sql-comment">$&</span>');
        
        // Highlight keywords
        this.keywords.forEach(keyword => {
            const regex = new RegExp(`\\\\b${keyword}\\\\b`, 'gi');
            processed = processed.replace(regex, `<span class="sql-keyword">${keyword.toUpperCase()}</span>`);
        });
        
        // Highlight data types
        this.dataTypes.forEach(type => {
            const regex = new RegExp(`\\\\b${type}\\\\b`, 'gi');
            processed = processed.replace(regex, `<span class="sql-datatype">${type.toUpperCase()}</span>`);
        });
        
        // Highlight functions
        this.functions.forEach(func => {
            const regex = new RegExp(`\\\\b${func}(?=\\\\s*\\\\()`, 'gi');
            processed = processed.replace(regex, `<span class="sql-function">${func.toUpperCase()}</span>`);
        });
        
        // Highlight table names
        this.tableNames.forEach(table => {
            const regex = new RegExp(`\\\\b${table}\\\\b`, 'gi');
            processed = processed.replace(regex, `<span class="sql-table">${table}</span>`);
        });
        
        // Highlight column names
        this.columnNames.forEach(column => {
            const regex = new RegExp(`\\\\b${column}\\\\b`, 'gi');
            processed = processed.replace(regex, `<span class="sql-column">${column}</span>`);
        });
        
        return processed;
    }
    
    updateLineNumbers() {
        const lines = this.textarea.value.split('\\n');
        const lineNumbersHTML = lines.map((_, index) => 
            `<div class="line-number">${index + 1}</div>`
        ).join('');
        
        this.lineNumbers.innerHTML = lineNumbersHTML;
    }
    
    syncScroll() {
        if (this.highlightContainer) {
            this.highlightContainer.scrollTop = this.textarea.scrollTop;
            this.highlightContainer.scrollLeft = this.textarea.scrollLeft;
        }
        
        if (this.lineNumbers) {
            this.lineNumbers.scrollTop = this.textarea.scrollTop;
        }
    }
    
    handleKeydown(e) {
        // Auto-indent on Enter
        if (e.key === 'Enter') {
            const value = this.textarea.value;
            const selectionStart = this.textarea.selectionStart;
            const lineStart = value.lastIndexOf('\\n', selectionStart - 1) + 1;
            const currentLine = value.substring(lineStart, selectionStart);
            const indent = currentLine.match(/^\\s*/)[0];
            
            // Add extra indent after certain keywords
            const shouldIndent = /\\b(SELECT|FROM|WHERE|JOIN|GROUP|ORDER|HAVING)\\s*$/i.test(currentLine.trim());
            const extraIndent = shouldIndent ? '  ' : '';
            
            setTimeout(() => {
                const newSelectionStart = this.textarea.selectionStart;
                this.textarea.value = this.textarea.value.substring(0, newSelectionStart) + 
                                   indent + extraIndent + 
                                   this.textarea.value.substring(newSelectionStart);
                this.textarea.selectionStart = this.textarea.selectionEnd = newSelectionStart + indent.length + extraIndent.length;
                this.highlightSyntax();
                this.updateLineNumbers();
            }, 0);
        }
        
        // Tab for indentation
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.textarea.selectionStart;
            const end = this.textarea.selectionEnd;
            
            this.textarea.value = this.textarea.value.substring(0, start) + 
                                '  ' + 
                                this.textarea.value.substring(end);
            
            this.textarea.selectionStart = this.textarea.selectionEnd = start + 2;
            this.highlightSyntax();
        }
    }
    
    // Auto-completion functionality
    getCompletions(text, position) {
        const currentWord = this.getCurrentWord(text, position);
        const completions = [];
        
        // Add keyword completions
        this.keywords.forEach(keyword => {
            if (keyword.toLowerCase().startsWith(currentWord.toLowerCase())) {
                completions.push({
                    text: keyword,
                    type: 'keyword',
                    description: 'SQL Keyword'
                });
            }
        });
        
        // Add table completions
        this.tableNames.forEach(table => {
            if (table.toLowerCase().startsWith(currentWord.toLowerCase())) {
                completions.push({
                    text: table,
                    type: 'table',
                    description: 'Table Name'
                });
            }
        });
        
        // Add column completions
        this.columnNames.forEach(column => {
            if (column.toLowerCase().startsWith(currentWord.toLowerCase())) {
                completions.push({
                    text: column,
                    type: 'column',
                    description: 'Column Name'
                });
            }
        });
        
        return completions;
    }
    
    getCurrentWord(text, position) {
        const beforeCursor = text.substring(0, position);
        const afterCursor = text.substring(position);
        
        const wordBefore = beforeCursor.match(/[a-zA-Z_][a-zA-Z0-9_]*$/);
        const wordAfter = afterCursor.match(/^[a-zA-Z0-9_]*/);
        
        const before = wordBefore ? wordBefore[0] : '';
        const after = wordAfter ? wordAfter[0] : '';
        
        return before + after;
    }
}