import { ref } from 'vue';
import { defineStore } from "pinia";
import { fetchConsultation, createConsultation, updateConsultation, fetchConsultationSummary } from '@/services/consultationService'

export const useConsultationStore = defineStore('consultation', () => {

    const consultation = ref(null);
    const loading = ref(false);
    const error = ref(null);

    async function loadAppointment(id) {
        loading.value = true;
        error.value = null;
        try {
            consultation.value = await fetchConsultation(id);
        } catch (e) {
            error.value = 'Error at fetching the consultaion data';
            throw e;
        }
        finally {
            loading.value = false;
        }
    }

    async function save(data) {
        loading.value = true;
        error.value = null;
        try {
            if (consultation.value?.id)
                consultation.value = await updateConsultation(consultation.value.id, data);
            else
                consultation.value = await createConsultation(data);
        } catch (e) {
            error.value = 'error saving consultation';
            throw e;
        }
        finally {
            loading.value = false;
        }
    }
    async function loadSummary(id) {
        loading.value = true;
        error.value = null;
        try {
            consultation.value = await fetchConsultationSummary(id)
        } catch (e) {
            error.value = 'error at loading summary.';
            throw e;
        } finally {
            loading.value = false;
        }
    }
    return { consultation, loading, error, loadAppointment, save, loadSummary };
})