/**
 * Tactics Unified Frontend Hub (V2)
 * Corrected Entry Point: Imports unified API and initializes Stores.
 */

import { api } from './core/api_v2.js';

// Global API Exposure for Legacy/Inline compatibility
window.tacticsApi = api;

// Alpine Store Initialization (Unified)
document.addEventListener('alpine:init', () => {
    // Analytics Store
    Alpine.store('analytics', {
        loading: false,
        metrics: {},
        async refresh() {
            this.loading = true;
            try {
                this.metrics = await api.get('/api/elite/metrics');
            } catch (e) {
                console.error('Analytics Refresh Error:', e);
            }
            this.loading = false;
        }
    });

    // Theme Store
    Alpine.store('theme', {
        darkMode: Alpine.$persist(true).as('darkMode'),
        toggle() {
            this.darkMode = !this.darkMode;
        }
    });

    console.log('[Tactics V2] Alpine Stores Ready');
});

console.log('[Tactics V2] Frontend Entry Point Initialized');
