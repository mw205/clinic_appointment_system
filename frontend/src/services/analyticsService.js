import { api } from '@/lib/api'

export async function fetchSummary() {
  const { data } = await api.get('/analytics/summary/')
  return data
}

export async function downloadCSV(type) {
  const { data } = await api.get(`/analytics/export/${type}/`, {
    responseType: 'blob',
  })

  const url = window.URL.createObjectURL(new Blob([data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `${type}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}
