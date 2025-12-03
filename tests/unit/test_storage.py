"""Unit tests for adk/storage.py

Tests StorageService CRUD operations for quizzes, concepts, knowledge gaps, and data export.
"""

import json
import pytest
from datetime import datetime
from adk.storage import StorageService, QuizResult, ConceptMastery, KnowledgeGap


class TestStorageService:
    """Tests for StorageService initialization and basic operations"""

    def test_storage_initialization(self, test_storage):
        """Test that storage initializes with correct user_id"""
        assert test_storage.user_id == "test_user"
        assert test_storage.db_path.exists()

    def test_storage_creates_tables(self, test_storage):
        """Test that all required tables are created"""
        conn = test_storage._get_connection()
        cursor = conn.cursor()

        # Check for required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        required_tables = {"quiz_results", "concept_mastery", "knowledge_gaps", "session_logs"}
        assert required_tables.issubset(tables), f"Missing tables: {required_tables - tables}"


class TestQuizOperations:
    """Tests for quiz CRUD operations"""

    def test_start_quiz(self, test_storage):
        """Test starting a new quiz"""
        quiz_id = test_storage.start_quiz(
            session_id="session_001",
            topic="Python Basics",
            total_questions=5
        )

        assert quiz_id is not None
        assert isinstance(quiz_id, int)

    def test_update_quiz_progress(self, test_storage):
        """Test updating quiz progress"""
        # Start quiz
        quiz_id = test_storage.start_quiz("session_001", "Python Basics", 5)

        # Update progress
        question_details = [
            {"question": "What is Python?", "correct": True, "concept": "Python Basics"}
        ]
        test_storage.update_quiz_progress(
            quiz_id=quiz_id,
            correct=1,
            mistakes=0,
            details=question_details
        )

        # Verify update
        conn = test_storage._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT correct_answers, total_mistakes FROM quiz_results WHERE id = ?", (quiz_id,))
        row = cursor.fetchone()

        assert row[0] == 1  # correct_answers
        assert row[1] == 0  # total_mistakes

    def test_complete_quiz(self, test_storage):
        """Test completing a quiz"""
        quiz_id = test_storage.start_quiz("session_001", "Python Basics", 5)

        # Complete quiz
        test_storage.complete_quiz(quiz_id)

        # Verify completion
        conn = test_storage._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT completed_at FROM quiz_results WHERE id = ?", (quiz_id,))
        completed_at = cursor.fetchone()[0]

        assert completed_at is not None

    def test_get_quiz_history(self, test_storage):
        """Test retrieving quiz history"""
        # Create multiple quizzes
        quiz1 = test_storage.start_quiz("session_001", "Python Basics", 5)
        quiz2 = test_storage.start_quiz("session_002", "Python Basics", 3)

        test_storage.complete_quiz(quiz1)
        test_storage.complete_quiz(quiz2)

        # Get history
        history = test_storage.get_quiz_history("Python Basics", limit=10)

        assert len(history) == 2
        assert all(isinstance(q, QuizResult) for q in history)


class TestConceptMastery:
    """Tests for concept mastery tracking"""

    def test_update_mastery_new_concept(self, test_storage):
        """Test tracking mastery for new concept"""
        test_storage.update_mastery("variables", correct=True)

        mastery = test_storage.get_mastery("variables")

        assert mastery is not None
        assert mastery.concept_name == "variables"
        assert mastery.times_seen == 1
        assert mastery.times_correct == 1
        assert mastery.mastery_level > 0

    def test_update_mastery_correct_answer(self, test_storage):
        """Test mastery increases with correct answers"""
        # First attempt
        test_storage.update_mastery("loops", correct=True)
        mastery1 = test_storage.get_mastery("loops")

        # Second correct attempt
        test_storage.update_mastery("loops", correct=True)
        mastery2 = test_storage.get_mastery("loops")

        assert mastery2.mastery_level > mastery1.mastery_level
        assert mastery2.times_correct == 2

    def test_update_mastery_incorrect_answer(self, test_storage):
        """Test mastery decreases with incorrect answers"""
        # Build up mastery
        for _ in range(3):
            test_storage.update_mastery("functions", correct=True)

        mastery_before = test_storage.get_mastery("functions")

        # Incorrect answer
        test_storage.update_mastery("functions", correct=False)
        mastery_after = test_storage.get_mastery("functions")

        assert mastery_after.mastery_level < mastery_before.mastery_level

    def test_get_weak_concepts(self, test_storage):
        """Test retrieving concepts below mastery threshold"""
        # Create concepts with different mastery levels
        for _ in range(5):
            test_storage.update_mastery("strong_concept", correct=True)

        test_storage.update_mastery("weak_concept", correct=False)
        test_storage.update_mastery("weak_concept", correct=False)

        weak = test_storage.get_weak_concepts(threshold=0.5)

        assert any(c.concept_name == "weak_concept" for c in weak)
        assert all(c.mastery_level < 0.5 for c in weak)

    def test_get_mastery_nonexistent_concept(self, test_storage):
        """Test retrieving mastery for concept that doesn't exist"""
        mastery = test_storage.get_mastery("nonexistent_concept")

        assert mastery is None


class TestKnowledgeGaps:
    """Tests for knowledge gap tracking"""

    def test_add_knowledge_gap(self, test_storage):
        """Test adding a knowledge gap"""
        gap_id = test_storage.add_knowledge_gap(
            concept="recursion",
            description="Difficulty understanding base cases",
            session_id="session_001"
        )

        assert gap_id is not None

    def test_get_active_gaps(self, test_storage):
        """Test retrieving active knowledge gaps"""
        # Add gaps
        test_storage.add_knowledge_gap("loops", "For loop confusion", "session_001")
        test_storage.add_knowledge_gap("arrays", "Index errors", "session_001")

        gaps = test_storage.get_active_gaps()

        assert len(gaps) == 2
        assert all(isinstance(g, KnowledgeGap) for g in gaps)
        assert all(not g.resolved for g in gaps)

    def test_resolve_gap(self, test_storage):
        """Test resolving a knowledge gap"""
        gap_id = test_storage.add_knowledge_gap("conditionals", "If/else logic", "session_001")

        # Resolve gap
        test_storage.resolve_gap(gap_id)

        # Verify resolution
        conn = test_storage._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT resolved, resolved_at FROM knowledge_gaps WHERE id = ?", (gap_id,))
        row = cursor.fetchone()

        assert row[0] == 1  # resolved
        assert row[1] is not None  # resolved_at


class TestUserStats:
    """Tests for user statistics and data export"""

    def test_get_user_stats(self, test_storage):
        """Test retrieving user statistics"""
        # Create some data
        quiz1 = test_storage.start_quiz("session_001", "Topic1", 3)
        test_storage.update_quiz_progress(quiz1, correct=2, mistakes=1, details=[])
        test_storage.complete_quiz(quiz1)

        test_storage.update_mastery("concept1", correct=True)
        test_storage.add_knowledge_gap("concept2", "Gap description", "session_001")

        stats = test_storage.get_user_stats()

        assert "total_quizzes" in stats
        assert "concepts_covered" in stats
        assert "active_knowledge_gaps" in stats
        assert stats["total_quizzes"] >= 1

    def test_export_progress(self, test_storage):
        """Test exporting all user progress data"""
        # Create sample data
        quiz1 = test_storage.start_quiz("session_001", "Topic1", 3)
        test_storage.complete_quiz(quiz1)
        test_storage.update_mastery("concept1", correct=True)

        export = test_storage.export_progress()

        assert "user_id" in export
        assert export["user_id"] == "test_user"
        assert "quiz_results" in export
        assert "concept_mastery" in export
        assert "knowledge_gaps" in export

    def test_export_progress_json_serializable(self, test_storage):
        """Test that exported data is JSON serializable"""
        # Create sample data
        quiz1 = test_storage.start_quiz("session_001", "Topic1", 3)
        test_storage.complete_quiz(quiz1)

        export = test_storage.export_progress()

        # Should not raise exception
        json_str = json.dumps(export)
        assert json_str is not None
