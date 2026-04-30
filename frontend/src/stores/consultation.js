import { ref } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchConsultation,
  createConsultation,
  updateConsultation,
  completeConsultation,
  fetchConsultationSummary,
} from '@/services/consultationService'

export const useConsultationStore = defineStore('consultation', () => {
  const consultation = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function loadForAppointment(appointmentId) {
    loading.value = true
    error.value = null
    try {
      const results = await fetchConsultation(appointmentId)
      consultation.value = results?.length ? results[0] : null
    } catch (e) {
      error.value = 'Could not load consultation.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function save(data) {
    loading.value = true
    error.value = null
    try {
      if (consultation.value?.id) {
        consultation.value = await updateConsultation(consultation.value.id, data)
      } else {
        consultation.value = await createConsultation(data)
      }
    } catch (e) {
      error.value = 'Could not save consultation.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function complete(id) {
    loading.value = true
    error.value = null
    try {
      consultation.value = await completeConsultation(id)
    } catch (e) {
      error.value = 'Could not complete consultation.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadSummary(id) {
    loading.value = true
    error.value = null
    try {
      consultation.value = await fetchConsultationSummary(id)
    } catch (e) {
      error.value = 'Could not load summary.'
      throw e
    } finally {
      loading.value = false
    }
  }

  return { consultation, loading, error, loadForAppointment, save, complete, loadSummary }
})
