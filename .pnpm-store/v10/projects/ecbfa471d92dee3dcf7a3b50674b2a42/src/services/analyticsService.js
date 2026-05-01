import { api } from '@/lib/api'
import { API_ENDPOINTS } from '@/constants/endpoints.js'

export async function fetchSummary() {
  const response = await  api.get(API_ENDPOINTS.ANALYTICS.SUMMARY)
  return response.data
}

export async function downloadCSV(type) {
  const endpoint = type === 'appointments'
    ? API_ENDPOINTS.ANALYTICS.EXPORT_APPOINTMENTS
    : API_ENDPOINTS.ANALYTICS.EXPORT_CONSULTATIONS

  const response = await api.get(endpoint, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = `${type}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}
