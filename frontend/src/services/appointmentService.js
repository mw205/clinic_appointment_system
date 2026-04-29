import { API_ENDPOINTS } from '@/constants/endpoints'
import { api } from '@/lib/api'

const appointmentUrl = (id) => `${API_ENDPOINTS.APPOINTMENTS.BASE}${id}/`
const appointmentActionUrl = (id, action) => `${appointmentUrl(id)}${action}/`

export const normalizeApiError = (error, fallback = 'Something went wrong. Please try again.') => {
  const data = error.response?.data

  if (!data) {
    return 'Unable to reach the server. Please check your connection.'
  }

  if (typeof data === 'string') {
    return data
  }

  if (data.detail || data.message || data.error) {
    return data.detail || data.message || data.error
  }

  const fieldErrors = data.errors || data.details || data
  if (fieldErrors && typeof fieldErrors === 'object') {
    return Object.entries(fieldErrors)
      .map(([field, value]) => {
        const message = Array.isArray(value) ? value.join(', ') : value
        return field === 'non_field_errors' ? message : `${field}: ${message}`
      })
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
