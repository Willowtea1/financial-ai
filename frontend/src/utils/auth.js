/**
 * Authentication Utility
 * Handles secure token storage and management
 */

import { supabase } from '../supabase'

/**
 * Store authentication tokens securely in localStorage
 * @param {string} accessToken - JWT access token
 * @param {string} refreshToken - Refresh token
 */
export function storeTokens(accessToken, refreshToken) {
  if (accessToken) {
    localStorage.setItem('supabase_token', accessToken)
  }
  if (refreshToken) {
    localStorage.setItem('supabase_refresh_token', refreshToken)
  }
}

/**
 * Get the current access token
 * @returns {string|null} Access token or null if not found
 */
export function getAccessToken() {
  return localStorage.getItem('supabase_token')
}

/**
 * Get the current refresh token
 * @returns {string|null} Refresh token or null if not found
 */
export function getRefreshToken() {
  return localStorage.getItem('supabase_refresh_token')
}

/**
 * Clear all authentication tokens
 */
export function clearTokens() {
  localStorage.removeItem('supabase_token')
  localStorage.removeItem('supabase_refresh_token')
  localStorage.removeItem('questionnaire_completed')
  localStorage.removeItem('questionnaire_data')
}

/**
 * Check if user is authenticated
 * @returns {Promise<boolean>} True if authenticated
 */
export async function isAuthenticated() {
  const { data: { session } } = await supabase.auth.getSession()
  return !!session
}

/**
 * Get current user session
 * @returns {Promise<Object|null>} Session object or null
 */
export async function getSession() {
  const { data: { session } } = await supabase.auth.getSession()
  return session
}

/**
 * Get current user
 * @returns {Promise<Object|null>} User object or null
 */
export async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

/**
 * Sign out user
 */
export async function signOut() {
  await supabase.auth.signOut()
  clearTokens()
}

/**
 * Handle OAuth callback from URL hash
 * Extracts tokens, stores them securely, and cleans the URL
 * @returns {Promise<boolean>} True if tokens were found and stored
 */
export async function handleOAuthCallback() {
  // Check for tokens in URL hash
  const hashParams = new URLSearchParams(window.location.hash.substring(1))
  const accessToken = hashParams.get('access_token')
  const refreshToken = hashParams.get('refresh_token')
  
  if (!accessToken) {
    return false
  }
  
  console.log('OAuth callback detected, storing tokens securely...')
  
  try {
    // Set the session in Supabase client
    const { data, error } = await supabase.auth.setSession({
      access_token: accessToken,
      refresh_token: refreshToken
    })
    
    if (error) {
      console.error('Error setting session:', error)
      return false
    }
    
    // Store tokens
    storeTokens(accessToken, refreshToken)
    
    // Clean the URL by removing hash parameters
    const cleanUrl = window.location.pathname + window.location.search
    window.history.replaceState({}, document.title, cleanUrl)
    
    console.log('Tokens stored securely, URL cleaned')
    return true
  } catch (error) {
    console.error('Error handling OAuth callback:', error)
    return false
  }
}

/**
 * Refresh the access token if expired
 * @returns {Promise<string|null>} New access token or null if refresh failed
 */
export async function refreshAccessToken() {
  const { data, error } = await supabase.auth.refreshSession()
  
  if (error) {
    console.error('Error refreshing token:', error)
    return null
  }
  
  if (data.session) {
    storeTokens(data.session.access_token, data.session.refresh_token)
    return data.session.access_token
  }
  
  return null
}

/**
 * Make an authenticated API request
 * Automatically includes the access token in headers
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
export async function authenticatedFetch(url, options = {}) {
  const token = getAccessToken()
  
  if (!token) {
    throw new Error('No access token available')
  }
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers
    })
    
    // If unauthorized, try to refresh token
    if (response.status === 401) {
      const newToken = await refreshAccessToken()
      
      if (newToken) {
        // Retry with new token
        headers['Authorization'] = `Bearer ${newToken}`
        return fetch(url, {
          ...options,
          headers
        })
      }
    }
    
    return response
  } catch (error) {
    console.error('Authenticated fetch error:', error)
    throw error
  }
}

/**
 * Setup auth state listener
 * Automatically updates stored tokens when auth state changes
 */
export function setupAuthListener() {
  supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event)
    
    switch (event) {
      case 'SIGNED_IN':
      case 'TOKEN_REFRESHED':
        if (session) {
          storeTokens(session.access_token, session.refresh_token)
        }
        break
      
      case 'SIGNED_OUT':
        clearTokens()
        break
      
      case 'USER_UPDATED':
        if (session) {
          storeTokens(session.access_token, session.refresh_token)
        }
        break
    }
  })
}
