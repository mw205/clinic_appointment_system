import { api } from '@/lib/api'

export async function fetchConsultation(appointmentId) {
  const { data } = await api.get('/consultations/consultations/', {
    params: { appointment: appointmentId },
  })
  return data
}

export async function createConsultation(payload) {
  const { data } = await api.post('/consultations/consultations/', payload)
  return data
}

export async function updateConsultation(id, payload) {
  const { data } = await api.patch(`/consultations/consultations/${id}/`, payload)
  return data
}

export async function completeConsultation(id) {
  const { data } = await api.post(`/consultations/consultations/${id}/complete/`)
  return data
}

export async function fetchConsultationSummary(id) {
  const { data } = await api.get(`/consultations/consultations/${id}/summary/`)
  return data
}

export async function createPrescription(payload) {
  const { data } = await api.post('/consultations/prescriptions/', payload)
  return data
}

export async function deletePrescription(id) {
  await api.delete(`/consultations/prescriptions/${id}/`)
}

export async function createTest(payload) {
  const { data } = await api.post('/consultations/tests/', payload)
  return data
}

export async function deleteTest(id) {
  await api.delete(`/consultations/tests/${id}/`)
}
