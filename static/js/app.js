<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>{% block title %}Tactics | Future of Marketing{% endblock %}</title>
    <meta name="description"
        content="{% block description %}Advanced Marketing Analytics & Autonomous ROI Optimization. Tactics is the AI-driven engine for modern growth teams.{% endblock %}">
    <meta name="keywords" content="Marketing Mix Modeling, AI Marketing, ROI Optimization, Autonomous Growth, Tactics">
    <meta name="author" content="Tactics AI">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://tactics.ai/">
    <meta property="og:title" content="{% block og_title %}Tactics | Autonomous Marketing Intelligence{% endblock %}">
    <meta property="og:description"
        content="{% block og_description %}Stop guessing. Start calculating. Tactics uses Bayesian inference to optimize your marketing budget automatically.{% endblock %}">
    <meta property="og:image" content="https://tactics.ai/static/images/og-image.jpg">

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="https://tactics.ai/">
    <meta property="twitter:title"
        content="{% block twitter_title %}Tactics | Autonomous Marketing Intelligence{% endblock %}">
    <meta property="twitter:description"
        content="{% block twitter_description %}Stop guessing. Start calculating. Tactics uses Bayesian inference to optimize your marketing budget automatically.{% endblock %}">
    <meta property="twitter:image" content="https://tactics.ai/static/images/og-image.jpg">

    <!-- JSON-LD Schema -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Tactics",
      "applicationCategory": "BusinessApplication",
      "operatingSystem": "Cloud",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "description": "AI-powered Marketing Mix Modeling and Budget Optimization platform."
    }
    </script>
    <link href="https://fonts.googleapis.com" rel="preconnect" />
    <link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect" />
    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&amp;family=Manrope:wght@400;500;600;700;800&amp;display=swap"
        rel="stylesheet" />
    <link
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap"
        rel="stylesheet" />
    <script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>
    <script defer src="https://unpkg.com/@alpinejs/persist@3.x.x/dist/cdn.min.js"></script>
    <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    zIndex: {
                        '9999': '9999',
                        '99999': '99999',
                        '999': '999',
                        '99': '99',
                    },
                    colors: {
                        // TailAdmin compatibility
                        'gray-dark': '#1C2434',
                        'gray-light': '#F8FAFC',
                        'success-500': '#10B981',
                        'warning-500': '#F59E0B',
                        'error-500': '#EF4444',
                        'brand-500': '#4F46E5',
                        black: '#0F172A',
                        // Light Theme (Public)
                        background: "#FFFFFF",
                        surface: "#F8FAFC",
                        "surface-highlight": "#F1F5F9",
                        primary: "#4F46E5",
                        "primary-dark": "#3730a3",
                        "primary-soft": "rgba(79, 70, 229, 0.1)",
                        text: {
                            main: "#0F172A",
                            muted: "#475569",
                            dim: "#94A3B8"
                        },
                        border: {
                            light: "#E2E8F0",
                            subtle: "#CBD5E1"
                        }
                    },
                    fontFamily: {
                        display: ['"Manrope"', 'sans-serif'],
                        body: ['"Inter"', 'sans-serif'],
                    },
                    borderRadius: {
                        DEFAULT: "6px",
                        'lg': "8px",
                        'xl': "12px",
                        '2xl': "16px",
                        '3xl': "24px",
                    },
                    boxShadow: {
                        'theme-xs': '0px 1px 2px rgba(16, 24, 40, 0.05)',
                        'theme-sm': '0px 1px 3px rgba(16, 24, 40, 0.1), 0px 1px 2px rgba(16, 24, 40, 0.06)',
                        'theme-md': '0px 4px 8px -2px rgba(16, 24, 40, 0.1), 0px 2px 4px -2px rgba(16, 24, 40, 0.06)',
                        'theme-lg': '0px 12px 16px -4px rgba(16, 24, 40, 0.08), 0px 4px 6px -2px rgba(16, 24, 40, 0.03)',
                    }
                },
            },
        };
    </script>
    <style>
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--scrollbar-track, #f1f5f9);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--scrollbar-thumb, #cbd5e1);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--scrollbar-thumb-hover, #94a3b8);
        }
    </style>
    {% block head %}{% endblock %}
</head>

<body
    class="font-body antialiased selection:bg-primary/20 selection:text-primary min-h-screen flex flex-col {% block body_class %}bg-background text-text-main{% endblock %}">
    {% block nav %}{% endblock %}

    <main class="{% block main_class %}flex-grow{% endblock %}">
        {% block content %}{% endblock %}
    </main>

    {% include 'partials/footer.html' %}

    <!-- Global Toast Notifications -->
    <div x-data="toastNotification()" class="fixed bottom-4 right-4 z-99999 flex flex-col gap-2 pointer-events-none">
        <template x-for="item in items" :key="item.id">
            <div x-transition:enter="transition ease-out duration-300"
                x-transition:enter-start="opacity-0 translate-y-2" x-transition:enter-end="opacity-100 translate-y-0"
                x-transition:leave="transition ease-in duration-200"
                x-transition:leave-start="opacity-100 translate-y-0" x-transition:leave-end="opacity-0 translate-y-2"
                class="pointer-events-auto min-w-[300px] max-w-sm rounded-lg shadow-theme-lg bg-white dark:bg-boxdark border-l-4 p-4 text-sm"
                :class="getColor(item.type).replace('bg-', 'border-')">
                <div class="flex items-start gap-3">
                    <span class="material-symbols-outlined text-lg" :class="getColor(item.type).replace('bg-', 'text-')"
                        x-text="getIcon(item.type)"></span>
                    <div class="flex-1">
                        <p class="font-medium text-black dark:text-white" x-text="item.type.toUpperCase()"></p>
                        <p class="text-gray-500 dark:text-gray-400 mt-0.5" x-text="item.message"></p>
                    </div>
                    <button @click="$store.toasts.remove(item.id)" class="text-gray-400 hover:text-gray-600">
                        <span class="material-symbols-outlined text-lg">close</span>
                    </button>
                </div>
            </div>
        </template>
    </div>

    <!-- Cookie Consent Banner -->
    <div x-data="cookieConsent()" x-show="open" x-transition:enter="transition ease-out duration-300"
        x-transition:enter-start="translate-y-full opacity-0" x-transition:enter-end="translate-y-0 opacity-100"
        x-transition:leave="transition ease-in duration-200" x-transition:leave-start="translate-y-0 opacity-100"
        x-transition:leave-end="translate-y-full opacity-0"
        class="fixed bottom-0 left-0 right-0 z-50 flex flex-col items-center justify-between gap-4 border-t border-stroke bg-white px-4 py-8 shadow-default dark:border-strokedark dark:bg-boxdark md:flex-row md:px-8">
        <div class="mb-4 md:mb-0 md:w-2/3">
            <h4 class="mb-2 text-xl font-bold text-black dark:text-white">
                We value your privacy
            </h4>
            <p class="font-medium text-body">
                We use cookies to enhance your browsing experience, serve personalized ads or content, and analyze our
                traffic. By
                clicking "Accept All", you consent to our use of cookies.
            </p>
        </div>
        <div class="flex gap-4">
            <button @click="open = false"
                class="rounded border border-stroke bg-gray py-3 px-8 font-medium text-black hover:bg-opacity-90 dark:border-strokedark dark:bg-meta-4 dark:text-white dark:hover:bg-opacity-90">
                Cancel
            </button>
            <button @click="acceptAll()"
                class="rounded bg-primary py-3 px-8 font-medium text-white hover:bg-opacity-90">
                Accept All
            </button>
        </div>
    </div>

    <!-- Main Module -->
    <script type="module">
        import toastComponent from '/static/js/components/toast-notification.js';
        import cookieComponent from '/static/js/components/cookie-consent.js';

        document.addEventListener('alpine:init', () => {
            Alpine.data('toastNotification', toastComponent);
            Alpine.data('cookieConsent', cookieComponent);
        });
    </script>
    <script type="module" src="/static/js/app.js"></script>
    <script type="module" src="/static/js/core/analytics.js"></script>

    {% block scripts %}{% endblock %}
</body>

</html>
