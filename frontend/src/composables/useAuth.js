import { computed, ref } from 'vue'
import { api, setAccessToken, clearAuthQueue } from '@/lib/api'

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
    } catch (error) {
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
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const verifyEmail = async (uid, token) => {
    isLoading.value = true
    try {
      const response = await api.post('/accounts/verify-email/', { uid, token })
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const resendVerificationEmail = async (email) => {
    isLoading.value = true
    try {
      const response = await api.post('/accounts/resend-verification-email/', { email })
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const forgotPassword = async (email) => {
    isLoading.value = true
    try {
      const response = await api.post('/accounts/forgot-password/', { email })
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const resetPassword = async (uid, token, new_password, new_password_confirm) => {
    isLoading.value = true
    try {
      const response = await api.post('/accounts/reset-password/', {
        uid,
        token,
        new_password,
        new_password_confirm
      })
      return response.data
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
      clearAuthQueue()
      window.location.href = '/login'
    }
  }

  const loginWithSocial = () => {
    console.warn("Social login not implemented.")
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
  }
}
