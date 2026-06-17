import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { useAuthStore } from '../store/auth'
import type { BoardCredential, BoardName, UserProfile } from '../types'
import { BOARD_OPTIONS } from '../types'

// ── Types ─────────────────────────────────────────────────────────────────────

interface ProfileFormState {
  full_name: string
  phone: string
  city: string
  country: string
  work_auth: string
  notice_period: string
  salary_min: string
  salary_max: string
  salary_currency: string
  remote_pref: string
  linkedin_url: string
  github_url: string
}

const EMPTY_PROFILE: ProfileFormState = {
  full_name: '', phone: '', city: '', country: '',
  work_auth: '', notice_period: '', salary_min: '', salary_max: '',
  salary_currency: 'USD', remote_pref: '', linkedin_url: '', github_url: '',
}

// ── Settings page ─────────────────────────────────────────────────────────────

export default function Settings() {
  const navigate = useNavigate()
  const { setApiUser } = useAuthStore()

  const [form, setForm] = useState<ProfileFormState>(EMPTY_PROFILE)
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileSaved, setProfileSaved] = useState(false)
  const [profileError, setProfileError] = useState<string | null>(null)

  const [credentials, setCredentials] = useState<BoardCredential[]>([])
  const [credBoard, setCredBoard] = useState<BoardName>('linkedin')
  const [credUsername, setCredUsername] = useState('')
  const [credPassword, setCredPassword] = useState('')
  const [credSaving, setCredSaving] = useState(false)
  const [credError, setCredError] = useState<string | null>(null)
  const [credSuccess, setCredSuccess] = useState<string | null>(null)

  // ── Load existing profile & credentials ────────────────────────────────────
  const loadData = useCallback(async () => {
    try {
      const [profileRes, credsRes] = await Promise.all([
        api.get<UserProfile>('/users/me'),
        api.get<BoardCredential[]>('/users/me/credentials'),
      ])
      const p = profileRes.data
      setForm({
        full_name:       p.full_name       ?? '',
        phone:           p.phone           ?? '',
        city:            p.city            ?? '',
        country:         p.country         ?? '',
        work_auth:       p.work_auth       ?? '',
        notice_period:   p.notice_period != null ? String(p.notice_period) : '',
        salary_min:      p.salary_min     != null ? String(p.salary_min)   : '',
        salary_max:      p.salary_max     != null ? String(p.salary_max)   : '',
        salary_currency: p.salary_currency ?? 'USD',
        remote_pref:     p.remote_pref     ?? '',
        linkedin_url:    p.linkedin_url    ?? '',
        github_url:      p.github_url      ?? '',
      })
      setCredentials(credsRes.data)
    } catch {
      // If profile fetch fails the ProtectedRoute will redirect
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  // ── Profile submit ─────────────────────────────────────────────────────────
  async function handleProfileSave(e: React.FormEvent) {
    e.preventDefault()
    setProfileSaving(true)
    setProfileError(null)
    setProfileSaved(false)
    try {
      const body: Record<string, string | number | null> = {
        full_name:       form.full_name       || null,
        phone:           form.phone           || null,
        city:            form.city            || null,
        country:         form.country         || null,
        work_auth:       form.work_auth       || null,
        notice_period:   form.notice_period   ? parseInt(form.notice_period, 10)   : null,
        salary_min:      form.salary_min      ? parseInt(form.salary_min, 10)      : null,
        salary_max:      form.salary_max      ? parseInt(form.salary_max, 10)      : null,
        salary_currency: form.salary_currency || 'USD',
        remote_pref:     form.remote_pref     || null,
        linkedin_url:    form.linkedin_url    || null,
        github_url:      form.github_url      || null,
      }
      const { data } = await api.patch<UserProfile>('/users/me', body)
      setApiUser(data)
      setProfileSaved(true)
      setTimeout(() => setProfileSaved(false), 3000)
    } catch {
      setProfileError('Failed to save profile. Please try again.')
    } finally {
      setProfileSaving(false)
    }
  }

  // ── Add credentials ────────────────────────────────────────────────────────
  async function handleAddCredential(e: React.FormEvent) {
    e.preventDefault()
    setCredSaving(true)
    setCredError(null)
    setCredSuccess(null)
    try {
      await api.post('/users/me/credentials', {
        board: credBoard,
        username: credUsername,
        password: credPassword,
      })
      setCredUsername('')
      setCredPassword('')
      setCredSuccess(`${credBoard} credentials saved.`)
      setTimeout(() => setCredSuccess(null), 4000)
      await loadData()
    } catch {
      setCredError('Failed to save credentials.')
    } finally {
      setCredSaving(false)
    }
  }

  // ── Delete credentials ─────────────────────────────────────────────────────
  async function handleDeleteCredential(board: string) {
    try {
      await api.delete(`/users/me/credentials/${board}`)
      setCredentials((prev) => prev.filter((c) => c.board !== board))
    } catch {
      setCredError(`Failed to remove ${board}.`)
    }
  }

  const field = (key: keyof ProfileFormState) => ({
    value: form[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value })),
  })

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-3xl mx-auto px-4 py-12 space-y-10">
        {/* Header */}
        <div>
          <button
            id="btn-settings-back"
            onClick={() => navigate('/dashboard')}
            className="text-sm text-slate-400 hover:text-white transition-colors mb-4 flex items-center gap-1"
          >
            ← Dashboard
          </button>
          <h1 className="text-2xl font-bold">Profile Settings</h1>
          <p className="text-slate-400 text-sm mt-1">
            Keep your details up to date so Kalibr can tailor your applications.
          </p>
        </div>

        {/* ── Profile form ─────────────────────────────────────────────────── */}
        <section className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-6">
          <h2 className="text-lg font-semibold">Personal Information</h2>
          <form onSubmit={handleProfileSave} className="space-y-5">
            {/* Row 1 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field id="field-full-name" label="Full name">
                <input id="field-full-name" type="text" {...field('full_name')} placeholder="Jane Smith" className={inputCls} />
              </Field>
              <Field id="field-phone" label="Phone">
                <input id="field-phone" type="tel" {...field('phone')} placeholder="+1 555 000 0000" className={inputCls} />
              </Field>
            </div>

            {/* Row 2 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field id="field-city" label="City">
                <input id="field-city" type="text" {...field('city')} placeholder="San Francisco" className={inputCls} />
              </Field>
              <Field id="field-country" label="Country">
                <input id="field-country" type="text" {...field('country')} placeholder="United States" className={inputCls} />
              </Field>
            </div>

            {/* Row 3 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field id="field-work-auth" label="Work authorisation">
                <select id="field-work-auth" {...field('work_auth')} className={inputCls}>
                  <option value="">Select…</option>
                  <option value="citizen">Citizen</option>
                  <option value="permanent_resident">Permanent Resident</option>
                  <option value="visa">Work Visa</option>
                  <option value="open">Open to Sponsorship</option>
                </select>
              </Field>
              <Field id="field-notice-period" label="Notice period (days)">
                <input id="field-notice-period" type="number" min={0} {...field('notice_period')} placeholder="30" className={inputCls} />
              </Field>
            </div>

            {/* Row 4 — Salary */}
            <div className="grid grid-cols-3 gap-4">
              <Field id="field-salary-min" label="Salary min">
                <input id="field-salary-min" type="number" min={0} {...field('salary_min')} placeholder="80000" className={inputCls} />
              </Field>
              <Field id="field-salary-max" label="Salary max">
                <input id="field-salary-max" type="number" min={0} {...field('salary_max')} placeholder="120000" className={inputCls} />
              </Field>
              <Field id="field-salary-currency" label="Currency">
                <select id="field-salary-currency" {...field('salary_currency')} className={inputCls}>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="INR">INR</option>
                  <option value="CAD">CAD</option>
                  <option value="AUD">AUD</option>
                </select>
              </Field>
            </div>

            {/* Row 5 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field id="field-remote-pref" label="Remote preference">
                <select id="field-remote-pref" {...field('remote_pref')} className={inputCls}>
                  <option value="">No preference</option>
                  <option value="remote">Remote only</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="onsite">On-site</option>
                </select>
              </Field>
            </div>

            {/* Row 6 — Social */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Field id="field-linkedin" label="LinkedIn URL">
                <input id="field-linkedin" type="url" {...field('linkedin_url')} placeholder="https://linkedin.com/in/…" className={inputCls} />
              </Field>
              <Field id="field-github" label="GitHub URL">
                <input id="field-github" type="url" {...field('github_url')} placeholder="https://github.com/…" className={inputCls} />
              </Field>
            </div>

            {profileError && (
              <div role="alert" className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-xl px-4 py-3">
                {profileError}
              </div>
            )}
            {profileSaved && (
              <div className="bg-green-500/10 border border-green-500/30 text-green-400 text-sm rounded-xl px-4 py-3">
                Profile saved successfully.
              </div>
            )}

            <button
              id="btn-save-profile"
              type="submit"
              disabled={profileSaving}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl px-6 py-2.5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {profileSaving ? 'Saving…' : 'Save profile'}
            </button>
          </form>
        </section>

        {/* ── Board credentials ─────────────────────────────────────────────── */}
        <section className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-5">
          <div>
            <h2 className="text-lg font-semibold">Job Board Credentials</h2>
            <p className="text-slate-400 text-sm mt-1">
              Used by Kalibr's auto-apply feature to submit applications on your behalf.
            </p>
          </div>

          {/* Warning banner */}
          <div className="flex gap-2 bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-3 text-amber-300 text-sm">
            <span>⚠</span>
            <span>
              Your credentials are stored encrypted on the server. They are never displayed in plain text.
            </span>
          </div>

          {/* Saved boards list */}
          {credentials.length > 0 && (
            <ul className="space-y-2">
              {credentials.map((cred) => (
                <li
                  key={cred.id}
                  className="flex items-center justify-between bg-white/5 border border-white/10 rounded-xl px-4 py-3"
                >
                  <span className="font-medium capitalize">{cred.board}</span>
                  <button
                    id={`btn-delete-cred-${cred.board}`}
                    onClick={() => handleDeleteCredential(cred.board)}
                    className="text-red-400 hover:text-red-300 text-sm transition-colors"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}

          {/* Add credentials form */}
          <form onSubmit={handleAddCredential} className="space-y-4 pt-2 border-t border-white/10">
            <h3 className="text-sm font-medium text-slate-300">Add credentials</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Field id="field-cred-board" label="Board">
                <select
                  id="field-cred-board"
                  value={credBoard}
                  onChange={(e) => setCredBoard(e.target.value as BoardName)}
                  className={inputCls}
                >
                  {BOARD_OPTIONS.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </Field>
              <Field id="field-cred-username" label="Username / Email">
                <input
                  id="field-cred-username"
                  type="text"
                  required
                  autoComplete="off"
                  value={credUsername}
                  onChange={(e) => setCredUsername(e.target.value)}
                  placeholder="your@email.com"
                  className={inputCls}
                />
              </Field>
              <Field id="field-cred-password" label="Password">
                <input
                  id="field-cred-password"
                  type="password"
                  required
                  autoComplete="new-password"
                  value={credPassword}
                  onChange={(e) => setCredPassword(e.target.value)}
                  placeholder="••••••••"
                  className={inputCls}
                />
              </Field>
            </div>

            {credError && (
              <div role="alert" className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm rounded-xl px-4 py-3">
                {credError}
              </div>
            )}
            {credSuccess && (
              <div className="bg-green-500/10 border border-green-500/30 text-green-400 text-sm rounded-xl px-4 py-3">
                {credSuccess}
              </div>
            )}

            <button
              id="btn-save-credentials"
              type="submit"
              disabled={credSaving}
              className="bg-white/10 hover:bg-white/20 text-white font-medium rounded-xl px-5 py-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {credSaving ? 'Saving…' : 'Save credentials'}
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}

// ── Shared sub-components ─────────────────────────────────────────────────────

const inputCls =
  'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition text-sm'

function Field({
  id, label, children,
}: {
  id: string
  label: string
  children: React.ReactNode
}) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm text-slate-400 mb-1.5">
        {label}
      </label>
      {children}
    </div>
  )
}
