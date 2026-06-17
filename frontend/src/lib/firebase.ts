/**
 * Firebase app initialisation.
 *
 * Reads configuration from VITE_FIREBASE_* environment variables.
 * Initialises Auth only — storage is handled by the backend via Supabase Storage.
 * Import `auth` and `googleProvider` wherever Firebase auth is needed.
 */

import { initializeApp } from 'firebase/app'
import { GoogleAuthProvider, getAuth } from 'firebase/auth'

const firebaseConfig = {
  apiKey:            import.meta.env.VITE_FIREBASE_API_KEY as string,
  authDomain:        import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string,
  projectId:         import.meta.env.VITE_FIREBASE_PROJECT_ID as string,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string | undefined,
  appId:             import.meta.env.VITE_FIREBASE_APP_ID as string | undefined,
}

const firebaseApp = initializeApp(firebaseConfig)

export const auth = getAuth(firebaseApp)
export const googleProvider = new GoogleAuthProvider()
