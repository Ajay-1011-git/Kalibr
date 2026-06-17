-- ============================================================
-- Migration: 002_resumes
-- Tables:    resumes
-- Requires:  001_initial_schema (users table must exist)
-- ============================================================

-- ── pgvector extension ─────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;

-- ── resumes ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resumes (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    display_name  TEXT        NOT NULL,
    source_format TEXT        NOT NULL CHECK (source_format IN ('pdf', 'docx')),
    storage_path  TEXT        NOT NULL,

    -- Parse outputs
    structured    JSONB,                         -- StructuredResume JSON
    fingerprint   JSONB,                         -- DocxFingerprint | PdfFingerprint JSON
    embedding     vector(384),                   -- all-MiniLM-L6-v2 sentence embedding

    -- Status tracking
    parse_status  TEXT        NOT NULL DEFAULT 'pending'
                  CHECK (parse_status IN ('pending', 'processing', 'done', 'failed')),
    parse_error   TEXT,

    -- Timestamps
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at    TIMESTAMPTZ                    -- NULL = active; soft-delete via SET
);

-- ── Indexes ───────────────────────────────────────────────────────────────
-- Efficient list queries scoped to a user (excludes soft-deleted rows)
CREATE INDEX IF NOT EXISTS idx_resumes_user
    ON resumes(user_id)
    WHERE deleted_at IS NULL;

-- Vector similarity search (cosine distance)
-- NOTE: ivfflat requires at least one row before index builds efficiently.
--       In production, build AFTER the first batch of embeddings are loaded.
CREATE INDEX IF NOT EXISTS idx_resumes_embedding
    ON resumes
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ── Row-Level Security ────────────────────────────────────────────────────
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;

-- Backend uses service-role key (bypasses RLS).
-- These policies protect against direct anon-key / PostgREST access.

CREATE POLICY "resumes_select_own"
    ON resumes FOR SELECT
    USING (
        user_id = (
            SELECT id FROM users
            WHERE firebase_uid = COALESCE(
                current_setting('request.jwt.claims', true)::json->>'sub', ''
            )
        )
    );

CREATE POLICY "resumes_insert_own"
    ON resumes FOR INSERT
    WITH CHECK (
        user_id = (
            SELECT id FROM users
            WHERE firebase_uid = COALESCE(
                current_setting('request.jwt.claims', true)::json->>'sub', ''
            )
        )
    );

CREATE POLICY "resumes_update_own"
    ON resumes FOR UPDATE
    USING (
        user_id = (
            SELECT id FROM users
            WHERE firebase_uid = COALESCE(
                current_setting('request.jwt.claims', true)::json->>'sub', ''
            )
        )
    );

CREATE POLICY "resumes_delete_own"
    ON resumes FOR DELETE
    USING (
        user_id = (
            SELECT id FROM users
            WHERE firebase_uid = COALESCE(
                current_setting('request.jwt.claims', true)::json->>'sub', ''
            )
        )
    );
