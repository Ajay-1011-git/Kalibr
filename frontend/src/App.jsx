import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { initAuthListener } from './lib/auth'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Search from './pages/Search'
import SavedJobs from './pages/SavedJobs'
import Resumes from './pages/Resumes'
import ResumeUpload from './pages/ResumeUpload'
import ResumeDetail from './pages/ResumeDetail'
import Rewrite from './pages/Rewrite'
import Applications from './pages/Applications'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'
import AutoApply from './pages/AutoApply'
import InterviewPrep from './pages/InterviewPrep'

export default function App() {
  // Start listening to Firebase auth state once on mount
  useEffect(() => {
    const unsubscribe = initAuthListener()
    return unsubscribe
  }, [])

  return (
    <BrowserRouter>
      <Routes>
        {/* Public — Login is the root route */}
        <Route path="/" element={<Login />} />

        {/* Protected — all other routes require authentication */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard"          element={<Dashboard />} />
          <Route path="/search"             element={<Search />} />
          <Route path="/jobs/saved"         element={<SavedJobs />} />
          <Route path="/resumes"            element={<Resumes />} />
          <Route path="/resumes/upload"     element={<ResumeUpload />} />
          <Route path="/resumes/:id"        element={<ResumeDetail />} />
          <Route path="/rewrite/:task_id"   element={<Rewrite />} />
          <Route path="/applications"       element={<Applications />} />
          <Route path="/alerts"             element={<Alerts />} />
          <Route path="/settings"           element={<Settings />} />
          <Route path="/settings/auto-apply" element={<AutoApply />} />
          <Route path="/interview/:id"      element={<InterviewPrep />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
