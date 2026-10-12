import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const client = axios.create({ baseURL: API_BASE })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return client.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  register: (payload) => client.post('/auth/register', payload),
  me: () => client.get('/auth/me'),
  updateProfile: (payload) => client.patch('/auth/me', payload),
}

export const lifeItemsApi = {
  list: (params) => client.get('/life-items', { params }),
  upcoming: () => client.get('/life-items/upcoming'),
  create: (payload) => client.post('/life-items', payload),
  update: (id, payload) => client.patch(`/life-items/${id}`, payload),
  delete: (id) => client.delete(`/life-items/${id}`),
}

export const notificationsApi = {
  list: () => client.get('/notifications'),
  markRead: (id) => client.patch(`/notifications/${id}/read`),
}

export const opportunitiesApi = {
  matches: (opportunity_type) => client.get('/opportunities/matches', { params: { opportunity_type } }),
  summary: () => client.get('/opportunities/summary'),
}

export const assistantApi = {
  chat: (message) => client.post('/assistant/chat', { message }),
  history: () => client.get('/assistant/chat/history'),
  dailySchedule: () => client.get('/assistant/daily-schedule'),
}

export const analyticsApi = {
  summary: () => client.get('/analytics/summary'),
}

export default client
