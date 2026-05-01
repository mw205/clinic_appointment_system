import { API_ENDPOINTS } from '@/constants/endpoints'
import { api } from '@/lib/api'

const buildDetailUrl = (baseUrl, id) => `${baseUrl}${id}/`
const schedulingBaseUrl = API_ENDPOINTS.SCHEDULING.BASE
const schedulesBaseUrl = `${schedulingBaseUrl}${API_ENDPOINTS.SCHEDULING.SCHEDULES}`
const exceptionsBaseUrl = `${schedulingBaseUrl}${API_ENDPOINTS.SCHEDULING.EXCEPTIONS}`
const availableSlotsUrl = `${schedulesBaseUrl}${API_ENDPOINTS.SCHEDULING.AVAILABLE_SLOTS}`

export const getDoctors = async function (params = {}) {
  const response = await api.get(API_ENDPOINTS.ACCOUNTS.BASE + API_ENDPOINTS.ACCOUNTS.USERS, {
    params,
  })
  return response.data
}

export const getSchedules = async function (params = {}) {
  const response = await api.get(schedulesBaseUrl, {
    params,
  })
  return response.data
}

export const getSchedule = async function (id) {
  const response = await api.get(buildDetailUrl(schedulesBaseUrl, id))
  return response.data
}

export const createSchedule = async function (payload) {
  const response = await api.post(schedulesBaseUrl, payload)
  return response.data
}

export const updateSchedule = async function (id, payload) {
  const response = await api.patch(buildDetailUrl(schedulesBaseUrl, id), payload)
  return response.data
}

export const deleteSchedule = async function (id) {
  const response = await api.delete(buildDetailUrl(schedulesBaseUrl, id))
  return response.data
}

export const getAvailableSlots = async function (doctor_id, date) {
  const response = await api.get(availableSlotsUrl, {
    params: {
      doctor_id,
      date,
    },
  })
  return response.data
}

export const getExceptions = async function (params = {}) {
  const response = await api.get(exceptionsBaseUrl, {
    params,
  })
  return response.data
}

export const createException = async function (payload) {
  const response = await api.post(exceptionsBaseUrl, payload)
  return response.data
}

export const getException = async function (id) {
  const response = await api.get(buildDetailUrl(exceptionsBaseUrl, id))
  return response.data
}

export const updateException = async function (id, payload) {
  const response = await api.patch(buildDetailUrl(exceptionsBaseUrl, id), payload)
  return response.data
}

export const deleteException = async function (id) {
  const response = await api.delete(buildDetailUrl(exceptionsBaseUrl, id))
  return response.data
}
