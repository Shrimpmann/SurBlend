import axios, { AxiosInstance, AxiosError } from 'axios'
import { toast } from '@/components/ui/use-toast'

// Types
export interface ApiError {
  detail: string
  status?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      toast({
        title: 'Access Denied',
        description: 'You do not have permission to perform this action.',
        variant: 'destructive',
      })
    } else if (error.response?.status === 404) {
      toast({
        title: 'Not Found',
        description: error.response.data?.detail || 'The requested resource was not found.',
        variant: 'destructive',
      })
    } else if (error.response?.status === 500) {
      toast({
        title: 'Server Error',
        description: 'An unexpected error occurred. Please try again later.',
        variant: 'destructive',
      })
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await axios.post('/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    
    return response.data
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/users/me')
    return response.data
  },
  
  changePassword: async (currentPassword: string, newPassword: string) => {
    const response = await api.post('/users/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  },
}

// Ingredients API
export const ingredientsApi = {
  getAll: async (page = 1, size = 20, search?: string) => {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    if (search) params.append('search', search)
    
    const response = await api.get<PaginatedResponse<any>>(`/ingredients?${params}`)
    return response.data
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/ingredients/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/ingredients', data)
    return response.data
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/ingredients/${id}`, data)
    return response.data
  },
  
  delete: async (id: number) => {
    await api.delete(`/ingredients/${id}`)
  },
  
  importCSV: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/ingredients/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  
  exportCSV: async () => {
    const response = await api.get('/ingredients/export', {
      responseType: 'blob',
    })
    return response.data
  },
}

// Blends API
export const blendsApi = {
  getAll: async (page = 1, size = 20, isTemplate?: boolean) => {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    if (isTemplate !== undefined) params.append('is_template', isTemplate.toString())
    
    const response = await api.get<PaginatedResponse<any>>(`/blends?${params}`)
    return response.data
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/blends/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/blends', data)
    return response.data
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/blends/${id}`, data)
    return response.data
  },
  
  delete: async (id: number) => {
    await api.delete(`/blends/${id}`)
  },
  
  optimize: async (data: {
    target_n?: number
    target_p?: number
    target_k?: number
    max_cost?: number
    available_ingredients?: number[]
  }) => {
    const response = await api.post('/blends/optimize', data)
    return response.data
  },
  
  calculateAnalysis: async (ingredients: any[]) => {
    const response = await api.post('/blends/calculate-analysis', { ingredients })
    return response.data
  },
}

// Customers API
export const customersApi = {
  getAll: async (page = 1, size = 20, search?: string) => {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    if (search) params.append('search', search)
    
    const response = await api.get<PaginatedResponse<any>>(`/customers?${params}`)
    return response.data
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/customers/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/customers', data)
    return response.data
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/customers/${id}`, data)
    return response.data
  },
  
  delete: async (id: number) => {
    await api.delete(`/customers/${id}`)
  },
  
  getFarms: async (customerId: number) => {
    const response = await api.get(`/customers/${customerId}/farms`)
    return response.data
  },
  
  createFarm: async (customerId: number, data: any) => {
    const response = await api.post(`/customers/${customerId}/farms`, data)
    return response.data
  },
}

// Quotes API
export const quotesApi = {
  getAll: async (page = 1, size = 20, status?: string) => {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    })
    if (status) params.append('status', status)
    
    const response = await api.get<PaginatedResponse<any>>(`/quotes?${params}`)
    return response.data
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/quotes/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/quotes', data)
    return response.data
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/quotes/${id}`, data)
    return response.data
  },
  
  delete: async (id: number) => {
    await api.delete(`/quotes/${id}`)
  },
  
  send: async (id: number, email: string) => {
    const response = await api.post(`/quotes/${id}/send`, { email })
    return response.data
  },
  
  generatePDF: async (id: number) => {
    const response = await api.get(`/quotes/${id}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },
  
  duplicate: async (id: number) => {
    const response = await api.post(`/quotes/${id}/duplicate`)
    return response.data
  },
}

// Analytics API
export const analyticsApi = {
  getDashboardStats: async () => {
    const response = await api.get('/analytics/dashboard')
    return response.data
  },
  
  getSalesRepStats: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    
    const response = await api.get(`/analytics/sales-reps?${params}`)
    return response.data
  },
  
  getIngredientTrends: async (ingredientId: number, days = 30) => {
    const response = await api.get(`/analytics/ingredients/${ingredientId}/trends?days=${days}`)
    return response.data
  },
  
  getQuoteConversion: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    
    const response = await api.get(`/analytics/quote-conversion?${params}`)
    return response.data
  },
}

// Users API
export const usersApi = {
  getAll: async (page = 1, size = 20) => {
    const response = await api.get<PaginatedResponse<any>>(`/users?page=${page}&size=${size}`)
    return response.data
  },
  
  getById: async (id: number) => {
    const response = await api.get(`/users/${id}`)
    return response.data
  },
  
  create: async (data: any) => {
    const response = await api.post('/users', data)
    return response.data
  },
  
  update: async (id: number, data: any) => {
    const response = await api.put(`/users/${id}`, data)
    return response.data
  },
  
  delete: async (id: number) => {
    await api.delete(`/users/${id}`)
  },
  
  resetPassword: async (id: number) => {
    const response = await api.post(`/users/${id}/reset-password`)
    return response.data
  },
}

// System API
export const systemApi = {
  getSettings: async () => {
    const response = await api.get('/system/settings')
    return response.data
  },
  
  updateSetting: async (key: string, value: any) => {
    const response = await api.put(`/system/settings/${key}`, { value })
    return response.data
  },
  
  getHealth: async () => {
    const response = await api.get('/health')
    return response.data
  },
  
  getActivityLogs: async (page = 1, size = 50) => {
    const response = await api.get<PaginatedResponse<any>>(`/system/activity-logs?page=${page}&size=${size}`)
    return response.data
  },
  
  exportData: async () => {
    const response = await api.get('/system/export', {
      responseType: 'blob',
    })
    return response.data
  },
}

export default api