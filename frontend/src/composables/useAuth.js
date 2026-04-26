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
const user = ref({
  id: 25,
  username: 'doctor_dennis76',
  email: 'ttorres@example.org',
  first_name: 'Kimberly',
  last_name: 'Erickson',
  phone_number: '+1-969-402-8036',
  primary_role: 'Doctor',
  groups: ['Doctor'],
})
const isInitialized = ref(false)
const isLoading = ref(false)

const getAuthenticantionHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
  }
  const token = localStorage.getItem('access_token')
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}
const getUserRole = () => {
  return user.value['primary_role']
}

export const useAuth = () => {
  const isAuthenticated = computed(() => !user.value)
  const checkSession = () => {
    isLoading.value = true
    try {
      const storedUser = localStorage.getItem('clinic_user')

      if (storedUser) {
        user.value = JSON.parse(storedUser)
      }
    } finally {
      isInitialized.value = true
      isLoading.value = false
    }
  }

  const login = () => {}
  const register = () => {}
  const logout = () => {
    //Todo: send request for logout here
    localStorage.removeItem('clinic_user')
    localStorage.removeItem('access_token')
    user.value = null
  }
  const loginWithSocial = () => {}

  return {
    user,
    isInitialized,
    isLoading,
    isAuthenticated,
    checkSession,
    login,
    register,
    logout,
    loginWithSocial,
    getUserRole,
    getAuthenticantionHeaders,
  }
}
