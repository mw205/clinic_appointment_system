import { ref } from 'vue';
import { defineStore } from "pinia";
import { fetchSummary, fetchPeakHours, fetchCSV, downloadBlob } from "@/services/analyticsService";

export const useAnalyticsStore = defineStore('analytics', () => {
    const summary = ref(null);
    const peakHours = ref(null);
    const loading = ref(false);
    const error = ref(null);

    async function loadAll() {
        loading.value = true;
        error.value = null;

        try {
            summary.value = await fetchSummary();
            peakHours.value = await fetchPeakHours();
        } catch (e) {
            error.value = 'error while loading analytics';
        }
        finally {
            loading.value = false;
        }
    }
    async function downloadCSV(type) {
        try {
            const blob = await fetchCSV(type);
            downloadBlob(blob, `${type}.csv`);
        } catch (e) {
            error.value = 'error at fetching the csv and dowloading it';
        }
    }
    return { summary, peakHours, loading, error, loadAll, downloadCSV };
})