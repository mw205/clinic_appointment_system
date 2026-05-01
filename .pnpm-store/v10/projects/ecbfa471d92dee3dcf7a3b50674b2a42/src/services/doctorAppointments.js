import {api} from '@/lib/api.js'

export async function getAppointments(params = {})
{
  const res = await api.get('/appointments/doctor/appointments/', { params })
  return res.data
}

export async function getDailyQueue(params = {})
{
  const res = await api.get('/appointments/doctor/queue/', { params })
  return res.data.data
}

export async function checkInAppointment(appointment_id)
{
  return await api.post(`/appointments/${appointment_id}/check_in/`)
}

export async function hideAppointment(appointment_id)
{
  return await api.post(`/appointments/${appointment_id}/hide/`)
}
