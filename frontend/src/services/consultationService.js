import { API_ENDPOINTS } from '@/constants/endpoints.js'
import { api } from '@/lib/api.js'


export  async function fetchConsultation(appointmentId) {
  const response = await api.get((API_ENDPOINTS.CONSULTATIONS.LIST), {
    params: { appointment: appointmentId },
  })
  return response.data
}
export async function createConsultation(newData) {
  const response = await api.post((API_ENDPOINTS.CONSULTATIONS.LIST), newData)
  return response.data
}
export async function updateConsultation(id,newData){
  const response = await api.patch((API_ENDPOINTS.CONSULTATIONS.DETAIL(id)), newData)
  return response.data
}
export async function completeConsultation(id){
  const response = await api.post((API_ENDPOINTS.CONSULTATIONS.COMPLETE(id)))
  return response.data
}
export async function fetchConsultationSummary(id) {
  const response = await api.get((API_ENDPOINTS.CONSULTATIONS.SUMMARY(id)))
  return response.data
}
export async function fetchConsultationByAppointment(appointmentId) {
  const response = await api.get(
    `${(API_ENDPOINTS.CONSULTATIONS.LIST)}by-appointment/${appointmentId}/`,
  )
  return response.data
}
export async function createPrescription(newData) {
  const response = await api.post((API_ENDPOINTS.PRESCRIPTIONS.LIST), newData)
  return response.data
}
export async function deletePrescription(id) {
  const response = await api.delete((API_ENDPOINTS.PRESCRIPTIONS.DETAIL(id)))
  return response.data
}
export async function createTest(newData) {
  const response = await api.post((API_ENDPOINTS.TESTS.LIST), newData)
  return response.data
}
export async function deleteTest(id) {
  const response = await api.delete((API_ENDPOINTS.TESTS.DETAIL(id)))
  response.data
}
