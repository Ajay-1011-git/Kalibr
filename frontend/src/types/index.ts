/**
 * Shared TypeScript types for the Kalibr frontend.
 */

/** Shape returned by GET /v1/users/me */
export interface UserProfile {
  id: string
  firebase_uid: string
  email: string
  full_name: string | null
  phone: string | null
  address_line: string | null
  city: string | null
  country: string | null
  nationality: string | null
  work_auth: string | null
  notice_period: number | null
  salary_min: number | null
  salary_max: number | null
  salary_currency: string
  remote_pref: string | null
  linkedin_url: string | null
  github_url: string | null
  portfolio_url: string | null
  created_at: string
  updated_at: string
}

/** Shape returned by GET /v1/users/me/credentials */
export interface BoardCredential {
  id: string
  board: string
  created_at: string
  updated_at: string
}

/** Shape returned by POST /v1/auth/verify */
export interface VerifyResponse {
  user_id: string
  is_new_user: boolean
}

export type BoardName =
  | 'linkedin'
  | 'indeed'
  | 'glassdoor'
  | 'monster'
  | 'wellfound'
  | 'ziprecruiter'
  | 'upwork'

export const BOARD_OPTIONS: BoardName[] = [
  'linkedin',
  'indeed',
  'glassdoor',
  'monster',
  'wellfound',
  'ziprecruiter',
  'upwork',
]
