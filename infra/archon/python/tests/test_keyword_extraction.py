"""
Tests for keyword extraction and improved hybrid search
"""

import pytest

from src.server.services.search.keyword_extractor import (
    KeywordExtractor,
    build_search_terms,
    extract_keywords,
)


class TestKeywordExtractor:
    """Test keyword extraction functionality"""

    @pytest.fixture
    def extractor(self):
        return KeywordExtractor()

    def test_simple_keyword_extraction(self, extractor):
        """Test extraction from simple queries"""
        query = "Supabase authentication"
        keywords = extractor.extract_keywords(query)

        assert "supabase" in keywords
        assert "authentication" in keywords
        assert len(keywords) >= 2

    def test_complex_query_extraction(self, extractor):
        """Test extraction from complex queries"""
        query = "Supabase auth flow best practices"
        keywords = extractor.extract_keywords(query)

        assert "supabase" in keywords
        assert "auth" in keywords
        assert "flow" in keywords
        assert "best_practices" in keywords or "practices" in keywords

    def test_stop_word_filtering(self, extractor):
        """Test that stop words are filtered out"""
        query = "How to use the React component with the database"
        keywords = extractor.extract_keywords(query)

        # Stop words should be filtered
        assert "how" not in keywords
        assert "to" not in keywords
        assert "the" not in keywords
        assert "with" not in keywords

        # Technical terms should remain
        assert "react" in keywords
        assert "component" in keywords
        assert "database" in keywords

    def test_technical_terms_preserved(self, extractor):
        """Test that technical terms are preserved"""
        query = "PostgreSQL full-text search with Python API"
        keywords = extractor.extract_keywords(query)

        assert "postgresql" in keywords or "postgres" in keywords
        assert "python" in keywords
        assert "api" in keywords

    def test_compound_terms(self, extractor):
        """Test compound term detection"""
        query = "best practices for real-time websocket connections"
        keywords = extractor.extract_keywords(query)

        # Should detect compound terms
        assert "best_practices" in keywords
        assert "realtime" in keywords or "real-time" in keywords
        assert "websocket" in keywords

    def test_empty_query(self, extractor):
        """Test handling of empty query"""
        keywords = extractor.extract_keywords("")
        assert keywords == []

    def test_query_with_only_stopwords(self, extractor):
        """Test query with only stop words"""
        query = "the and with for in"
        keywords = extractor.extract_keywords(query)
        assert keywords == []

    def test_keyword_prioritization(self, extractor):
        """Test that keywords are properly prioritized"""
        query = "Python Python Django REST API framework Python"
        keywords = extractor.extract_keywords(query)

        # Python appears 3 times, should be prioritized
        assert keywords[0] == "python"

        # Technical terms should be high priority
        assert "django" in keywords[:3]
        assert "api" in keywords[:5]  # API should be in top 5

    def test_max_keywords_limit(self, extractor):
        """Test that max_keywords parameter is respected"""
        query = "Python Django Flask FastAPI React Vue Angular TypeScript JavaScript HTML CSS"
        keywords = extractor.extract_keywords(query, max_keywords=5)

        assert len(keywords) <= 5
        # Most important terms should be included
        assert "python" in keywords
        assert "django" in keywords

    def test_min_length_filtering(self, extractor):
        """Test minimum length filtering"""
        query = "a b c API JWT DB SQL"
        keywords = extractor.extract_keywords(query, min_length=3)

        # Single letters should be filtered
        assert "a" not in keywords
        assert "b" not in keywords
        assert "c" not in keywords

        # 3+ letter terms should remain
        assert "api" in keywords
        assert "jwt" in keywords
        assert "sql" in keywords


class TestSearchTermBuilder:
    """Test search term building with variations"""

    def test_plural_variations(self):
        """Test plural/singular variations"""
        keywords = ["functions", "class", "error"]
        terms = build_search_terms(keywords)

        # Should include singular of "functions"
        assert "function" in terms
        # Should include plural of "class"
        assert "classes" in terms
        # Should include plural of "error"
        assert "errors" in terms

    def test_verb_variations(self):
        """Test verb form variations"""
        keywords = ["creating", "updated", "testing"]
        terms = build_search_terms(keywords)

        # Should generate base forms
        assert "create" in terms or "creat" in terms
        assert "update" in terms or "updat" in terms
        assert "test" in terms

    def test_no_duplicates(self):
        """Test that duplicates are removed"""
        keywords = ["test", "tests", "testing"]
        terms = build_search_terms(keywords)

        # Should have unique terms only
        assert len(terms) == len(set(terms))


class TestIntegration:
    """Integration tests for keyword extraction in search context"""

    def test_real_world_query_1(self):
        """Test with real-world query example 1"""
        query = "How to implement JWT authentication in FastAPI with Supabase"
        keywords = extract_keywords(query)

        # Should extract the key technical terms
        assert "jwt" in keywords
        assert "authentication" in keywords
        assert "fastapi" in keywords
        assert "supabase" in keywords

        # Should not include generic words (implement is now filtered as technical stop word)
        assert "how" not in keywords
        assert "to" not in keywords

    def test_real_world_query_2(self):
        """Test with real-world query example 2"""
        query = "PostgreSQL full text search vs Elasticsearch performance comparison"
        keywords = extract_keywords(query)

        assert "postgresql" in keywords or "postgres" in keywords
        assert "elasticsearch" in keywords
        assert "performance" in keywords
        assert "comparison" in keywords

        # Should handle "full text" as compound or separate
        assert "fulltext" in keywords or ("full" in keywords and "text" in keywords)

    def test_real_world_query_3(self):
        """Test with real-world query example 3"""
        query = "debugging async await issues in Node.js Express middleware"
        keywords = extract_keywords(query)

        assert "debugging" in keywords or "debug" in keywords
        assert "async" in keywords
        assert "await" in keywords
        assert "express" in keywords
        assert "middleware" in keywords

        # Node.js might be split
        assert "nodejs" in keywords or "node" in keywords

    def test_code_related_query(self):
        """Test with code-related query"""
        query = "TypeError cannot read property undefined JavaScript React hooks"
        keywords = extract_keywords(query)

        assert "typeerror" in keywords or "type" in keywords
        assert "property" in keywords
        assert "undefined" in keywords
        assert "javascript" in keywords
        assert "react" in keywords
        assert "hooks" in keywords
