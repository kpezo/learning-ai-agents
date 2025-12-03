-- Storage Schema Extensions for Pedagogical Metrics
-- Feature: 008-pedagogical-metrics
--
-- These extensions are applied to existing per-user SQLite databases
-- managed by adk/storage.py

-- =============================================================================
-- BKT Parameters Table
-- =============================================================================
-- Stores Bayesian Knowledge Tracing parameters per concept per user

CREATE TABLE IF NOT EXISTS bkt_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    concept_name TEXT NOT NULL,

    -- BKT model parameters
    p_l0 REAL DEFAULT 0.1 CHECK (p_l0 >= 0 AND p_l0 <= 1),
    p_t REAL DEFAULT 0.3 CHECK (p_t >= 0 AND p_t <= 1),
    p_g REAL DEFAULT 0.2 CHECK (p_g >= 0 AND p_g <= 0.5),
    p_s REAL DEFAULT 0.1 CHECK (p_s >= 0 AND p_s <= 0.3),

    -- Current state
    p_l_current REAL DEFAULT 0.1 CHECK (p_l_current >= 0 AND p_l_current <= 1),
    confidence_lower REAL DEFAULT 0.0,
    confidence_upper REAL DEFAULT 1.0,
    observations INTEGER DEFAULT 0,

    -- Metadata
    last_updated TEXT NOT NULL,

    -- Constraints
    UNIQUE(user_id, concept_name),
    CHECK (p_g + p_s < 1)  -- Prevents negative learning
);

CREATE INDEX IF NOT EXISTS idx_bkt_user ON bkt_parameters(user_id);
CREATE INDEX IF NOT EXISTS idx_bkt_concept ON bkt_parameters(user_id, concept_name);
CREATE INDEX IF NOT EXISTS idx_bkt_mastery ON bkt_parameters(p_l_current);


-- =============================================================================
-- Question Parameters Table (IRT)
-- =============================================================================
-- Stores Item Response Theory parameters for questions

CREATE TABLE IF NOT EXISTS question_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL UNIQUE,

    -- IRT 3PL parameters
    discrimination_a REAL DEFAULT 1.0 CHECK (discrimination_a >= 0.5 AND discrimination_a <= 2.5),
    difficulty_b REAL DEFAULT 0.0 CHECK (difficulty_b >= -3 AND difficulty_b <= 3),
    guessing_c REAL DEFAULT 0.25 CHECK (guessing_c >= 0 AND guessing_c <= 0.35),

    -- Empirical calibration data
    attempt_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    observed_rate REAL,
    fisher_info REAL,

    -- Calibration status
    calibrated INTEGER DEFAULT 0,
    last_calibrated TEXT,

    CHECK (success_count <= attempt_count)
);

CREATE INDEX IF NOT EXISTS idx_question_id ON question_parameters(question_id);
CREATE INDEX IF NOT EXISTS idx_question_calibrated ON question_parameters(calibrated);
CREATE INDEX IF NOT EXISTS idx_question_difficulty ON question_parameters(difficulty_b);


-- =============================================================================
-- Learner Ability Table
-- =============================================================================
-- Stores ability estimates (theta) per user per domain

CREATE TABLE IF NOT EXISTS learner_ability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    domain TEXT NOT NULL DEFAULT 'general',

    -- Ability estimate
    theta REAL DEFAULT 0.0 CHECK (theta >= -4 AND theta <= 4),
    standard_error REAL DEFAULT 1.0 CHECK (standard_error > 0),
    responses_count INTEGER DEFAULT 0,

    -- Metadata
    last_updated TEXT NOT NULL,

    UNIQUE(user_id, domain)
);

CREATE INDEX IF NOT EXISTS idx_ability_user ON learner_ability(user_id);
CREATE INDEX IF NOT EXISTS idx_ability_domain ON learner_ability(user_id, domain);


-- =============================================================================
-- ZPD Status Table
-- =============================================================================
-- Tracks Zone of Proximal Development status per concept

CREATE TABLE IF NOT EXISTS zpd_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    concept_name TEXT NOT NULL,

    -- ZPD assessment
    status TEXT DEFAULT 'optimal'
        CHECK (status IN ('frustration_risk', 'below_zpd', 'optimal', 'above_zpd', 'boredom_risk')),
    recent_success_rate REAL CHECK (recent_success_rate >= 0 AND recent_success_rate <= 1),

    -- Streak tracking
    consecutive_correct INTEGER DEFAULT 0,
    consecutive_incorrect INTEGER DEFAULT 0,

    -- Difficulty recommendation
    recommended_difficulty INTEGER DEFAULT 3 CHECK (recommended_difficulty >= 1 AND recommended_difficulty <= 6),

    -- Metadata
    last_evaluated TEXT NOT NULL,

    UNIQUE(user_id, concept_name)
);

CREATE INDEX IF NOT EXISTS idx_zpd_user ON zpd_status(user_id);
CREATE INDEX IF NOT EXISTS idx_zpd_status ON zpd_status(status);


-- =============================================================================
-- Behavioral Events Table
-- =============================================================================
-- Tracks behavioral indicators for frustration/boredom detection

CREATE TABLE IF NOT EXISTS behavioral_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,

    -- Event type
    event_type TEXT NOT NULL
        CHECK (event_type IN ('answer', 'hint_request', 'abandon', 'rapid_attempt', 'timeout')),
    timestamp TEXT NOT NULL,

    -- Context
    question_id TEXT,
    concept_name TEXT,

    -- Timing
    response_time_ms INTEGER CHECK (response_time_ms >= 0),
    expected_time_ms INTEGER CHECK (expected_time_ms > 0),

    -- Engagement metrics
    hints_used INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 1,
    correct INTEGER CHECK (correct IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_behavior_user ON behavioral_events(user_id);
CREATE INDEX IF NOT EXISTS idx_behavior_session ON behavioral_events(session_id);
CREATE INDEX IF NOT EXISTS idx_behavior_type ON behavioral_events(event_type);
CREATE INDEX IF NOT EXISTS idx_behavior_time ON behavioral_events(timestamp);


-- =============================================================================
-- Domain Thresholds Table
-- =============================================================================
-- Stores domain-specific mastery thresholds

CREATE TABLE IF NOT EXISTS domain_thresholds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,

    -- Threshold configuration
    mastery_threshold REAL DEFAULT 0.80 CHECK (mastery_threshold >= 0 AND mastery_threshold <= 1),
    consistency_count INTEGER DEFAULT 0 CHECK (consistency_count >= 0),

    -- Metadata
    description TEXT
);

-- Insert default domains
INSERT OR IGNORE INTO domain_thresholds (domain, mastery_threshold, consistency_count, description)
VALUES
    ('general', 0.80, 0, 'General educational content'),
    ('stem', 0.85, 3, 'STEM skills requiring procedural accuracy'),
    ('medical', 0.95, 5, 'Medical and safety-critical content'),
    ('safety', 0.95, 5, 'Safety-critical operational procedures'),
    ('language', 0.80, 0, 'Language learning with spaced repetition');


-- =============================================================================
-- Schema Extension for concept_mastery (existing table)
-- =============================================================================
-- Add columns to existing concept_mastery table from adk/storage.py

-- Note: These ALTER statements should be run conditionally
-- SQLite doesn't support IF NOT EXISTS for columns, so check in code

-- ALTER TABLE concept_mastery ADD COLUMN bkt_mastery REAL;
-- ALTER TABLE concept_mastery ADD COLUMN mastery_source TEXT DEFAULT 'simple';
-- ALTER TABLE concept_mastery ADD COLUMN domain TEXT DEFAULT 'general';


-- =============================================================================
-- Views for Common Queries
-- =============================================================================

-- Concepts needing attention (low mastery or frustration)
CREATE VIEW IF NOT EXISTS v_concepts_needing_attention AS
SELECT
    b.user_id,
    b.concept_name,
    b.p_l_current as mastery,
    z.status as zpd_status,
    z.recommended_difficulty
FROM bkt_parameters b
LEFT JOIN zpd_status z ON b.user_id = z.user_id AND b.concept_name = z.concept_name
WHERE b.p_l_current < 0.50
   OR z.status IN ('frustration_risk', 'below_zpd')
ORDER BY b.p_l_current ASC;

-- Learner progress summary
CREATE VIEW IF NOT EXISTS v_learner_progress AS
SELECT
    b.user_id,
    COUNT(*) as concepts_seen,
    AVG(b.p_l_current) as avg_mastery,
    SUM(CASE WHEN b.p_l_current >= 0.95 THEN 1 ELSE 0 END) as mastered_count,
    SUM(CASE WHEN b.p_l_current < 0.50 THEN 1 ELSE 0 END) as struggling_count
FROM bkt_parameters b
GROUP BY b.user_id;

-- Question calibration status
CREATE VIEW IF NOT EXISTS v_question_calibration AS
SELECT
    question_id,
    difficulty_b,
    discrimination_a,
    attempt_count,
    observed_rate,
    calibrated,
    CASE
        WHEN attempt_count < 50 THEN 'needs_data'
        WHEN calibrated = 0 THEN 'ready_to_calibrate'
        ELSE 'calibrated'
    END as status
FROM question_parameters
ORDER BY attempt_count DESC;
