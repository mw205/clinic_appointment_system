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
      clearAuthQueue()
      window.location.href = '/login'
    }
  }

  const loginWithSocial = () => {
    console.warn("Social login not implemented.")
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
    logout,
    loginWithSocial,
    getUserRole,
  }
}
