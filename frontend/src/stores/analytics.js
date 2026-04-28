import { ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchSummary, downloadCSV } from '@/services/analyticsService'

export const useAnalyticsStore = defineStore('analytics', () => {
  const summary = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function loadAll() {
    loading.value = true
    error.value = null
    try {
      summary.value = await fetchSummary()
    } catch (e) {
      error.value = 'Could not load analytics.'
    } finally {
      loading.value = false
    }
  }

  async function exportCSV(type) {
    try {
      await downloadCSV(type)
    } catch (e) {
      error.value = 'Export failed.'
    }
  }

  return { summary, loading, error, loadAll, exportCSV }
})
