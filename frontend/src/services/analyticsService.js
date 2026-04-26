import { BASE_URL, getAuthenticantionHeaders } from './consultationService'

export async function fetchSummary() {
  const response = await fetch(`${BASE_URL}/analytics/summary/`, {
    headers: getAuthenticantionHeaders(),
  })
  if (!response.ok) throw new Error('error at fetching summary')
  return response.json()
}

export async function fetchPeakHours() {
  const response = await fetch(`${BASE_URL}/analytics/peakHours/`, {
    headers: getAuthenticantionHeaders(),
  })
  if (!response.ok) throw new Error('error at fetch peak hours')
  return response.json()
}

export async function fetchCSV(type) {
  const res = await fetch(`${BASE_URL}/analytics/export/${type}/`, {
    headers: getAuthenticantionHeaders(),
  })

  if (!res.ok) {
    throw new Error('error at fetching csv')
  }
  return await res.blob()
}
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
