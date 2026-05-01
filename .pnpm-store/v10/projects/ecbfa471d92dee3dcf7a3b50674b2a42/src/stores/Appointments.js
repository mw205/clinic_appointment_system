import {defineStore} from 'pinia'
import * as appointmentService from "@/services/appointmentService.js";
import {ref} from "vue";


export const useAppointmentsStore = defineStore('doctorAppointments', () => {
  const appointments = ref([]);
  const pagination = ref({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    totalPages: 1,
    pageSize: null,
  });
  const pendingRequests = ref([]);
  const loading = ref(false);
  const actionStatus = ref(null)
  const actionMessage = ref('')

  function getPageFromUrl(url) {
    if (!url) {
      return null
    }

    try {
      const parsedUrl = new URL(url)
      const page = Number(parsedUrl.searchParams.get('page'))
      return Number.isFinite(page) && page > 0 ? page : null
    } catch {
      return null
    }
  }

  function updatePagination(data, requestedPage = 1) {
    const results = Array.isArray(data?.results) ? data.results : []
    const count = Number(data?.count ?? results.length)
    const previousPage = getPageFromUrl(data?.previous)
    const nextPage = getPageFromUrl(data?.next)
    const currentPage = Number(requestedPage) > 0
      ? Number(requestedPage)
      : previousPage
        ? previousPage + 1
        : nextPage
          ? nextPage - 1
          : 1

    if ((data?.next || currentPage === 1) && results.length > 0) {
      pagination.value.pageSize = results.length
    }

    const pageSize = pagination.value.pageSize || results.length || 1
    const totalPages = Math.max(1, Math.ceil(count / pageSize))

    pagination.value = {
      count,
      next: data?.next ?? null,
      previous: data?.previous ?? null,
      currentPage,
      totalPages,
      pageSize: pagination.value.pageSize,
    }
  }

  function resetPagination(totalCount = 0) {
    pagination.value = {
      count: totalCount,
      next: null,
      previous: null,
      currentPage: 1,
      totalPages: 1,
      pageSize: null,
    }
  }

  // async function loadDailyQueue(params = {}) {
  //   loading.value = true
  //
  //   try {
  //     dailyQueue.value = await doctorAppointmentsService.getDailyQueue({
  //       ...params
  //       // date: new Date().toISOString().slice(0,10)
  //     });
  //   }finally {
  //     loading.value = false;
  //   }
  // }

async function loadAppointments(params = {})
{
  loading.value = true
  try {
    const data = await appointmentService.getAppointments(params)
    appointments.value = data.results
    updatePagination(data, params.page)
  }finally {
    loading.value = false
  }
}

async function loadDoctorDailyQueue(params = {})
{
  loading.value = true
  try {
    appointments.value = await appointmentService.getDoctorDailyQueue(params)
    resetPagination(appointments.value.length)
  }finally {
    loading.value = false
  }
}

async function confirmAppointment(appointment_id) {
  loading.value = true
  try {
    const response = await appointmentService.confirmAppointment(appointment_id)
    return response
  } finally {
    loading.value = false
  }
}


async function checkInAppointment(appointment_id) {
  loading.value = true
  try {
    const response = await appointmentService.checkInAppointment(appointment_id)
    // await loadDailyQueue()
    return response.data
  } finally {
    loading.value = false
  }
}

async function hideAppointment(appointment_id)
{
  loading.value = true
  try {
    const response = await appointmentService.hideAppointment(appointment_id)
    // await loadDailyQueue()
    return response.data
  }finally {
    loading.value = false
  }

}

  return {
    appointments,
    pagination,
    pendingRequests,
    loading,
    confirmAppointment,
    checkInAppointment,
    actionStatus,
    actionMessage,
    hideAppointment,
    loadAppointments,
    loadDoctorDailyQueue,
  };
})
