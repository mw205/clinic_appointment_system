import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 5000,
  headers: { Accept: 'application/json' },
})
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, config.data || '')
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`, response.data)
    return response
  },
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        console.warn('[API Error] Unautorhized! Redirecting to login ..')
        try {
          localStorage.removeItem('access_token')
        } catch (e) {
          console.error(e)
        }
        window.location.href = '/login'
      }
      console.error(
        `[API Error] ${error.response.status} ${error.response.config.url}`,
        error.response.data || '',
      )
    } else {
      console.error('[API Error] Network Error')
    }

    return Promise.reject(error)
  },
)
