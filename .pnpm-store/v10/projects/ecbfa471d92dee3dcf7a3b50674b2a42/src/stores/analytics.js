import { ref , computed} from 'vue'
import { defineStore } from 'pinia'
import { fetchSummary, downloadCSV } from '@/services/analyticsService'

export const useAnalyticsStore = defineStore('analytics', () => {
  const summary = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const filter = ref('')

  const filterByStatus = computed(() => {
    const rows = summary.value?.appointment_status_counts
      ?? summary.value?.group_by_status
      ?? []
    if (!filter.value) return rows
    return rows.filter((row) => row.status === filter.value)
  })

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

  return { summary, loading, error, filter,filterByStatus, loadAll, exportCSV }
})
