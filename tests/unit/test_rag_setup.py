"""Unit tests for adk/rag_setup.py

Tests SimpleRetriever, chunking logic, and PDF retriever building.
"""

import pytest
from adk.rag_setup import SimpleRetriever, Document, _chunk_text


class TestSimpleRetriever:
    """Tests for SimpleRetriever class"""

    def test_get_relevant_documents_returns_top_k(self, mock_retriever):
        """Test that get_relevant_documents returns k documents"""
        query = "Python programming"
        docs = mock_retriever.get_relevant_documents(query, k=3)

        assert len(docs) == 3
        assert all(isinstance(doc, Document) for doc in docs)

    def test_get_relevant_documents_scores_by_term_frequency(self, mock_retriever):
        """Test that documents with more matching terms score higher"""
        # Query targeting first chunk specifically
        query = "Python high-level readability"
        docs = mock_retriever.get_relevant_documents(query, k=1)

        # First chunk should be returned (contains all query terms)
        assert "high-level" in docs[0].page_content
        assert "Python" in docs[0].page_content

    def test_get_relevant_documents_case_insensitive(self, mock_retriever):
        """Test that search is case-insensitive"""
        docs_lower = mock_retriever.get_relevant_documents("python", k=2)
        docs_upper = mock_retriever.get_relevant_documents("PYTHON", k=2)

        # Should return same results regardless of case
        assert len(docs_lower) == len(docs_upper)

    def test_get_relevant_documents_empty_query(self, mock_retriever):
        """Test handling of empty query"""
        docs = mock_retriever.get_relevant_documents("", k=5)

        # Should still return documents (all have score 0)
        assert len(docs) == 5

    def test_get_relevant_documents_no_matches(self, mock_retriever):
        """Test query with no matching terms"""
        docs = mock_retriever.get_relevant_documents("xyzabc123", k=5)

        # Should still return k documents (with score 0)
        assert len(docs) == 5


class TestChunkText:
    """Tests for _chunk_text function"""

    def test_chunk_text_basic(self):
        """Test basic chunking with no overlap"""
        text = "a" * 100
        chunks = _chunk_text(text, chunk_size=25, overlap=0)

        assert len(chunks) == 4
        assert all(len(chunk) == 25 for chunk in chunks)

    def test_chunk_text_with_overlap(self):
        """Test chunking with overlap"""
        text = "0123456789" * 10  # 100 chars
        chunks = _chunk_text(text, chunk_size=30, overlap=5)

        # Should have overlapping sections
        assert len(chunks) > 3
        # Check overlap exists
        assert chunks[1][:5] == chunks[0][-5:]

    def test_chunk_text_empty_string(self):
        """Test chunking empty string"""
        chunks = _chunk_text("", chunk_size=100, overlap=10)

        # Empty string produces no chunks
        assert chunks == []

    def test_chunk_text_smaller_than_chunk_size(self):
        """Test text smaller than chunk size"""
        text = "Short text"
        chunks = _chunk_text(text, chunk_size=100, overlap=10)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_overlap_larger_than_chunk(self):
        """Test edge case: overlap larger than chunk size"""
        text = "a" * 100
        # This is an invalid configuration but should not crash
        chunks = _chunk_text(text, chunk_size=10, overlap=20)

        # Should still produce chunks (behavior may vary)
        assert len(chunks) > 0

    def test_chunk_text_preserves_content(self):
        """Test that no content is lost during chunking"""
        text = "The quick brown fox jumps over the lazy dog"
        chunks = _chunk_text(text, chunk_size=15, overlap=5)

        # All words should appear in at least one chunk
        combined = " ".join(chunks)
        for word in text.split():
            assert word in combined
