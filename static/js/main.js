/**
 * Main Application Entry Point
 */
import { initStores } from './core/store.js';
import { api } from './core/api.js';

// Initialize Alpine Stores
initStores();

// Expose API globally for inline scripts (optional, for transition period)
window.tacticsApi = api;

console.log('[Tactics] Frontend App Initialized');
