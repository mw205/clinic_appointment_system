import {defineStore} from 'pinia'
import * as doctorAppointmentsService from '@/services/doctorAppointments'
import {ref} from "vue";


export const useDoctorAppointmentsStore = defineStore('doctorAppointments', () => {
  const dailyQueue = ref([]);
  const pendingRequests = ref([]);
  const loading = ref(false);
  const actionStatus = ref(null)
  const actionMessage = ref('')

  async function loadDailyQueue() {
    loading.value = true

    try {
      dailyQueue.value = await doctorAppointmentsService.getDailyQueue({
        // status: 'confirmed',
        // date: new Date().toISOString().slice(0,10)
      });
    }finally {
      loading.value = false;
    }
  }

async function checkInAppointment(appointment_id) {
  loading.value = true
  try {
    const response = await doctorAppointmentsService.checkInAppointment(appointment_id)
    await loadDailyQueue()
    return response.data
  } finally {
    loading.value = false
  }
}

async function hideAppointment(appointment_id)
{
  loading.value = true
  try {
    const response = await doctorAppointmentsService.hideAppointment(appointment_id)
    await loadDailyQueue()
    return response.data
  }finally {
    loading.value = false
  }

}

  return { dailyQueue, pendingRequests, loading, loadDailyQueue, checkInAppointment, actionStatus, actionMessage , hideAppointment};
})
