/**
 * Theme Manager - Handles dark/light theme switching
 */

(function() {
    'use strict';

    const THEME_KEY = 'timetable_theme';
    const THEME_DARK = 'dark';
    const THEME_LIGHT = 'light';

    /**
     * Theme Manager Class
     */
    class ThemeManager {
        constructor() {
            this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
            this.init();
        }

        /**
         * Initialize theme manager
         */
        init() {
            // Check if theme was pre-applied to html element (from inline script)
            if (document.documentElement.classList.contains('light-theme-loading')) {
                document.documentElement.classList.remove('light-theme-loading');
                this.currentTheme = THEME_LIGHT;
            }
            
            // Apply theme immediately (before page renders)
            this.applyTheme(this.currentTheme, false);
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setupToggle());
            } else {
                this.setupToggle();
            }

            // Listen for system theme changes
            this.watchSystemTheme();
        }

        /**
         * Get stored theme from localStorage
         */
        getStoredTheme() {
            try {
                return localStorage.getItem(THEME_KEY);
            } catch (e) {
                console.warn('localStorage not available:', e);
                return null;
            }
        }

        /**
         * Store theme in localStorage
         */
        storeTheme(theme) {
            try {
                localStorage.setItem(THEME_KEY, theme);
            } catch (e) {
                console.warn('Failed to store theme:', e);
            }
        }

        /**
         * Get system theme preference
         */
        getSystemTheme() {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                return THEME_LIGHT;
            }
            return THEME_DARK;
        }

        /**
         * Watch for system theme changes
         */
        watchSystemTheme() {
            if (window.matchMedia) {
                const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
                
                // Modern browsers
                if (mediaQuery.addEventListener) {
                    mediaQuery.addEventListener('change', (e) => {
                        // Only auto-switch if user hasn't set a preference
                        if (!this.getStoredTheme()) {
                            this.applyTheme(e.matches ? THEME_LIGHT : THEME_DARK);
                        }
                    });
                }
                // Older browsers
                else if (mediaQuery.addListener) {
                    mediaQuery.addListener((e) => {
                        if (!this.getStoredTheme()) {
                            this.applyTheme(e.matches ? THEME_LIGHT : THEME_DARK);
                        }
                    });
                }
            }
        }

        /**
         * Apply theme to the page
         */
        applyTheme(theme, animate = true) {
            const body = document.body;
            const html = document.documentElement;
            
            // Add animation class
            if (animate) {
                body.classList.add('theme-switching');
                setTimeout(() => body.classList.remove('theme-switching'), 300);
            }

            // Apply theme
            if (theme === THEME_LIGHT) {
                body.classList.add('light-theme');
                html.classList.add('light-theme');
            } else {
                body.classList.remove('light-theme');
                html.classList.remove('light-theme');
            }

            // Remove the inline style set by the anti-flash inline script
            // (body now has the correct class so CSS takes over)
            document.documentElement.style.removeProperty('background');
            document.documentElement.style.removeProperty('min-height');

            this.currentTheme = theme;
            this.storeTheme(theme);

            // Update toggle button if it exists
            this.updateToggleButton();

            // Dispatch custom event for other components
            document.dispatchEvent(new CustomEvent('themeChanged', {
                detail: { theme: theme }
            }));
        }

        /**
         * Toggle between themes
         */
        toggleTheme() {
            const newTheme = this.currentTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK;
            this.applyTheme(newTheme);

            // Show toast notification if available
            if (typeof showToast === 'function') {
                const themeName = newTheme === THEME_LIGHT ? 'Light' : 'Dark';
                showToast(`${themeName} theme activated`, 'success', 2000);
            }
        }

        /**
         * Setup toggle button
         */
        setupToggle() {
            console.log('Setting up theme toggle button...');
            
            // Create toggle button if it doesn't exist
            let toggleBtn = document.getElementById('themeToggle');
            
            if (!toggleBtn) {
                console.log('Creating new theme toggle button');
                toggleBtn = this.createToggleButton();
                document.body.appendChild(toggleBtn);
                console.log('Theme toggle button added to page');
            } else {
                console.log('Theme toggle button already exists');
            }

            // Add click handler
            toggleBtn.addEventListener('click', () => this.toggleTheme());

            // Add keyboard shortcut (Ctrl+Shift+T)
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                    e.preventDefault();
                    this.toggleTheme();
                }
            });

            // Update button state
            this.updateToggleButton();
            
            console.log('Theme toggle button setup complete');
        }

        /**
         * Create toggle button element
         */
        createToggleButton() {
            const button = document.createElement('button');
            button.id = 'themeToggle';
            button.className = 'theme-toggle';
            button.setAttribute('aria-label', 'Toggle theme');
            button.setAttribute('title', 'Switch between dark and light theme (Ctrl+Shift+T)');
            
            button.innerHTML = `
                <span class="theme-toggle-icon" id="themeToggleIcon">
                    🌙
                </span>
                <span class="theme-toggle-label" id="themeToggleLabel">
                    Dark
                </span>
            `;
            
            return button;
        }

        /**
         * Update toggle button state
         */
        updateToggleButton() {
            const icon = document.getElementById('themeToggleIcon');
            const label = document.getElementById('themeToggleLabel');
            
            if (icon && label) {
                if (this.currentTheme === THEME_LIGHT) {
                    icon.textContent = '☀️';
                    label.textContent = 'Light';
                } else {
                    icon.textContent = '🌙';
                    label.textContent = 'Dark';
                }
            }
        }

        /**
         * Get current theme
         */
        getCurrentTheme() {
            return this.currentTheme;
        }

        /**
         * Check if light theme is active
         */
        isLightTheme() {
            return this.currentTheme === THEME_LIGHT;
        }

        /**
         * Check if dark theme is active
         */
        isDarkTheme() {
            return this.currentTheme === THEME_DARK;
        }

        /**
         * Reset to system theme
         */
        resetToSystemTheme() {
            try {
                localStorage.removeItem(THEME_KEY);
            } catch (e) {
                console.warn('Failed to remove theme preference:', e);
            }
            this.applyTheme(this.getSystemTheme());
        }
    }

    // Initialize theme manager
    window.themeManager = new ThemeManager();

    // Expose API for other scripts
    window.toggleTheme = () => window.themeManager.toggleTheme();
    window.getCurrentTheme = () => window.themeManager.getCurrentTheme();
    window.setTheme = (theme) => window.themeManager.applyTheme(theme);

})();

/**
 * Chart.js theme integration
 * Updates Chart.js default colors when theme changes
 */
document.addEventListener('themeChanged', function(e) {
    const isLight = e.detail.theme === 'light';
    
    // Update Chart.js defaults if Chart is loaded
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = isLight ? '#666666' : '#b4bab7';
        Chart.defaults.borderColor = isLight ? '#d0d0d0' : '#686868';
        
        // Trigger chart refresh if charts exist
        document.dispatchEvent(new CustomEvent('chartThemeChanged', {
            detail: { isLight: isLight }
        }));
    }
});

console.log('Theme Manager initialized - Current theme:', window.themeManager.getCurrentTheme());
