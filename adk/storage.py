"""Persistent storage for user progress using SQLite.

Stores:
- Quiz results (topic, scores, timestamps, mistakes)
- Concepts mastered and knowledge gaps
- Session history and conversation logs
- Extracted concepts and relationships from PDFs
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default storage location
DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).parent.parent / "data"))


@dataclass
class QuizResult:
    """A single quiz attempt result."""

    id: Optional[int] = None
    user_id: str = ""
    session_id: str = ""
    topic: str = ""
    total_questions: int = 0
    correct_answers: int = 0
    total_mistakes: int = 0
    started_at: str = ""
    completed_at: str = ""
    question_details: str = ""  # JSON string of per-question data


@dataclass
class ConceptMastery:
    """Tracks user's mastery of a concept."""

    id: Optional[int] = None
    user_id: str = ""
    concept_name: str = ""
    mastery_level: float = 0.0  # 0.0 - 1.0
    times_seen: int = 0
    times_correct: int = 0
    last_seen: str = ""
    knowledge_type: str = ""  # declarative/procedural/conditional
    avg_difficulty_achieved: float = 3.0
    max_difficulty_achieved: int = 1
    difficulty_distribution: str = "{}"
    struggle_area: Optional[str] = None
    complexity: int = 3


@dataclass
class KnowledgeGap:
    """Identified knowledge gap for a user."""

    id: Optional[int] = None
    user_id: str = ""
    concept_name: str = ""
    gap_type: str = ""  # missing/weak/misconception
    identified_at: str = ""
    resolved_at: Optional[str] = None
    related_concepts: str = ""  # JSON array


@dataclass
class SessionLog:
    """Conversation session log entry."""

    id: Optional[int] = None
    user_id: str = ""
    session_id: str = ""
    role: str = ""  # user/assistant/system
    content: str = ""
    timestamp: str = ""
    agent_name: str = ""


@dataclass
class ExtractedConcept:
    """Concept extracted from educational content."""

    id: Optional[int] = None
    pdf_hash: str = ""  # Hash of source PDF for caching
    name: str = ""
    declarative: str = ""
    procedural: str = ""
    conditional_use: str = ""
    conditional_avoid: str = ""
    confidence: float = 0.0
    extracted_at: str = ""


@dataclass
class ConceptRelationship:
    """Relationship between concepts."""

    id: Optional[int] = None
    pdf_hash: str = ""
    source_concept: str = ""
    target_concept: str = ""
    relationship_type: str = ""  # depends-on, enables, part-of, etc.
    direction: str = ""  # A->B or bidirectional
    rationale: str = ""
    confidence: float = 0.0


class StorageService:
    """SQLite-based persistent storage for user learning progress."""

    def __init__(self, user_id: str, db_path: Optional[Path] = None):
        self.user_id = user_id
        self.db_path = db_path or (DATA_DIR / f"{user_id}.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_conn(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_conn() as conn:
            conn.executescript(
                """
                -- Quiz results
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    total_questions INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    total_mistakes INTEGER DEFAULT 0,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    question_details TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_results(user_id);
                CREATE INDEX IF NOT EXISTS idx_quiz_topic ON quiz_results(topic);

                -- Concept mastery tracking
                CREATE TABLE IF NOT EXISTS concept_mastery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    concept_name TEXT NOT NULL,
                    mastery_level REAL DEFAULT 0.0,
                    times_seen INTEGER DEFAULT 0,
                    times_correct INTEGER DEFAULT 0,
                    last_seen TEXT,
                    knowledge_type TEXT,
                    UNIQUE(user_id, concept_name)
                );
                CREATE INDEX IF NOT EXISTS idx_mastery_user ON concept_mastery(user_id);

                -- Knowledge gaps
                CREATE TABLE IF NOT EXISTS knowledge_gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    concept_name TEXT NOT NULL,
                    gap_type TEXT NOT NULL,
                    identified_at TEXT NOT NULL,
                    resolved_at TEXT,
                    related_concepts TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_gaps_user ON knowledge_gaps(user_id);

                -- Session conversation logs
                CREATE TABLE IF NOT EXISTS session_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_name TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_logs_session ON session_logs(session_id);

                -- Extracted concepts from PDFs
                CREATE TABLE IF NOT EXISTS extracted_concepts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pdf_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    declarative TEXT,
                    procedural TEXT,
                    conditional_use TEXT,
                    conditional_avoid TEXT,
                    confidence REAL DEFAULT 0.0,
                    extracted_at TEXT NOT NULL,
                    UNIQUE(pdf_hash, name)
                );
                CREATE INDEX IF NOT EXISTS idx_concepts_pdf ON extracted_concepts(pdf_hash);

                -- Concept relationships
                CREATE TABLE IF NOT EXISTS concept_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pdf_hash TEXT NOT NULL,
                    source_concept TEXT NOT NULL,
                    target_concept TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    direction TEXT,
                    rationale TEXT,
                    confidence REAL DEFAULT 0.0,
                    UNIQUE(pdf_hash, source_concept, target_concept, relationship_type)
                );
                CREATE INDEX IF NOT EXISTS idx_rels_pdf ON concept_relationships(pdf_hash);

                -- Performance records for difficulty decisions
                CREATE TABLE IF NOT EXISTS performance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    quiz_id INTEGER,
                    question_number INTEGER NOT NULL,
                    score REAL NOT NULL,
                    response_time_ms INTEGER DEFAULT 0,
                    hints_used INTEGER DEFAULT 0,
                    difficulty_level INTEGER NOT NULL,
                    concept_tested TEXT NOT NULL,
                    question_type TEXT,
                    in_optimal_zone INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (quiz_id) REFERENCES quiz_results(id)
                );
                CREATE INDEX IF NOT EXISTS idx_perf_user ON performance_records(user_id);
                CREATE INDEX IF NOT EXISTS idx_perf_session ON performance_records(session_id);
                CREATE INDEX IF NOT EXISTS idx_perf_concept ON performance_records(concept_tested);

                -- Difficulty adjustment history
                CREATE TABLE IF NOT EXISTS difficulty_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    previous_level INTEGER NOT NULL,
                    new_level INTEGER NOT NULL,
                    adjustment_type TEXT NOT NULL,
                    reason TEXT,
                    triggered_by TEXT NOT NULL,
                    scaffolding_recommended INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_diff_user ON difficulty_history(user_id);
                CREATE INDEX IF NOT EXISTS idx_diff_session ON difficulty_history(session_id);
            """
            )
            # Add columns to concept_mastery for difficulty tracking
            self._migrate_concept_mastery()

    def _migrate_concept_mastery(self):
        """Add difficulty-related columns to concept_mastery table if they don't exist."""
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # Check which columns exist
            cursor.execute("PRAGMA table_info(concept_mastery)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            # Add missing columns
            columns_to_add = {
                "avg_difficulty_achieved": "REAL DEFAULT 3.0",
                "max_difficulty_achieved": "INTEGER DEFAULT 1",
                "difficulty_distribution": "TEXT DEFAULT '{}'",
                "struggle_area": "TEXT",
                "complexity": "INTEGER DEFAULT 3"
            }

            for column_name, column_def in columns_to_add.items():
                if column_name not in existing_columns:
                    try:
                        conn.execute(
                            f"ALTER TABLE concept_mastery ADD COLUMN {column_name} {column_def}"
                        )
                    except sqlite3.OperationalError:
                        pass  # Column already exists

    # =========================================================================
    # Quiz Results
    # =========================================================================

    def start_quiz(self, session_id: str, topic: str, total_questions: int) -> int:
        """Record quiz start. Returns quiz result ID."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO quiz_results
                (user_id, session_id, topic, total_questions, started_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    self.user_id,
                    session_id,
                    topic,
                    total_questions,
                    datetime.utcnow().isoformat(),
                ),
            )
            return cursor.lastrowid

    def update_quiz_progress(
        self,
        quiz_id: int,
        correct_answers: int,
        total_mistakes: int,
        question_details: List[Dict],
    ):
        """Update quiz progress."""
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE quiz_results
                SET correct_answers = ?, total_mistakes = ?, question_details = ?
                WHERE id = ?
            """,
                (correct_answers, total_mistakes, json.dumps(question_details), quiz_id),
            )

    def complete_quiz(self, quiz_id: int):
        """Mark quiz as completed."""
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE quiz_results SET completed_at = ? WHERE id = ?
            """,
                (datetime.utcnow().isoformat(), quiz_id),
            )

    def get_quiz_history(
        self, topic: Optional[str] = None, limit: int = 10
    ) -> List[QuizResult]:
        """Get user's quiz history, optionally filtered by topic."""
        with self._get_conn() as conn:
            if topic:
                rows = conn.execute(
                    """
                    SELECT * FROM quiz_results
                    WHERE user_id = ? AND topic = ?
                    ORDER BY started_at DESC LIMIT ?
                """,
                    (self.user_id, topic, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM quiz_results
                    WHERE user_id = ?
                    ORDER BY started_at DESC LIMIT ?
                """,
                    (self.user_id, limit),
                ).fetchall()
            return [QuizResult(**dict(row)) for row in rows]

    # =========================================================================
    # Concept Mastery
    # =========================================================================

    def update_mastery(
        self, concept_name: str, correct: bool, knowledge_type: str = ""
    ):
        """Update mastery level for a concept after a quiz interaction."""
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            # Get current mastery
            row = conn.execute(
                """
                SELECT times_seen, times_correct, mastery_level
                FROM concept_mastery
                WHERE user_id = ? AND concept_name = ?
            """,
                (self.user_id, concept_name),
            ).fetchone()

            if row:
                times_seen = row["times_seen"] + 1
                times_correct = row["times_correct"] + (1 if correct else 0)
                # Simple mastery calculation: ratio with recency weighting
                mastery = times_correct / times_seen
                conn.execute(
                    """
                    UPDATE concept_mastery
                    SET times_seen = ?, times_correct = ?, mastery_level = ?,
                        last_seen = ?, knowledge_type = COALESCE(NULLIF(?, ''), knowledge_type)
                    WHERE user_id = ? AND concept_name = ?
                """,
                    (
                        times_seen,
                        times_correct,
                        mastery,
                        now,
                        knowledge_type,
                        self.user_id,
                        concept_name,
                    ),
                )
            else:
                mastery = 1.0 if correct else 0.0
                conn.execute(
                    """
                    INSERT INTO concept_mastery
                    (user_id, concept_name, mastery_level, times_seen, times_correct,
                     last_seen, knowledge_type)
                    VALUES (?, ?, ?, 1, ?, ?, ?)
                """,
                    (
                        self.user_id,
                        concept_name,
                        mastery,
                        1 if correct else 0,
                        now,
                        knowledge_type,
                    ),
                )

    def get_mastery(self, concept_name: str) -> Optional[ConceptMastery]:
        """Get mastery level for a specific concept."""
        with self._get_conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM concept_mastery
                WHERE user_id = ? AND concept_name = ?
            """,
                (self.user_id, concept_name),
            ).fetchone()
            return ConceptMastery(**dict(row)) if row else None

    def get_all_mastery(self, min_mastery: float = 0.0) -> List[ConceptMastery]:
        """Get all concept mastery levels for user."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM concept_mastery
                WHERE user_id = ? AND mastery_level >= ?
                ORDER BY mastery_level DESC
            """,
                (self.user_id, min_mastery),
            ).fetchall()
            return [ConceptMastery(**dict(row)) for row in rows]

    def get_weak_concepts(self, threshold: float = 0.5) -> List[ConceptMastery]:
        """Get concepts below mastery threshold."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM concept_mastery
                WHERE user_id = ? AND mastery_level < ?
                ORDER BY mastery_level ASC
            """,
                (self.user_id, threshold),
            ).fetchall()
            return [ConceptMastery(**dict(row)) for row in rows]

    # =========================================================================
    # Knowledge Gaps
    # =========================================================================

    def add_knowledge_gap(
        self,
        concept_name: str,
        gap_type: str,
        related_concepts: Optional[List[str]] = None,
    ) -> int:
        """Record a knowledge gap."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO knowledge_gaps
                (user_id, concept_name, gap_type, identified_at, related_concepts)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    self.user_id,
                    concept_name,
                    gap_type,
                    datetime.utcnow().isoformat(),
                    json.dumps(related_concepts or []),
                ),
            )
            return cursor.lastrowid

    def resolve_gap(self, gap_id: int):
        """Mark a knowledge gap as resolved."""
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE knowledge_gaps SET resolved_at = ? WHERE id = ?
            """,
                (datetime.utcnow().isoformat(), gap_id),
            )

    def get_active_gaps(self) -> List[KnowledgeGap]:
        """Get unresolved knowledge gaps."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM knowledge_gaps
                WHERE user_id = ? AND resolved_at IS NULL
                ORDER BY identified_at DESC
            """,
                (self.user_id,),
            ).fetchall()
            return [KnowledgeGap(**dict(row)) for row in rows]

    # =========================================================================
    # Session Logs
    # =========================================================================

    def log_message(
        self, session_id: str, role: str, content: str, agent_name: str = ""
    ):
        """Log a conversation message."""
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO session_logs
                (user_id, session_id, role, content, timestamp, agent_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    self.user_id,
                    session_id,
                    role,
                    content,
                    datetime.utcnow().isoformat(),
                    agent_name,
                ),
            )

    def get_session_history(self, session_id: str) -> List[SessionLog]:
        """Get conversation history for a session."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM session_logs
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """,
                (session_id,),
            ).fetchall()
            return [SessionLog(**dict(row)) for row in rows]

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent session summaries."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT session_id, MIN(timestamp) as started,
                       MAX(timestamp) as last_activity,
                       COUNT(*) as message_count
                FROM session_logs
                WHERE user_id = ?
                GROUP BY session_id
                ORDER BY started DESC LIMIT ?
            """,
                (self.user_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    # =========================================================================
    # Extracted Concepts (for caching PDF processing)
    # =========================================================================

    def save_extracted_concepts(
        self, pdf_hash: str, concepts: List[Dict[str, Any]]
    ):
        """Save concepts extracted from a PDF."""
        now = datetime.utcnow().isoformat()
        with self._get_conn() as conn:
            for concept in concepts:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO extracted_concepts
                    (pdf_hash, name, declarative, procedural, conditional_use,
                     conditional_avoid, confidence, extracted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        pdf_hash,
                        concept.get("name", ""),
                        concept.get("declarative", ""),
                        concept.get("procedural", ""),
                        concept.get("conditional_use", ""),
                        concept.get("conditional_avoid", ""),
                        concept.get("confidence", 0.0),
                        now,
                    ),
                )

    def get_extracted_concepts(self, pdf_hash: str) -> List[ExtractedConcept]:
        """Get cached concepts for a PDF."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM extracted_concepts WHERE pdf_hash = ?
            """,
                (pdf_hash,),
            ).fetchall()
            return [ExtractedConcept(**dict(row)) for row in rows]

    def save_relationships(self, pdf_hash: str, relationships: List[Dict[str, Any]]):
        """Save concept relationships."""
        with self._get_conn() as conn:
            for rel in relationships:
                between = rel.get("between", [])
                if len(between) >= 2:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO concept_relationships
                        (pdf_hash, source_concept, target_concept, relationship_type,
                         direction, rationale, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            pdf_hash,
                            between[0],
                            between[1],
                            rel.get("type", ""),
                            rel.get("direction", ""),
                            rel.get("rationale", ""),
                            rel.get("confidence", 0.0),
                        ),
                    )

    def get_relationships(self, pdf_hash: str) -> List[ConceptRelationship]:
        """Get cached relationships for a PDF."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM concept_relationships WHERE pdf_hash = ?
            """,
                (pdf_hash,),
            ).fetchall()
            return [ConceptRelationship(**dict(row)) for row in rows]

    # =========================================================================
    # Performance Records (Adaptive Difficulty)
    # =========================================================================

    def save_performance_record(
        self,
        session_id: str,
        quiz_id: Optional[int],
        question_number: int,
        score: float,
        response_time_ms: int,
        hints_used: int,
        difficulty_level: int,
        concept_tested: str,
        question_type: str,
    ) -> int:
        """Save a performance record. Returns record ID."""
        in_optimal_zone = 1 if 0.60 <= score <= 0.85 else 0
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO performance_records
                (user_id, session_id, quiz_id, question_number, score,
                 response_time_ms, hints_used, difficulty_level, concept_tested,
                 question_type, in_optimal_zone, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.user_id,
                    session_id,
                    quiz_id,
                    question_number,
                    score,
                    response_time_ms,
                    hints_used,
                    difficulty_level,
                    concept_tested,
                    question_type,
                    in_optimal_zone,
                    datetime.utcnow().isoformat(),
                ),
            )
            return cursor.lastrowid

    def get_recent_performance_records(
        self, session_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent performance records for a session."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM performance_records
                WHERE user_id = ? AND session_id = ?
                ORDER BY id DESC
                LIMIT ?
            """,
                (self.user_id, session_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_performance_by_concept(
        self, concept_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get performance records for a specific concept."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM performance_records
                WHERE user_id = ? AND concept_tested = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (self.user_id, concept_name, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    # =========================================================================
    # Difficulty Adjustment History
    # =========================================================================

    def save_difficulty_adjustment(
        self,
        session_id: str,
        previous_level: int,
        new_level: int,
        adjustment_type: str,
        reason: str,
        triggered_by: str,
        scaffolding_recommended: bool,
    ) -> int:
        """Save a difficulty adjustment record. Returns record ID."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO difficulty_history
                (user_id, session_id, previous_level, new_level, adjustment_type,
                 reason, triggered_by, scaffolding_recommended, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.user_id,
                    session_id,
                    previous_level,
                    new_level,
                    adjustment_type,
                    reason,
                    triggered_by,
                    1 if scaffolding_recommended else 0,
                    datetime.utcnow().isoformat(),
                ),
            )
            return cursor.lastrowid

    def get_difficulty_history(
        self, session_id: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get difficulty adjustment history."""
        with self._get_conn() as conn:
            if session_id:
                rows = conn.execute(
                    """
                    SELECT * FROM difficulty_history
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (self.user_id, session_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM difficulty_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (self.user_id, limit),
                ).fetchall()
            return [dict(row) for row in rows]

    def get_last_difficulty_level(self, session_id: Optional[str] = None) -> Optional[int]:
        """Get the last difficulty level for a user (optionally for a specific session)."""
        with self._get_conn() as conn:
            if session_id:
                row = conn.execute(
                    """
                    SELECT new_level FROM difficulty_history
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """,
                    (self.user_id, session_id),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT new_level FROM difficulty_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """,
                    (self.user_id,),
                ).fetchone()
            return row[0] if row else None

    # =========================================================================
    # Summary / Stats
    # =========================================================================

    def get_user_stats(self) -> Dict[str, Any]:
        """Get overall user learning statistics."""
        with self._get_conn() as conn:
            quiz_stats = conn.execute(
                """
                SELECT
                    COUNT(*) as total_quizzes,
                    SUM(correct_answers) as total_correct,
                    SUM(total_questions) as total_questions,
                    SUM(total_mistakes) as total_mistakes,
                    COUNT(DISTINCT topic) as topics_studied
                FROM quiz_results WHERE user_id = ?
            """,
                (self.user_id,),
            ).fetchone()

            mastery_stats = conn.execute(
                """
                SELECT
                    COUNT(*) as concepts_seen,
                    AVG(mastery_level) as avg_mastery,
                    SUM(CASE WHEN mastery_level >= 0.8 THEN 1 ELSE 0 END) as mastered_count
                FROM concept_mastery WHERE user_id = ?
            """,
                (self.user_id,),
            ).fetchone()

            gap_stats = conn.execute(
                """
                SELECT
                    COUNT(*) as total_gaps,
                    SUM(CASE WHEN resolved_at IS NULL THEN 1 ELSE 0 END) as active_gaps
                FROM knowledge_gaps WHERE user_id = ?
            """,
                (self.user_id,),
            ).fetchone()

            return {
                "quizzes": dict(quiz_stats) if quiz_stats else {},
                "mastery": dict(mastery_stats) if mastery_stats else {},
                "gaps": dict(gap_stats) if gap_stats else {},
            }

    def export_progress(self) -> Dict[str, Any]:
        """Export all user progress as JSON-serializable dict."""
        return {
            "user_id": self.user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "stats": self.get_user_stats(),
            "quiz_history": [asdict(q) for q in self.get_quiz_history(limit=100)],
            "concept_mastery": [asdict(m) for m in self.get_all_mastery()],
            "knowledge_gaps": [asdict(g) for g in self.get_active_gaps()],
            "recent_sessions": self.get_recent_sessions(limit=20),
        }


# Global storage instance cache
_storage_cache: Dict[str, StorageService] = {}


def get_storage(user_id: str) -> StorageService:
    """Get or create storage service for a user."""
    if user_id not in _storage_cache:
        _storage_cache[user_id] = StorageService(user_id)
    return _storage_cache[user_id]


__all__ = [
    "StorageService",
    "get_storage",
    "QuizResult",
    "ConceptMastery",
    "KnowledgeGap",
    "SessionLog",
    "ExtractedConcept",
    "ConceptRelationship",
    "DATA_DIR",
]
