-- ============================================================
-- Migration: 001_initial_schema
-- Tables:    users, board_credentials
-- RLS:       enabled on both tables
-- ============================================================

-- ── Enable pgcrypto for gen_random_uuid() ─────────────────────────────────
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ── users ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid     TEXT NOT NULL UNIQUE,
    email            TEXT NOT NULL,

    -- Profile
    full_name        TEXT,
    phone            TEXT,
    address_line     TEXT,
    city             TEXT,
    country          TEXT,
    nationality      TEXT,
    work_auth        TEXT,                         -- e.g. 'citizen', 'visa', 'open'
    notice_period    INTEGER,                      -- days

    -- Salary preferences
    salary_min       INTEGER,
    salary_max       INTEGER,
    salary_currency  TEXT NOT NULL DEFAULT 'USD',

    -- Job preferences
    remote_pref      TEXT,                         -- 'remote' | 'hybrid' | 'onsite'

    -- Social links
    linkedin_url     TEXT,
    github_url       TEXT,
    portfolio_url    TEXT,

    -- Timestamps
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Row-Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: a user can only see and modify their own row.
-- The backend uses the service-role key (bypasses RLS).
-- These policies protect against direct PostgREST / anon-key access.
CREATE POLICY "users_select_own"
    ON users FOR SELECT
    USING (
        firebase_uid = COALESCE(
            current_setting('request.jwt.claims', true)::json->>'sub',
            ''
        )
    );

CREATE POLICY "users_update_own"
    ON users FOR UPDATE
    USING (
        firebase_uid = COALESCE(
            current_setting('request.jwt.claims', true)::json->>'sub',
            ''
        )
    );

-- ── board_credentials ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS board_credentials (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    board        TEXT NOT NULL,                   -- linkedin | indeed | glassdoor | …
    username_enc TEXT NOT NULL,                   -- Fernet-encrypted job-board username
    password_enc TEXT NOT NULL,                   -- Fernet-encrypted job-board password
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT board_credentials_user_board_unique UNIQUE (user_id, board)
);

-- Row-Level Security
ALTER TABLE board_credentials ENABLE ROW LEVEL SECURITY;

CREATE POLICY "board_credentials_select_own"
    ON board_credentials FOR SELECT
    USING (
        user_id = (
            SELECT id FROM users
            WHERE firebase_uid = COALESCE(
                current_setting('request.jwt.claims', true)::json->>'sub',
                ''
            )
        )
    );

CREATE POLICY "board_credentials_all_own"
    ON board_credentials FOR ALL
    USING (
        user_id = (
            SELECT id FROM users
            WHERE firebase_uid = COALESCE(
                current_setting('request.jwt.claims', true)::json->>'sub',
                ''
            )
        )
    );

-- ── Indexes ───────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_board_credentials_user_id ON board_credentials(user_id);
