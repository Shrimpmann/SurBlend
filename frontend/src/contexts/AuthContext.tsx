import React, { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '@/services/api'
import { toast } from '@/components/ui/use-toast'

interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: 'admin' | 'sales_rep' | 'viewer'
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
  isAuthenticated: boolean
  hasRole: (role: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const userData = await authApi.getCurrentUser()
          setUser(userData)
        } catch (error) {
          // Token is invalid
          localStorage.removeItem('access_token')
        }
      }
      setIsLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.login(username, password)
      localStorage.setItem('access_token', response.access_token)
      
      // Get user data
      const userData = await authApi.getCurrentUser()
      setUser(userData)
      
      toast({
        title: 'Welcome back!',
        description: `Logged in as ${userData.full_name || userData.username}`,
      })
      
      navigate('/dashboard')
    } catch (error: any) {
      toast({
        title: 'Login failed',
        description: error.response?.data?.detail || 'Invalid credentials',
        variant: 'destructive',
      })
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    navigate('/login')
    toast({
      title: 'Logged out',
      description: 'You have been successfully logged out',
    })
  }

  const hasRole = (role: string) => {
    if (!user) return false
    if (user.role === 'admin') return true // Admin has all permissions
    return user.role === role
  }

  const value = {
    user,
    login,
    logout,
    isLoading,
    isAuthenticated: !!user,
    hasRole,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}