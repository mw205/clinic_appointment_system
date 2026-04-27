import {api} from '@/lib/api.js'

export async function getAppointments(params = {})
{
  const res = await api.get('/appointments/doctor/appointments/', { params })
  return res.data
}
