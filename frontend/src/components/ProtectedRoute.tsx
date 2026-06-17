import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

/**
 * ProtectedRoute — wraps authenticated sections of the app.
 *
 * - While Firebase is resolving the initial auth state (isLoading = true),
 *   render nothing to avoid a flash of the login page.
 * - Once resolved, redirect unauthenticated users to / (Login).
 * - Authenticated users see the nested route via <Outlet />.
 */
export default function ProtectedRoute() {
  const user = useAuthStore((s) => s.user)
  const isLoading = useAuthStore((s) => s.isLoading)

  if (isLoading) {
    // Auth state not yet resolved — render blank to avoid flicker
    return null
  }

  if (!user) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
