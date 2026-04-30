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

const resetRoleProfiles = () => {
  doctorProfile.value = null
  patientProfile.value = null
}

export const useAuth = () => {
  const isAuthenticated = computed(() => !!user.value)

  const getCurrentUserProfile = async () => {
    if (!user.value?.primary_role) {
      resetRoleProfiles()
      return null
    }

    resetRoleProfiles()

    if (user.value.primary_role === 'Doctor') {
      const response = await api.get(
        API_ENDPOINTS.ACCOUNTS.BASE +
          API_ENDPOINTS.ACCOUNTS.ME +
          API_ENDPOINTS.ACCOUNTS.DOCTOR_PROFILE,
      )
      doctorProfile.value = response.data
      return doctorProfile.value
    }

    if (user.value.primary_role === 'Patient') {
      const response = await api.get(
        API_ENDPOINTS.ACCOUNTS.BASE +
          API_ENDPOINTS.ACCOUNTS.ME +
          API_ENDPOINTS.ACCOUNTS.PATIENT_PROFILE,
      )
      patientProfile.value = response.data
      return patientProfile.value
    }

    return null
  }

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

      const userRes = await api.get(API_ENDPOINTS.ACCOUNTS.BASE + API_ENDPOINTS.ACCOUNTS.ME)
      user.value = userRes.data
      await getCurrentUserProfile()
    } catch {
      user.value = null
      resetRoleProfiles()
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

      const userRes = await api.get(API_ENDPOINTS.ACCOUNTS.BASE + API_ENDPOINTS.ACCOUNTS.ME)
      user.value = userRes.data
      await getCurrentUserProfile()
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
      resetRoleProfiles()
      clearAuthQueue()
      window.location.href = '/login'
    }
  }

  const loginWithSocial = () => {
    console.warn('Social login not implemented.')
  }

  const updateAccount = async (data) => {
    isLoading.value = true
    try {
      const response = await api.patch('/accounts/me/', data)
      user.value = response.data
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (current_password, new_password, new_password_confirm) => {
    isLoading.value = true
    try {
      const response = await api.post('/accounts/me/change-password/', {
        current_password,
        new_password,
        new_password_confirm
      })
      // Clear user session as they need to log in again
      setAccessToken(null)
      user.value = null
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const getPatientProfile = async () => {
    isLoading.value = true
    try {
      const response = await api.get('/accounts/me/patient-profile/')
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const updatePatientProfile = async (data) => {
    isLoading.value = true
    try {
      const response = await api.patch('/accounts/me/patient-profile/', data)
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const getDoctorProfile = async () => {
    isLoading.value = true
    try {
      const response = await api.get('/accounts/me/doctor-profile/')
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const updateDoctorProfile = async (data) => {
    isLoading.value = true
    try {
      const response = await api.patch('/accounts/me/doctor-profile/', data)
      return response.data
    } finally {
      isLoading.value = false
    }
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
    verifyEmail,
    resendVerificationEmail,
    forgotPassword,
    resetPassword,
    logout,
    loginWithSocial,
    updateAccount,
    changePassword,
    getPatientProfile,
    updatePatientProfile,
    getDoctorProfile,
    updateDoctorProfile,
    getUserRole,
    getCurrentUserProfile,
  }
}
