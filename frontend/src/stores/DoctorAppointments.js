import {defineStore} from 'pinia'
import * as doctorAppointmentsService from '@/services/doctorAppointments'
import {ref} from "vue";


export const useDoctorAppointmentsStore = defineStore('doctorAppointments', () => {
  const dailyQueue = ref([]);
  const pendingRequests = ref([]);
  const loading = ref(false);

  async function loadDailyQueue() {
    loading.value = true

    try {
      dailyQueue.value = await doctorAppointmentsService.getAppointments({
        status: 'confirmed',
        // date: new Date().toISOString().slice(0,10)
      });
    }finally {
      loading.value = false;
    }
  }

  return { dailyQueue, pendingRequests, loading, loadDailyQueue };
})
