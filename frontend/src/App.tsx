import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from '@/components/ui/toaster'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'

// Layouts
import MainLayout from '@/layouts/MainLayout'
import AuthLayout from '@/layouts/AuthLayout'

// Pages
import Login from '@/pages/auth/Login'
import Dashboard from '@/pages/Dashboard'
import Ingredients from '@/pages/ingredients/Ingredients'
import IngredientForm from '@/pages/ingredients/IngredientForm'
import Blends from '@/pages/blends/Blends'
import BlendBuilder from '@/pages/blends/BlendBuilder'
import Customers from '@/pages/customers/Customers'
import CustomerForm from '@/pages/customers/CustomerForm'
import Quotes from '@/pages/quotes/Quotes'
import QuoteBuilder from '@/pages/quotes/QuoteBuilder'
import Users from '@/pages/users/Users'
import Settings from '@/pages/settings/Settings'
import Analytics from '@/pages/analytics/Analytics'

// Protected Route Component
import ProtectedRoute from '@/components/auth/ProtectedRoute'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <Routes>
              {/* Auth Routes */}
              <Route element={<AuthLayout />}>
                <Route path="/login" element={<Login />} />
              </Route>

              {/* Protected Routes */}
              <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                
                {/* Ingredients */}
                <Route path="/ingredients" element={<Ingredients />} />
                <Route path="/ingredients/new" element={<IngredientForm />} />
                <Route path="/ingredients/:id/edit" element={<IngredientForm />} />
                
                {/* Blends */}
                <Route path="/blends" element={<Blends />} />
                <Route path="/blends/new" element={<BlendBuilder />} />
                <Route path="/blends/:id/edit" element={<BlendBuilder />} />
                
                {/* Customers */}
                <Route path="/customers" element={<Customers />} />
                <Route path="/customers/new" element={<CustomerForm />} />
                <Route path="/customers/:id/edit" element={<CustomerForm />} />
                
                {/* Quotes */}
                <Route path="/quotes" element={<Quotes />} />
                <Route path="/quotes/new" element={<QuoteBuilder />} />
                <Route path="/quotes/:id/edit" element={<QuoteBuilder />} />
                
                {/* Analytics */}
                <Route path="/analytics" element={<Analytics />} />
                
                {/* Admin Routes */}
                <Route path="/users" element={<ProtectedRoute requiredRole="admin"><Users /></ProtectedRoute>} />
                <Route path="/settings" element={<ProtectedRoute requiredRole="admin"><Settings /></ProtectedRoute>} />
              </Route>
            </Routes>
          </Router>
          <Toaster />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App