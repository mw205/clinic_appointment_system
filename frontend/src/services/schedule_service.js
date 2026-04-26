import { API_ENDPOINTS } from '@/constants/endpoints'
import api from '@/lib/api'
const fetchSchedule = async function (doctor_id) {
  let response = await api.get(API_ENDPOINTS.SCHEDULING.SCHEDULES)
}
const saveWeeklySchedule = async function (doctor_id, schedule) {
  let response = await api.post(API_ENDPOINTS.SCHEDULING.SCHEDULES)
}
const fetchSlots = async function (doctor_id) {
  let response = await api.get(API_ENDPOINTS.SCHEDULING.EXCEPTIONS)
}
const saveException = async function (exception_data) {
  let response = await api.post(API_ENDPOINTS.SCHEDULING.EXCEPTIONS)
}
