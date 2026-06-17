/**
 * Axios instance for Kalibr API requests.
 *
 * - baseURL defaults to VITE_API_URL (http://localhost:8000/v1)
 * - Request interceptor: attaches Authorization: Bearer {token}
 * - Response interceptor: on 401 → Firebase signOut + clear store + redirect to /
 */

import axios from 'axios'
import { signOut } from 'firebase/auth'
import { auth } from './firebase'
import { useAuthStore } from '../store/auth'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/v1',
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor — attach Bearer token ──────────────────────────────
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor — handle 401 ─────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // Clear local auth state and redirect to login
      await signOut(auth).catch(() => {})
      useAuthStore.getState().logout()
      window.location.href = '/'
    }
    return Promise.reject(error)
  },
)

export default api
