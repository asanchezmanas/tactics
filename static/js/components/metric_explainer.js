/**
 * Metric Explainer Component
 * Manages the logic for fetching and displaying AI-driven metric explanations.
 */
export default function metricExplainer() {
    return {
        open: false,
        title: '',
        content: null,
        loading: false,

        /**
         * Fetches an explanation for a specific metric.
         * @param {string} category - The algorithm category (ltv, mmm, eclat, etc.)
         * @param {string} metricId - The ID of the metric to explain.
         * @param {number} value - The current value of the metric.
         */
        async explain(category, metricId, value) {
            this.title = 'Analizando m├®trica...';
            this.loading = true;
            this.open = true;
            this.content = null;

            try {
                const apiBase = window.location.origin;
                // Using the specific quick-explain endpoint
                const response = await fetch(`${apiBase}/api/explain/${category}/${metricId}/quick?value=${value}&locale=es`);

                if (!response.ok) {
                    throw new Error(`Error ${response.status}: No se pudo obtener la explicaci├│n.`);
                }

                const data = await response.json();

                this.content = data;
                this.title = data.metric_name;
            } catch (error) {
                console.error('[Explainer] Error:', error);
                this.content = {
                    what_it_means: 'Lo sentimos, hubo un error al procesar esta explicaci├│n. Por favor, int├®ntalo de nuevo.',
                    how_calculated: 'Error de comunicaci├│n con el motor de IA.',
                    caveats: ['Verifica tu conexi├│n a internet o contacta con soporte.']
                };
                this.title = 'Error de An├ílisis';
            } finally {
                this.loading = false;
            }
        },

        close() {
            this.open = false;
        }
    };
}
