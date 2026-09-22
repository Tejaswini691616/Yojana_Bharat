-- PATH: GovScheme/database/schema.sql
-- SmartGov AI - SQLite schema

PRAGMA foreign_keys = ON;

-- ============ USERS ============
CREATE TABLE IF NOT EXISTS users (
    user_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name          TEXT NOT NULL,
    email              TEXT NOT NULL UNIQUE,
    password_hash      TEXT NOT NULL,
    phone              TEXT,
    gender             TEXT,
    age                INTEGER,
    state              TEXT,
    district            TEXT,
    education          TEXT,
    occupation         TEXT,
    annual_income      INTEGER,
    caste              TEXT,
    farmer             TEXT DEFAULT 'No',
    student            TEXT DEFAULT 'No',
    disabled           TEXT DEFAULT 'No',
    senior_citizen     TEXT DEFAULT 'No',
    bpl                TEXT DEFAULT 'No',
    widow              TEXT DEFAULT 'No',
    land_holding_acres REAL DEFAULT 0,
    is_admin           INTEGER DEFAULT 0,
    preferred_language TEXT DEFAULT 'English',
    created_at         TEXT DEFAULT (datetime('now'))
);

-- ============ SCHEMES ============
CREATE TABLE IF NOT EXISTS schemes (
    scheme_id            TEXT PRIMARY KEY,
    scheme_name          TEXT NOT NULL,
    category             TEXT,
    description          TEXT,
    benefits             TEXT,
    eligibility          TEXT,
    documents_required   TEXT,
    official_link        TEXT,
    application_link     TEXT,
    state                TEXT DEFAULT 'All India',
    status               TEXT DEFAULT 'Active',
    source_url           TEXT,
    last_checked         TEXT,
    last_updated         TEXT,
    verification_status  TEXT DEFAULT 'Verified (prototype dataset)',
    -- structured rule fields preserved from Scheme_Master
    min_age              REAL,
    max_age              REAL,
    income_limit         REAL,
    caste_requirement    TEXT,
    farmer_required      INTEGER DEFAULT 0,
    bpl_required         INTEGER DEFAULT 0,
    land_limit_required  INTEGER DEFAULT 0,
    land_limit_acres     REAL,
    disability_required  INTEGER DEFAULT 0,
    student_required     INTEGER DEFAULT 0,
    widow_required       INTEGER DEFAULT 0
);

-- ============ APPLICATIONS ============
CREATE TABLE IF NOT EXISTS applications (
    application_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER NOT NULL REFERENCES users(user_id),
    scheme_id          TEXT NOT NULL REFERENCES schemes(scheme_id),
    application_date   TEXT DEFAULT (datetime('now')),
    status             TEXT DEFAULT 'Draft',
    application_number TEXT,
    remarks            TEXT,
    created_at         TEXT DEFAULT (datetime('now')),
    updated_at         TEXT DEFAULT (datetime('now'))
);

-- ============ SAVED SCHEMES ============
CREATE TABLE IF NOT EXISTS saved_schemes (
    saved_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(user_id),
    scheme_id   TEXT NOT NULL REFERENCES schemes(scheme_id),
    saved_date  TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, scheme_id)
);

-- ============ NOTIFICATIONS ============
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(user_id),
    title            TEXT NOT NULL,
    message          TEXT NOT NULL,
    status           TEXT DEFAULT 'Unread',
    created_at       TEXT DEFAULT (datetime('now'))
);

-- ============ ELIGIBILITY RESULTS (engine outputs, cached) ============
CREATE TABLE IF NOT EXISTS eligibility_results (
    result_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(user_id),
    scheme_id     TEXT NOT NULL REFERENCES schemes(scheme_id),
    is_eligible   INTEGER NOT NULL,
    explanation   TEXT,
    evaluated_at  TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, scheme_id)
);

-- ============ RECOMMENDATIONS (ML outputs, cached) ============
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER NOT NULL REFERENCES users(user_id),
    scheme_id          TEXT NOT NULL REFERENCES schemes(scheme_id),
    relevance_score    REAL,
    rank               INTEGER,
    generated_at       TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, scheme_id)
);

-- ============ SCHEME UPDATES (discovery pipeline log) ============
CREATE TABLE IF NOT EXISTS scheme_updates (
    update_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_id    TEXT,
    source       TEXT,
    change_type  TEXT,          -- NEW / UPDATED / UNCHANGED
    old_value    TEXT,
    new_value    TEXT,
    checked_at   TEXT DEFAULT (datetime('now'))
);

-- ============ AUTOMATION LOGS ============
CREATE TABLE IF NOT EXISTS automation_logs (
    log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name   TEXT,
    status     TEXT,
    details    TEXT,
    run_at     TEXT DEFAULT (datetime('now'))
);

-- ============ AUDIT LOGS ============
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    action      TEXT,
    details     TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- ============ RPA JOBS ============
CREATE TABLE IF NOT EXISTS rpa_jobs (
    rpa_job_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  INTEGER NOT NULL REFERENCES applications(application_id),
    status          TEXT DEFAULT 'Queued',
    application_number TEXT,
    remarks         TEXT,
    started_at      TEXT,
    completed_at    TEXT
);

-- ============ CHAT SESSIONS / MESSAGES ============
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(user_id),
    language    TEXT DEFAULT 'English',
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chat_messages (
    message_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES chat_sessions(session_id),
    sender      TEXT NOT NULL,   -- 'user' or 'bot'
    message     TEXT NOT NULL,
    language    TEXT,
    intent      TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_schemes(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_eligibility_user ON eligibility_results(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);
