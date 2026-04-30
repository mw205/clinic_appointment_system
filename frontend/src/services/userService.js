import { api } from '@/lib/api'

export const userService = {
  async getUsers(params) {
    const response = await api.get('/accounts/users/', { params })
    return response.data
  },

  async getUser(id) {
    const response = await api.get(`/accounts/users/${id}/`)
    return response.data
  },

  async updateUser(id, data) {
    const response = await api.patch(`/accounts/users/${id}/`, data)
    return response.data
  }
}
