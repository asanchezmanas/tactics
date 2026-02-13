/**
 * SOTA Analytics Abstraction Layer
 * 
 * Provides a unified interface for tracking user interactions, pageviews, and conversion events.
 * Designed to support multiple backends (GTM, GA4, Custom, Plausible) while maintaining privacy compliance.
 */

class AnalyticsService {
    constructor() {
        this.initialized = false;
        this.queue = [];
        this.providers = [];

        // Load settings from local storage or config
        this.debug = window.location.hostname === 'localhost';
    }

    /**
     * Initialize analytics providers and performance monitoring
     */
    init() {
        if (this.initialized) return;

        this.initialized = true;
        this.processQueue();

        // Track initial page view with device info
        this.track('page_view', {
            path: window.location.pathname,
            referrer: document.referrer,
            screen_width: window.innerWidth,
            screen_height: window.innerHeight,
            device_pixel_ratio: window.devicePixelRatio,
            connection: navigator.connection ? navigator.connection.effectiveType : 'unknown'
        });

        // Basic Web Vitals Monitoring (LCP, CLS)
        this.observePerformance();

        if (this.debug) console.log('[Analytics] Initialized with Performance Monitoring');
    }

    observePerformance() {
        if (!window.PerformanceObserver) return;

        try {
            // Layout Shift (CLS)
            new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (!entry.hadRecentInput) {
                        this.track('web_vital', { metric: 'CLS', value: entry.value, label: 'Cumulative Layout Shift' });
                    }
                }
            }).observe({ type: 'layout-shift', buffered: true });

            // Largest Contentful Paint (LCP)
            new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    this.track('web_vital', { metric: 'LCP', value: entry.startTime, label: 'Largest Contentful Paint' });
                }
            }).observe({ type: 'largest-contentful-paint', buffered: true });

        } catch (e) {
            // Browser might not support some observers
            if (this.debug) console.warn('[Analytics] Performance observers not fully supported');
        }
    }

    /**
     * Track a page view
     * @param {string} path 
     * @param {object} properties 
     */
    page(path = window.location.pathname, properties = {}) {
        this.track('page_view', { path, ...properties });
    }

    /**
     * Track a custom event
     * @param {string} eventName 
     * @param {object} properties 
     */
    track(eventName, properties = {}) {
        if (!this.initialized) {
            this.queue.push({ eventName, properties });
            return;
        }

        const payload = {
            event: eventName,
            timestamp: new Date().toISOString(),
            ...properties
        };

        if (this.debug) {
            console.log(`[Analytics] ${eventName}`, payload);
        }

        // Push to DataLayer (GTM/GA4)
        if (window.dataLayer) {
            window.dataLayer.push(payload);
        }
    }

    /**
     * Identify a user (e.g. after login)
     * @param {string} userId 
     * @param {object} traits 
     */
    identify(userId, traits = {}) {
        if (this.debug) console.log(`[Analytics] Identify ${userId}`, traits);

        if (window.dataLayer) {
            window.dataLayer.push({
                event: 'identify',
                userId: userId,
                ...traits
            });
        }
    }

    processQueue() {
        while (this.queue.length > 0) {
            const { eventName, properties } = this.queue.shift();
            this.track(eventName, properties);
        }
    }
}

export const analytics = new AnalyticsService();

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    analytics.init();
});
