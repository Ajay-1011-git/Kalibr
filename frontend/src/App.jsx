import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Home from './pages/Home'
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
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/search" element={<Search />} />
        <Route path="/jobs/saved" element={<SavedJobs />} />
        <Route path="/resumes" element={<Resumes />} />
        <Route path="/resumes/upload" element={<ResumeUpload />} />
        <Route path="/resumes/:id" element={<ResumeDetail />} />
        <Route path="/rewrite/:task_id" element={<Rewrite />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/settings/auto-apply" element={<AutoApply />} />
        <Route path="/interview/:id" element={<InterviewPrep />} />
      </Routes>
    </BrowserRouter>
  )
}
