/**
 * Core API Client
 * Wraps fetch with robust error handling and standardized response parsing.
 */

class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    /**
     * Main request handler
     * @param {string} endpoint 
     * @param {object} options 
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        const config = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);

            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                this.handleError(response.status, data);
                throw { status: response.status, ...data };
            }

            return data;

        } catch (error) {
            // Re-throw if it's already a handled API error
            if (error.status) throw error;

            // Handle network errors
            this.handleNetworkError(error);
            throw error;
        }
    }

    handleError(status, data) {
        const message = data.detail || 'An unexpected error occurred.';

        // Dispatch event for Toast notification
        window.dispatchEvent(new CustomEvent('toast:notify', {
            detail: {
                type: 'error',
                message: `Error ${status}: ${message}`
            }
        }));

        console.error(`[API Error ${status}]`, data);

        // Handle specific status codes
        if (status === 401) {
            // Redirect to login if unauthorized
            // window.location.href = '/signin';
        }
    }

    handleNetworkError(error) {
        window.dispatchEvent(new CustomEvent('toast:notify', {
            detail: {
                type: 'error',
                message: 'Network error. Please check your connection.'
            }
        }));
        console.error('[Network Error]', error);
    }

    get(endpoint, headers = {}) {
        return this.request(endpoint, { method: 'GET', headers });
    }

    post(endpoint, body, headers = {}) {
        return this.request(endpoint, { method: 'POST', body: JSON.stringify(body), headers });
    }

    put(endpoint, body, headers = {}) {
        return this.request(endpoint, { method: 'PUT', body: JSON.stringify(body), headers });
    }

    delete(endpoint, headers = {}) {
        return this.request(endpoint, { method: 'DELETE', headers });
    }
}

export const api = new ApiClient();
