import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 5000,
  headers: { Accept: 'application/json' },
  withCredentials: true,
})

let accessToken = null
let isRefreshing = false
let refreshQueue = []

export const setAccessToken = (token) => {
  accessToken = token
}

export const clearAuthQueue = () => {
  isRefreshing = false
  refreshQueue = []
}

api.interceptors.request.use(
  (config) => {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, config.data || '')
    return config
  },
  (error) => Promise.reject(error),
)

api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`, response.data)
    return response
  },
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401) {
      // Protect Refresh Endpoint
      if (originalRequest.url.includes('/refresh')) {
        return Promise.reject(error)
      }

      // Prevent Infinite Retry Loops
      if (originalRequest._retry) {
        return Promise.reject(error)
      }
      originalRequest._retry = true

      // Handle Concurrent 401 Requests
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          refreshQueue.push((token) => {
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(api(originalRequest))
            } else {
              reject(error)
            }
          })
        })
      }

      isRefreshing = true

      try {
        const response = await api.post('/accounts/refresh/')
        const newAccessToken = response.data.access || response.data.access_token || response.data

        setAccessToken(newAccessToken)

        // Replay queued requests
        refreshQueue.forEach((cb) => cb(newAccessToken))
        refreshQueue = []

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return api(originalRequest)
      } catch (refreshError) {
        refreshQueue.forEach((cb) => cb(null))
        refreshQueue = []
        setAccessToken(null)

        // Import useAuth lazily to avoid circular dependency
        const { useAuth } = await import('@/composables/useAuth')
        useAuth().logout()

        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    if (error.response) {
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
