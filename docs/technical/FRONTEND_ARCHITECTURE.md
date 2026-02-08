# Frontend Architecture (The "Boring Stack")

**Last Updated:** February 2026
**Tech Stack:** Vanilla JS (ES6+), Alpine.js 3.x, Tailwind CSS, Jinja2.

## 1. Philosophy: "No Build Step"

Tactics uses a zero-compile frontend architecture. We serve ES Modules directly to the browser.
- **Why?**: Eliminates "Webpack fatigue", simplifies debugging (WYSIWYG), and ensures instant deployments.
- **Performance**: Scripts are loaded with `defer`, and Alpine.js initializes reactivity only after the DOM is ready.

---

## 2. Directory Structure

```text
/static/js/
├── app.js                  # Main entry point (Alpine init)
├── core/                   # Singleton Infrastructure
│   ├── api.js              # Robust Fetch Wrapper (Error Handling, Toasts)
│   ├── store.js            # Global State (User, Toasts, Sidebar)
│   └── analytics.js        # Event Tracking & Web Vitals
└── components/             # Business Logic (Alpine Data)
    ├── crm-dashboard.js    # Logic for CRM / LTV view
    ├── mmm-dashboard.js    # Logic for Budget Optimizer
    ├── toast-notification.js # UI Alerts
    ├── cookie-consent.js   # GDPR Compliance
    └── metric-explainer.js # AI-driven metric interpretations
```

---

## 3. Core Modules

### A. API Wrapper (`core/api.js`)
All HTTP requests **MUST** use the global `api` object.
- **Features**:
  - Auto-injects headers (JSON).
  - Centralized Error Handling (401, 403, 500).
  - Toasts: Triggers UI alerts on failure automatically.
- **Usage**:
  ```javascript
  import { api } from '../core/api.js';
  const data = await api.get('/api/dashboard-data');
  ```

### B. Global Store (`core/store.js`)
We use `Alpine.store()` for cross-component state.
- **Stores**:
  - `toasts`: Manages alert notifications.
  - `user`: User profile and preferences.
  - `app`: UI state (Sidebar toggle, Loading indicators).

---

## 4. Component Pattern

We generally use **Alpine.data()** to encapsulate complex logic, keeping HTML templates clean.

**Example**:
```javascript
// static/js/components/example.js
export default () => ({
    loading: false,
    data: [],
    
    async init() {
        this.loading = true;
        this.data = await api.get('/endpoint');
        this.loading = false;
    }
});
```

**Template**:
```html
<div x-data="exampleComponent()">
    <span x-show="loading">Loading...</span>
</div>
```

---

## 5. CSS & Theming

- **Framework**: Tailwind CSS (Utility First).
- **Customization**: Defined in `static/css/style.css` (TailAdmin port).
- **Dark Mode**: Native Tailwind `dark:` classes, toggled via `Alpine.store('app').darkMode`.
