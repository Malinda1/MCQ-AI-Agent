/**
 * Professional MCQ Generator - Fixed JavaScript
 * FIXED: Tab switching and file upload functionality
 */

class MCQGenerator {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileUpload();
        this.setDefaultValues();
    }

    setupEventListeners() {
        // FIXED: Tab switching with proper event listeners
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = e.currentTarget.dataset.tab;
                this.showTab(tabName, e.currentTarget);
            });
        });

        // Form submissions
        document.getElementById('domain-form').addEventListener('submit', (e) => {
            this.handleDomainFormSubmit(e);
        });

        document.getElementById('document-form').addEventListener('submit', (e) => {
            this.handleDocumentFormSubmit(e);
        });

        // Real-time validation
        this.setupFormValidation();
    }

    setupFormValidation() {
        // Domain input validation
        const domainInput = document.getElementById('domain');
        if (domainInput) {
            domainInput.addEventListener('input', (e) => {
                this.validateDomainInput(e.target);
            });
        }

        // Email validation
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                this.validateEmailInput(e.target);
            });
        });

        // Number input validation
        const numberInputs = document.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.validateNumberInput(e.target);
            });
        });
    }

    setupFileUpload() {
        const fileInput = document.getElementById('document');
        const uploadDisplay = document.querySelector('.file-upload-display');

        if (!fileInput || !uploadDisplay) {
            console.warn('File upload elements not found');
            return;
        }

        // FIXED: File selection event
        fileInput.addEventListener('change', (e) => {
            console.log('File selected:', e.target.files[0]);
            this.handleFileSelection(e.target.files[0], uploadDisplay);
        });

        // FIXED: Drag and drop functionality
        const uploadWrapper = document.querySelector('.file-upload-wrapper');
        
        if (uploadWrapper) {
            uploadWrapper.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadWrapper.classList.add('drag-over');
            });

            uploadWrapper.addEventListener('dragleave', (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadWrapper.classList.remove('drag-over');
            });

            uploadWrapper.addEventListener('drop', (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadWrapper.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    this.handleFileSelection(files[0], uploadDisplay);
                }
            });

            // FIXED: Click handler for the display area
            uploadDisplay.addEventListener('click', () => {
                fileInput.click();
            });
        }
    }

    handleFileSelection(file, displayElement) {
        if (!file) {
            console.log('No file selected');
            return;
        }

        console.log('Processing file:', file.name, file.type, file.size);

        const validTypes = ['.pdf', '.docx', '.pptx', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!validTypes.includes(fileExtension)) {
            this.showFileError(displayElement, 'Invalid file type. Please select PDF, DOCX, PPTX, or TXT files.');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            this.showFileError(displayElement, 'File size too large. Please select a file smaller than 10MB.');
            return;
        }

        this.showFileSuccess(displayElement, file);
    }

    showFileSuccess(displayElement, file) {
        displayElement.innerHTML = `
            <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
            <span style="color: var(--success-color);">File selected: ${file.name}</span>
            <small>Size: ${this.formatFileSize(file.size)} | Click to change</small>
        `;
        displayElement.style.borderColor = 'var(--success-color)';
        displayElement.style.background = 'rgba(5, 150, 105, 0.05)';
    }

    showFileError(displayElement, message) {
        displayElement.innerHTML = `
            <i class="fas fa-exclamation-triangle" style="color: var(--error-color);"></i>
            <span style="color: var(--error-color);">${message}</span>
            <small>Please try again</small>
        `;
        displayElement.style.borderColor = 'var(--error-color)';
        displayElement.style.background = 'rgba(220, 38, 38, 0.05)';
        
        // Reset after 3 seconds
        setTimeout(() => {
            this.resetFileDisplay(displayElement);
        }, 3000);
    }

    resetFileDisplay(displayElement) {
        displayElement.innerHTML = `
            <i class="fas fa-file-upload"></i>
            <span>Choose file or drag and drop</span>
            <small>Supported: PDF, DOCX, PPTX, TXT</small>
        `;
        displayElement.style.borderColor = 'var(--border-color)';
        displayElement.style.background = 'var(--bg-input)';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    validateDomainInput(input) {
        const value = input.value.trim();
        if (value.length < 2) {
            this.showInputError(input, 'Domain must be at least 2 characters long');
        } else {
            this.clearInputError(input);
        }
    }

    validateEmailInput(input) {
        const value = input.value.trim();
        if (value && !this.isValidEmail(value)) {
            this.showInputError(input, 'Please enter a valid email address');
        } else {
            this.clearInputError(input);
        }
    }

    validateNumberInput(input) {
        const value = parseInt(input.value);
        const min = parseInt(input.min) || 1;
        const max = parseInt(input.max) || 50;
        
        if (value < min || value > max) {
            this.showInputError(input, `Value must be between ${min} and ${max}`);
        } else {
            this.clearInputError(input);
        }
    }

    showInputError(input, message) {
        input.style.borderColor = 'var(--error-color)';
        input.style.boxShadow = '0 0 0 3px rgba(220, 38, 38, 0.1)';
        
        let errorElement = input.parentNode.querySelector('.input-error');
        if (!errorElement) {
            errorElement = document.createElement('small');
            errorElement.className = 'input-error';
            errorElement.style.color = 'var(--error-color)';
            errorElement.style.marginTop = '0.25rem';
            input.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    clearInputError(input) {
        input.style.borderColor = 'var(--border-color)';
        input.style.boxShadow = 'none';
        
        const errorElement = input.parentNode.querySelector('.input-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    setDefaultValues() {
        document.getElementById('count').value = 10;
        document.getElementById('doc-count').value = 10;
        document.getElementById('difficulty').value = 'medium';
        document.getElementById('doc-difficulty').value = 'medium';
        document.getElementById('source').value = 'main_brain';
    }

    // FIXED: Tab switching logic
    showTab(tabName, buttonElement) {
        console.log('Switching to tab:', tabName);
        
        // Remove active class from all tab contents immediately
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected tab content immediately (no setTimeout)
        const targetTab = document.getElementById(tabName + '-tab');
        if (targetTab) {
            targetTab.classList.add('active');
            console.log('Activated tab:', tabName + '-tab');
        } else {
            console.error('Tab not found:', tabName + '-tab');
        }
        
        // Add active class to clicked button
        buttonElement.classList.add('active');
    }

    async handleDomainFormSubmit(e) {
        e.preventDefault();
        
        const formData = this.collectDomainFormData();
        if (!this.validateDomainForm(formData)) {
            return;
        }
        
        await this.generateMCQs('/generate-domain-mcq', formData);
    }

    async handleDocumentFormSubmit(e) {
        e.preventDefault();
        
        const formData = this.collectDocumentFormData();
        if (!this.validateDocumentForm(formData)) {
            return;
        }
        
        await this.generateMCQsWithFile('/upload-document-mcq', formData);
    }

    collectDomainFormData() {
        return {
            domain: document.getElementById('domain').value.trim(),
            count: parseInt(document.getElementById('count').value),
            difficulty: document.getElementById('difficulty').value,
            source: document.getElementById('source').value,
            email: document.getElementById('email').value.trim() || null,
            custom_prompt: document.getElementById('custom-prompt').value.trim() || null
        };
    }

    collectDocumentFormData() {
        const formData = new FormData();
        const fileInput = document.getElementById('document');
        
        if (fileInput.files[0]) {
            formData.append('file', fileInput.files[0]);
        }
        
        formData.append('count', document.getElementById('doc-count').value);
        formData.append('difficulty', document.getElementById('doc-difficulty').value);
        formData.append('email', document.getElementById('doc-email').value.trim() || '');
        formData.append('custom_prompt', document.getElementById('doc-custom-prompt').value.trim() || '');
        
        return formData;
    }

    validateDomainForm(formData) {
        if (!formData.domain) {
            this.showError('Please enter a domain or topic');
            return false;
        }
        
        if (formData.count < 1 || formData.count > 50) {
            this.showError('Number of questions must be between 1 and 50');
            return false;
        }
        
        if (formData.email && !this.isValidEmail(formData.email)) {
            this.showError('Please enter a valid email address');
            return false;
        }
        
        return true;
    }

    validateDocumentForm(formData) {
        const fileInput = document.getElementById('document');
        
        if (!fileInput.files[0]) {
            this.showError('Please select a file');
            return false;
        }
        
        const count = parseInt(formData.get('count'));
        if (count < 1 || count > 50) {
            this.showError('Number of questions must be between 1 and 50');
            return false;
        }
        
        const email = formData.get('email');
        if (email && !this.isValidEmail(email)) {
            this.showError('Please enter a valid email address');
            return false;
        }
        
        return true;
    }

    async generateMCQs(endpoint, data) {
        this.showLoading();
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showSuccess(result);
            } else {
                this.showError(result.detail || result.message || 'An error occurred while generating MCQs');
            }
            
        } catch (error) {
            console.error('Network error:', error);
            this.showError('Network error: Unable to connect to the server. Please check your connection and try again.');
        }
    }

    async generateMCQsWithFile(endpoint, formData) {
        this.showLoading();
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showSuccess(result);
            } else {
                this.showError(result.detail || result.message || 'An error occurred while generating MCQs');
            }
            
        } catch (error) {
            console.error('Network error:', error);
            this.showError('Network error: Unable to connect to the server. Please check your connection and try again.');
        }
    }

    showLoading() {
        this.hideAllResults();
        const loadingElement = document.getElementById('loading');
        loadingElement.classList.remove('hidden');
        loadingElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    showSuccess(result) {
        this.hideAllResults();
        
        const successDiv = document.getElementById('success');
        const messageP = document.getElementById('success-message');
        
        messageP.innerHTML = `
            <strong>Generated ${result.mcq_count || 'your'} MCQs successfully!</strong><br>
            PDF has been created and uploaded to Google Drive.<br>
            ${result.email ? '<span style="color: var(--success-color);">✉️ Email notification sent successfully!</span>' : ''}
        `;
        
        // Setup download button
        const downloadBtn = document.getElementById('download-btn');
        downloadBtn.onclick = () => {
            const filename = result.pdf_path ? result.pdf_path.split('/').pop() : 'mcq_questions.pdf';
            this.downloadFile(`/download-pdf/${filename}`, filename);
        };
        
        // Setup copy button
        const copyBtn = document.getElementById('copy-btn');
        copyBtn.onclick = () => {
            if (result.drive_file_id) {
                const driveLink = `https://drive.google.com/file/d/${result.drive_file_id}/view`;
                this.copyToClipboard(driveLink);
            } else {
                this.showNotification('Drive link not available', 'warning');
            }
        };
        
        successDiv.classList.remove('hidden');
        successDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        this.showSuccessAnimation();
    }

    showError(message) {
        this.hideAllResults();
        
        const errorDiv = document.getElementById('error');
        const messageP = document.getElementById('error-message');
        
        messageP.textContent = message;
        errorDiv.classList.remove('hidden');
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    hideAllResults() {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('success').classList.add('hidden');
        document.getElementById('error').classList.add('hidden');
    }

    downloadFile(url, filename) {
        try {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showNotification('Download started!', 'success');
        } catch (error) {
            console.error('Download error:', error);
            this.showNotification('Download failed. Please try again.', 'error');
        }
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('Google Drive link copied to clipboard!', 'success');
        } catch (error) {
            console.error('Clipboard error:', error);
            this.fallbackCopyTextToClipboard(text);
        }
    }

    fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.position = 'fixed';
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showNotification('Link copied to clipboard!', 'success');
        } catch (error) {
            console.error('Fallback copy failed:', error);
            this.showNotification('Failed to copy link', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    showNotification(message, type = 'info') {
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'notification';
            document.body.appendChild(notification);
        }
        
        notification.textContent = message;
        notification.className = `notification notification-${type} show`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    showSuccessAnimation() {
        const successCard = document.getElementById('success');
        successCard.style.animation = 'successPulse 0.6s ease-in-out';
        
        setTimeout(() => {
            successCard.style.animation = '';
        }, 600);
    }
}

// Global function for backward compatibility
function showTab(tabName) {
    const button = document.querySelector(`[data-tab="${tabName}"]`);
    if (button && window.mcqGenerator) {
        window.mcqGenerator.showTab(tabName, button);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing MCQ Generator...');
    window.mcqGenerator = new MCQGenerator();
    
    // Add notification styles if they don't exist
    if (!document.querySelector('style[data-notification-styles]')) {
        const notificationStyles = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 0.5rem;
                color: white;
                font-weight: 600;
                z-index: 1000;
                transform: translateX(100%);
                transition: transform 0.3s ease-in-out;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.6);
            }
            
            .notification.show {
                transform: translateX(0);
            }
            
            .notification-success {
                background: #10b981;
            }
            
            .notification-error {
                background: #ef4444;
            }
            
            .notification-warning {
                background: #f59e0b;
            }
            
            .notification-info {
                background: #3b82f6;
            }
            
            @keyframes successPulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }
            
            .drag-over .file-upload-display {
                border-color: #3b82f6 !important;
                background: rgba(37, 99, 235, 0.05) !important;
                transform: scale(1.02);
            }
            
            @media (max-width: 768px) {
                .notification {
                    top: 10px;
                    right: 10px;
                    left: 10px;
                    transform: translateY(-100%);
                }
                
                .notification.show {
                    transform: translateY(0);
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.setAttribute('data-notification-styles', 'true');
        styleElement.textContent = notificationStyles;
        document.head.appendChild(styleElement);
    }
    
    // Test tab switching after initialization
    setTimeout(() => {
        console.log('Testing tab functionality...');
        const documentTab = document.getElementById('document-tab');
        const domainTab = document.getElementById('domain-tab');
        
        if (documentTab && domainTab) {
            console.log('Both tabs found - functionality should work');
        } else {
            console.error('Tab elements not found:', {
                documentTab: !!documentTab,
                domainTab: !!domainTab
            });
        }
    }, 1000);
});