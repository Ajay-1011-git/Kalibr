/**
 * Zustand auth store.
 *
 * Holds Firebase user, Kalibr API user profile, the current ID token,
 * and a loading flag that is true until the first Firebase auth state
 * resolution.
 */

import type { User as FirebaseUser } from 'firebase/auth'
import { create } from 'zustand'
import type { UserProfile } from '../types'

interface AuthState {
  user: FirebaseUser | null
  apiUser: UserProfile | null
  token: string | null
  isLoading: boolean
}

interface AuthActions {
  setUser: (user: FirebaseUser | null) => void
  setApiUser: (apiUser: UserProfile | null) => void
  setToken: (token: string | null) => void
  setLoading: (loading: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  // ── Initial state ──────────────────────────────────────────────────────────
  user: null,
  apiUser: null,
  token: null,
  isLoading: true,

  // ── Actions ────────────────────────────────────────────────────────────────
  setUser:    (user)    => set({ user }),
  setApiUser: (apiUser) => set({ apiUser }),
  setToken:   (token)   => set({ token }),
  setLoading: (isLoading) => set({ isLoading }),

  logout: () =>
    set({ user: null, apiUser: null, token: null, isLoading: false }),
}))
