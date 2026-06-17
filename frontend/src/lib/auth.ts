/**
 * Firebase auth state listener.
 *
 * Call `initAuthListener()` once at app startup (inside a useEffect in App).
 * It watches onAuthStateChanged, keeps the Zustand store in sync, and
 * refreshes the ID token on every state change.
 */

import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebase'
import { useAuthStore } from '../store/auth'

/**
 * Subscribe to Firebase auth state changes.
 * Returns an unsubscribe function — call it on component unmount.
 */
export function initAuthListener(): () => void {
  const { setUser, setToken, setLoading, logout } = useAuthStore.getState()

  const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
    if (firebaseUser) {
      try {
        const token = await firebaseUser.getIdToken()
        setUser(firebaseUser)
        setToken(token)
      } catch {
        logout()
      }
    } else {
      logout()
    }
    setLoading(false)
  })

  return unsubscribe
}
