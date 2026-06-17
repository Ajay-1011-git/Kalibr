import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  signInWithEmailAndPassword,
  signInWithPopup,
} from 'firebase/auth'
import { auth, googleProvider } from '../lib/firebase'
import api from '../lib/api'
import { useAuthStore } from '../store/auth'
import type { UserProfile, VerifyResponse } from '../types'

export default function Login() {
  const navigate = useNavigate()
  const { setUser, setApiUser, setToken } = useAuthStore()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // ── Shared post-auth handler ──────────────────────────────────────────────
  async function handleFirebaseUser(firebaseUser: import('firebase/auth').User) {
    const token = await firebaseUser.getIdToken()
    setUser(firebaseUser)
    setToken(token)

    const { data } = await api.post<VerifyResponse>('/auth/verify', {
      firebase_token: token,
    })

    if (data.is_new_user) {
      // Fetch the just-created profile so apiUser is populated
      const profile = await api.get<UserProfile>('/users/me')
      setApiUser(profile.data)
      navigate('/settings')
    } else {
      const profile = await api.get<UserProfile>('/users/me')
      setApiUser(profile.data)
      navigate('/dashboard')
    }
  }

  // ── Google OAuth ──────────────────────────────────────────────────────────
  async function handleGoogle() {
    setError(null)
    setLoading(true)
    try {
      const result = await signInWithPopup(auth, googleProvider)
      await handleFirebaseUser(result.user)
    } catch (err: unknown) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  // ── Email / password ──────────────────────────────────────────────────────
  async function handleEmailLogin(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const result = await signInWithEmailAndPassword(auth, email, password)
      await handleFirebaseUser(result.user)
    } catch (err: unknown) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      {/* Decorative blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-violet-600/15 rounded-full blur-3xl pointer-events-none" />

      <div className="relative w-full max-w-md mx-4">
        {/* Logo / brand */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold tracking-tight text-white">
            Kali<span className="text-indigo-400">br</span>
          </h1>
          <p className="mt-2 text-slate-400 text-sm">
            AI-powered resume tailoring & job tracking
          </p>
        </div>

        {/* Card */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
          {/* Google button */}
          <button
            id="btn-google-signin"
            onClick={handleGoogle}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 bg-white text-slate-800 font-semibold rounded-xl px-4 py-3 hover:bg-slate-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {/* Google logo SVG */}
            <svg width="20" height="20" viewBox="0 0 48 48">
              <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.5 29.3 35 24 35c-6.1 0-11-4.9-11-11s4.9-11 11-11c2.8 0 5.3 1 7.2 2.7l5.7-5.7C33.5 7.1 29 5 24 5 12.9 5 4 13.9 4 25s8.9 20 20 20 20-8.9 20-20c0-1.2-.1-2.4-.4-3.5z"/>
              <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.5 16.1 18.9 13 24 13c2.8 0 5.3 1 7.2 2.7l5.7-5.7C33.5 7.1 29 5 24 5 16.3 5 9.7 8.9 6.3 14.7z"/>
              <path fill="#4CAF50" d="M24 45c5 0 9.4-1.9 12.7-5l-5.9-5c-1.9 1.4-4.3 2.3-6.8 2.3-5.2 0-9.6-3.5-11.2-8.2l-6.5 5C9.5 41 16.2 45 24 45z"/>
              <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.1-4 5.5l5.9 5C40.3 36.5 44 31.2 44 25c0-1.5-.2-2.4-.4-4.5z"/>
            </svg>
            Continue with Google
          </button>

          {/* Divider */}
          <div className="flex items-center my-6">
            <div className="flex-1 h-px bg-white/10" />
            <span className="mx-4 text-slate-500 text-xs uppercase tracking-widest">or</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          {/* Email / password form */}
          <form onSubmit={handleEmailLogin} className="space-y-4">
            <div>
              <label htmlFor="login-email" className="block text-sm text-slate-400 mb-1.5">
                Email
              </label>
              <input
                id="login-email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              />
            </div>

            <div>
              <label htmlFor="login-password" className="block text-sm text-slate-400 mb-1.5">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              />
            </div>

            {error && (
              <div
                role="alert"
                className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-xl px-4 py-3"
              >
                {error}
              </div>
            )}

            <button
              id="btn-email-signin"
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl px-4 py-3 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
        </div>

        <p className="text-center text-slate-600 text-xs mt-6">
          By signing in you agree to our Terms of Service.
        </p>
      </div>
    </div>
  )
}

// ── Utility ───────────────────────────────────────────────────────────────────
function getErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'code' in err) {
    const code = (err as { code: string }).code
    if (code === 'auth/invalid-credential' || code === 'auth/wrong-password') {
      return 'Incorrect email or password.'
    }
    if (code === 'auth/user-not-found') {
      return 'No account found with that email.'
    }
    if (code === 'auth/too-many-requests') {
      return 'Too many attempts. Please try again later.'
    }
    if (code === 'auth/popup-closed-by-user') {
      return 'Sign-in popup was closed. Please try again.'
    }
  }
  if (err instanceof Error) return err.message
  return 'An unexpected error occurred.'
}
