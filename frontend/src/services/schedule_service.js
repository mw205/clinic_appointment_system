import { API_ENDPOINTS } from '@/constants/endpoints'
import { api } from '@/lib/api'

const buildDetailUrl = (baseUrl, id) => `${baseUrl}${id}/`

export const getDoctors = async function (params = {}) {
  const response = await api.get(API_ENDPOINTS.ACCOUNTS.BASE + API_ENDPOINTS.ACCOUNTS.USERS, {
    params,
  })
  return response.data
}

export const getSchedules = async function (params = {}) {
  const response = await api.get(API_ENDPOINTS.SCHEDULING.SCHEDULES, {
    params,
  })
  return response.data
}

export const getSchedule = async function (id) {
  const response = await api.get(buildDetailUrl(API_ENDPOINTS.SCHEDULING.SCHEDULES, id))
  return response.data
}

export const createSchedule = async function (payload) {
  const response = await api.post(API_ENDPOINTS.SCHEDULING.SCHEDULES, payload)
  return response.data
}

export const updateSchedule = async function (id, payload) {
  const response = await api.patch(buildDetailUrl(API_ENDPOINTS.SCHEDULING.SCHEDULES, id), payload)
  return response.data
}

export const deleteSchedule = async function (id) {
  const response = await api.delete(buildDetailUrl(API_ENDPOINTS.SCHEDULING.SCHEDULES, id))
  return response.data
}

export const getAvailableSlots = async function (doctor_id, date) {
  const response = await api.get(API_ENDPOINTS.SCHEDULING.AVAILABLE_SLOTS, {
    params: {
      doctor_id,
      date,
    },
  })
  return response.data
}

export const getExceptions = async function (params = {}) {
  const response = await api.get(API_ENDPOINTS.SCHEDULING.EXCEPTIONS, {
    params,
  })
  return response.data
}

export const createException = async function (payload) {
  const response = await api.post(API_ENDPOINTS.SCHEDULING.EXCEPTIONS, payload)
  return response.data
}

export const getException = async function (id) {
  const response = await api.get(buildDetailUrl(API_ENDPOINTS.SCHEDULING.EXCEPTIONS, id))
  return response.data
}

export const updateException = async function (id, payload) {
  const response = await api.patch(buildDetailUrl(API_ENDPOINTS.SCHEDULING.EXCEPTIONS, id), payload)
  return response.data
}

export const deleteException = async function (id) {
  const response = await api.delete(buildDetailUrl(API_ENDPOINTS.SCHEDULING.EXCEPTIONS, id))
  return response.data
}
