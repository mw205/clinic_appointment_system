import * as scheduleService from '@/services/schedule_service'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useScheduleStore = defineStore('schedule', () => {
  const doctors = ref([])
  const selectedDoctorId = ref(null)
  const schedules = ref([])
  const exceptions = ref([])
  const availableSlots = ref([])
  const loadingDoctors = ref(false)
  const loadingSchedules = ref(false)
  const loadingExceptions = ref(false)
  const loadingAvailableSlots = ref(false)
  const submitting = ref(false)
  const error = ref(null)

  const loadDoctors = async (params = { role: 'Doctor' }) => {
    loadingDoctors.value = true
    error.value = null

    try {
      doctors.value = await scheduleService.getDoctors(params)
      return doctors.value
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loadingDoctors.value = false
    }
  }

  const loadSchedules = async (params = {}) => {
    loadingSchedules.value = true
    error.value = null

    try {
      schedules.value = await scheduleService.getSchedules(params)
      return schedules.value
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loadingSchedules.value = false
    }
  }

  const createSchedule = async (payload) => {
    submitting.value = true
    error.value = null

    try {
      const createdSchedule = await scheduleService.createSchedule(payload)
      await loadSchedules({ doctor: payload.doctor_id })
      return createdSchedule
    } catch (e) {
      error.value = e
      throw e
    } finally {
      submitting.value = false
    }
  }

  const editSchedule = async (id, payload) => {
    submitting.value = true
    error.value = null

    try {
      const updatedSchedule = await scheduleService.updateSchedule(id, payload)
      await loadSchedules({ doctor: payload.doctor_id })
      return updatedSchedule
    } catch (e) {
      error.value = e
      throw e
    } finally {
      submitting.value = false
    }
  }

  const removeSchedule = async (id, doctorId = selectedDoctorId.value) => {
    submitting.value = true
    error.value = null

    try {
      await scheduleService.deleteSchedule(id)
      if (doctorId) {
        await loadSchedules({ doctor: doctorId })
      } else {
        await loadSchedules()
      }
    } catch (e) {
      error.value = e
      throw e
    } finally {
      submitting.value = false
    }
  }

  const loadExceptions = async (params = {}) => {
    loadingExceptions.value = true
    error.value = null

    try {
      exceptions.value = await scheduleService.getExceptions(params)
      return exceptions.value
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loadingExceptions.value = false
    }
  }

  const createException = async (payload) => {
    submitting.value = true
    error.value = null

    try {
      const createdException = await scheduleService.createException(payload)
      await loadExceptions({ doctor_id: payload.doctor_id })
      return createdException
    } catch (e) {
      error.value = e
      throw e
    } finally {
      submitting.value = false
    }
  }

  const editException = async (id, payload) => {
    submitting.value = true
    error.value = null

    try {
      const updatedException = await scheduleService.updateException(id, payload)
      await loadExceptions({ doctor_id: payload.doctor_id })
      return updatedException
    } catch (e) {
      error.value = e
      throw e
    } finally {
      submitting.value = false
    }
  }

  const removeException = async (id, doctorId = selectedDoctorId.value) => {
    submitting.value = true
    error.value = null

    try {
      await scheduleService.deleteException(id)
      if (doctorId) {
        await loadExceptions({ doctor_id: doctorId })
      } else {
        await loadExceptions()
      }
    } catch (e) {
      error.value = e
      throw e
    } finally {
      submitting.value = false
    }
  }

  const loadAvailableSlots = async (doctorId, date) => {
    loadingAvailableSlots.value = true
    error.value = null

    try {
      availableSlots.value = await scheduleService.getAvailableSlots(doctorId, date)
      return availableSlots.value
    } catch (e) {
      error.value = e
      throw e
    } finally {
      loadingAvailableSlots.value = false
    }
  }

  return {
    doctors,
    selectedDoctorId,
    schedules,
    exceptions,
    availableSlots,
    loadingDoctors,
    loadingSchedules,
    loadingExceptions,
    loadingAvailableSlots,
    submitting,
    error,
    loadDoctors,
    loadSchedules,
    createSchedule,
    editSchedule,
    removeSchedule,
    loadExceptions,
    loadAvailableSlots,
    removeException,
    editException,
    createException,
  }
})
