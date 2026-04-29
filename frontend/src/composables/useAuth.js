import { API_ENDPOINTS } from '@/constants/endpoints'
import { api, clearAuthQueue, setAccessToken } from '@/lib/api'
import { computed, ref } from 'vue'

export const getDefaultRouteForRole = (role) => {
  switch (role) {
    case 'Patient':
      return '/patient/dashboard'
    case 'Doctor':
      return '/doctor/schedules'
    case 'Receptionist':
      return '/receptionist/queue'
    case 'Admin':
      return '/admin/dashboard'
    default:
      return '/login'
  }
}

const user = ref(null)
const doctorProfile = ref(null)
const patientProfile = ref(null)
const activeProfileId = computed(() => {
  if (user.value?.primary_role === 'Doctor') {
    return doctorProfile.value?.id
  }
  if (user.value?.primary_role === 'Patient') {
    return patientProfile.value?.id
  }
  return null
})
const isInitialized = ref(false)
const isLoading = ref(false)
const authReady = ref(false)

const getUserRole = () => {
  return user.value?.primary_role
}

export const useAuth = () => {
  const isAuthenticated = computed(() => !!user.value)

  const checkSession = async () => {
    isLoading.value = true

    // Clean up legacy localStorage items from old auth flow
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('clinic_user')

    try {
      const response = await api.post('/accounts/refresh/')
      const newAccessToken = response.data.access || response.data.access_token || response.data
      setAccessToken(newAccessToken)

      const userRes = await api.get('/accounts/me/')
      user.value = userRes.data
    } catch {
      user.value = null
      setAccessToken(null)
    } finally {
      isInitialized.value = true
      isLoading.value = false
      authReady.value = true
    }
  }

  const login = async (username, password) => {
    isLoading.value = true
    try {
      const response = await api.post('/accounts/login/', { username, password })
      const newAccessToken = response.data.access || response.data.access_token || response.data
      setAccessToken(newAccessToken)

      const userRes = await api.get('/accounts/me/')
      user.value = userRes.data
      return user.value
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      const response = await api.post('/accounts/register/', userData)
      const newAccessToken = response.data.access || response.data.access_token || response.data
      setAccessToken(newAccessToken)

      const userRes = await api.get('/accounts/me/')
      user.value = userRes.data
      return user.value
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await api.post('/accounts/logout/')
    } catch (error) {
      console.error('Logout API failed', error)
    } finally {
      setAccessToken(null)
      user.value = null
      patientProfile.value = null
      doctorProfile.value = null
      activeProfileId.value = null
      clearAuthQueue()
      window.location.href = '/login'
    }
  }

  const loginWithSocial = () => {
    console.warn('Social login not implemented.')
  }

  const getCurrentUserProfile = async () => {
    if (user.value.primary_role == 'Doctor') {
      const response = await api.get(
        API_ENDPOINTS.ACCOUNTS.BASE + API_ENDPOINTS.ACCOUNTS.DOCTOR_PROFILE,
      )
      doctorProfile.value = response.data
    } else if (user.value.primary_role == 'Patient') {
      const response = await api.get(
        API_ENDPOINTS.ACCOUNTS.BASE + API_ENDPOINTS.ACCOUNTS.PATIENT_PROFILE,
      )
      patientProfile.value = response.data
    }
    return null
  }

  return {
    user,
    isInitialized,
    isLoading,
    authReady,
    isAuthenticated,
    doctorProfile,
    patientProfile,
    activeProfileId,
    checkSession,
    login,
    register,
    logout,
    loginWithSocial,
    getUserRole,
    getCurrentUserProfile,
  }
}
