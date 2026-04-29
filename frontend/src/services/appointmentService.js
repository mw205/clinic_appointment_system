import { API_ENDPOINTS } from '@/constants/endpoints'
import { api } from '@/lib/api'

const appointmentUrl = (id) => `${API_ENDPOINTS.APPOINTMENTS.BASE}${id}/`
const appointmentActionUrl = (id, action) => `${appointmentUrl(id)}${action}/`

const extractErrorDetailString = (value) => {
  const match = value.match(/'message':\s*ErrorDetail\(string='([^']+)'/)
  return match?.[1] || value
}

const normalizeErrorValue = (value) => {
  if (!value) {
    return ''
  }

  if (typeof value === 'string') {
    return extractErrorDetailString(value)
  }

  if (Array.isArray(value)) {
    return value.map(normalizeErrorValue).filter(Boolean).join(', ')
  }

  if (typeof value === 'object') {
    if (value.message || value.detail || value.error) {
      return normalizeErrorValue(value.message || value.detail || value.error)
    }

    return Object.values(value).map(normalizeErrorValue).filter(Boolean).join(', ')
  }

  return String(value)
}

export const normalizeApiError = (error, fallback = 'Something went wrong. Please try again.') => {
  const data = error.response?.data

  if (!data) {
    return 'Unable to reach the server. Please check your connection.'
  }

  if (typeof data === 'string') {
    return normalizeErrorValue(data) || fallback
  }

  if (data.message || data.detail || data.error) {
    return normalizeErrorValue(data.message || data.detail || data.error) || fallback
  }

  const fieldErrors = data.errors || data.details || data
  if (fieldErrors && typeof fieldErrors === 'object') {
    return Object.entries(fieldErrors)
      .map(([field, value]) => {
        const message = normalizeErrorValue(value)
        return field === 'non_field_errors' ? message : `${field}: ${message}`
      })
      .filter(Boolean)
      .join('\n')
  }

  return fallback
}

export const getAppointments = async (params = {}) => {
  const response = await api.get(API_ENDPOINTS.APPOINTMENTS.BASE, { params })
  return response.data
}

export const getAppointment = async (id) => {
  const response = await api.get(appointmentUrl(id))
  return response.data
}

export const createAppointment = async (payload) => {
  const response = await api.post(API_ENDPOINTS.APPOINTMENTS.BASE, payload)
  return response.data
}

export const cancelAppointment = async (id) => {
  const response = await api.post(appointmentActionUrl(id, 'cancel'))
  return response.data
}

export const rescheduleAppointment = async (id, payload) => {
  const response = await api.post(appointmentActionUrl(id, 'reschedule'), payload)
  return response.data
}

export const getAvailableSlots = async (params = {}) => {
  const response = await api.get(API_ENDPOINTS.SCHEDULING.AVAILABLE_SLOTS, { params })
  return response.data
}
