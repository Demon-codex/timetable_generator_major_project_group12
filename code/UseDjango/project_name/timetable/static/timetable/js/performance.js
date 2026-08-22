/**
 * Performance Optimization - Lazy Loading for Images and Heavy Content
 */

(function() {
    'use strict';

    /**
     * Lazy Load Images
     */
    function initLazyLoading() {
        // Check if IntersectionObserver is supported
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.add('loaded');
                            observer.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            // Observe all images with data-src attribute
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for browsers that don't support IntersectionObserver
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }

    /**
     * Lazy Load Content Sections
     */
    function initContentLazyLoading() {
        if ('IntersectionObserver' in window) {
            const contentObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        element.classList.add('loaded');
                        
                        // Trigger any deferred initialization
                        if (element.dataset.lazyInit) {
                            const initFunction = window[element.dataset.lazyInit];
                            if (typeof initFunction === 'function') {
                                initFunction(element);
                            }
                        }
                        
                        observer.unobserve(element);
                    }
                });
            }, {
                rootMargin: '100px 0px',
                threshold: 0.01
            });

            // Observe all elements with lazy-load class
            document.querySelectorAll('.lazy-load').forEach(element => {
                contentObserver.observe(element);
            });
        } else {
            // Fallback: load all content immediately
            document.querySelectorAll('.lazy-load').forEach(element => {
                element.classList.add('loaded');
            });
        }
    }

    /**
     * Debounce function to limit rate of function calls
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Throttle function to ensure function is called at most once per interval
     */
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    /**
     * Virtual Scrolling for Large Lists
     */
    class VirtualScroller {
        constructor(container, options = {}) {
            this.container = typeof container === 'string' 
                ? document.querySelector(container) 
                : container;
            
            if (!this.container) return;

            this.options = {
                itemHeight: options.itemHeight || 50,
                buffer: options.buffer || 5,
                items: options.items || [],
                renderItem: options.renderItem || (item => `<div>${item}</div>`)
            };

            this.visibleStart = 0;
            this.visibleEnd = 0;
            
            this.init();
        }

        init() {
            this.container.style.overflow = 'auto';
            this.container.style.position = 'relative';
            
            this.viewport = document.createElement('div');
            this.viewport.style.position = 'absolute';
            this.viewport.style.top = '0';
            this.viewport.style.left = '0';
            this.viewport.style.right = '0';
            
            const totalHeight = this.options.items.length * this.options.itemHeight;
            this.container.innerHTML = '';
            this.container.style.height = `${Math.min(totalHeight, 600)}px`;
            
            this.spacer = document.createElement('div');
            this.spacer.style.height = `${totalHeight}px`;
            this.container.appendChild(this.spacer);
            this.container.appendChild(this.viewport);
            
            this.onScroll = throttle(() => this.render(), 16);
            this.container.addEventListener('scroll', this.onScroll);
            
            this.render();
        }

        render() {
            const scrollTop = this.container.scrollTop;
            const containerHeight = this.container.clientHeight;
            
            this.visibleStart = Math.max(0, Math.floor(scrollTop / this.options.itemHeight) - this.options.buffer);
            this.visibleEnd = Math.min(
                this.options.items.length,
                Math.ceil((scrollTop + containerHeight) / this.options.itemHeight) + this.options.buffer
            );
            
            const visibleItems = this.options.items.slice(this.visibleStart, this.visibleEnd);
            
            this.viewport.innerHTML = visibleItems
                .map((item, index) => {
                    const actualIndex = this.visibleStart + index;
                    return `
                        <div style="
                            position: absolute;
                            top: ${actualIndex * this.options.itemHeight}px;
                            height: ${this.options.itemHeight}px;
                            left: 0;
                            right: 0;
                        ">
                            ${this.options.renderItem(item, actualIndex)}
                        </div>
                    `;
                })
                .join('');
        }

        updateItems(items) {
            this.options.items = items;
            const totalHeight = items.length * this.options.itemHeight;
            this.spacer.style.height = `${totalHeight}px`;
            this.render();
        }
    }

    /**
     * Optimize table rendering for large datasets
     */
    function optimizeLargeTables() {
        document.querySelectorAll('table[data-optimize="true"]').forEach(table => {
            const tbody = table.querySelector('tbody');
            if (!tbody) return;

            const rows = Array.from(tbody.querySelectorAll('tr'));
            if (rows.length < 50) return; // Only optimize if more than 50 rows

            // Hide rows that are not in viewport
            const optimizeTableScroll = throttle(() => {
                const rect = table.getBoundingClientRect();
                const viewportTop = 0;
                const viewportBottom = window.innerHeight;

                rows.forEach((row, index) => {
                    const rowRect = row.getBoundingClientRect();
                    const isVisible = rowRect.bottom >= viewportTop && rowRect.top <= viewportBottom;
                    
                    if (!isVisible && index > 20) { // Keep first 20 rows always rendered
                        row.style.display = 'none';
                    } else {
                        row.style.display = '';
                    }
                });
            }, 100);

            window.addEventListener('scroll', optimizeTableScroll);
            optimizeTableScroll(); // Initial call
        });
    }

    /**
     * Initialize performance optimizations
     */
    function initPerformanceOptimizations() {
        // Lazy load images
        initLazyLoading();
        
        // Lazy load content sections
        initContentLazyLoading();
        
        // Optimize large tables
        optimizeLargeTables();

        // Add loading indicators for async operations
        const asyncButtons = document.querySelectorAll('[data-async="true"]');
        asyncButtons.forEach(button => {
            button.addEventListener('click', function() {
                if (!this.disabled) {
                    this.classList.add('loading');
                    this.setAttribute('data-original-text', this.textContent);
                    this.textContent = 'Loading...';
                }
            });
        });
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPerformanceOptimizations);
    } else {
        initPerformanceOptimizations();
    }

    // Expose utilities globally
    window.performanceUtils = {
        debounce,
        throttle,
        VirtualScroller,
        initLazyLoading,
        initContentLazyLoading
    };

})();

console.log('Performance optimization utilities loaded');
