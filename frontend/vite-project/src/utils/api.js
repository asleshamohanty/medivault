// API base URL from environment variable
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

// Helper function to handle API responses
const handleResponse = async (response) => {
  const data = await response.json()
  if (!response.ok) {
    console.error('API Error:', {
      status: response.status,
      statusText: response.statusText,
      data
    })
    throw new Error(data.error || 'API request failed')
  }
  return data
}

// Login function
export const login = async (credentials) => {
  console.log('Attempting login for:', credentials.email)
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(credentials),
    credentials: 'include'  // Important for session cookies
  })
  const data = await handleResponse(response)
  console.log('Login successful')
  return data
}

// Register function
export const register = async (userData) => {
  console.log('Attempting registration for:', userData.email)
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData),
    credentials: 'include'  // Important for session cookies
  })
  const data = await handleResponse(response)
  console.log('Registration successful')
  return data
}

// Logout function
export const logout = async () => {
  const response = await fetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
    credentials: 'include'  // Important for session cookies
  })
  const data = await handleResponse(response)
  console.log('Logout successful')
  return data
}

// Authenticated fetch function
export const fetchWithAuth = async (endpoint, options = {}) => {
  console.log('Making authenticated request to:', endpoint)
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include',  // Important for session cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })
  
  const data = await handleResponse(response)
  console.log('Request successful, response status:', response.status)
  return data
}

// Export the API base URL for use in components
export { API_BASE_URL } 