"""Tests for crawler utility functions."""

import pytest

from app.crawlers.crawler_utils import (
    clean_text,
    extract_numbers,
    parse_japanese_date,
)


class TestCleanText:
    """Tests for clean_text function."""

    def test_removes_extra_whitespace(self):
        """Test that extra whitespace is removed."""
        assert clean_text("  hello   world  ") == "hello world"

    def test_handles_full_width_space(self):
        """Test handling of Japanese full-width spaces."""
        assert clean_text("東京　電力") == "東京 電力"  # Full-width space

    def test_handles_newlines(self):
        """Test handling of newlines."""
        assert clean_text("line1\nline2\n") == "line1 line2"

    def test_handles_none(self):
        """Test handling of None input."""
        assert clean_text(None) == ""

    def test_handles_empty_string(self):
        """Test handling of empty string."""
        assert clean_text("") == ""


class TestExtractNumbers:
    """Tests for extract_numbers function."""

    def test_extracts_integers(self):
        """Test extracting integer numbers."""
        assert extract_numbers("基本料金 885円") == [885.0]

    def test_extracts_decimals(self):
        """Test extracting decimal numbers."""
        assert extract_numbers("29.80円/kWh") == [29.80]

    def test_extracts_multiple_numbers(self):
        """Test extracting multiple numbers."""
        result = extract_numbers("120kWhまで 29.80円 300kWh超過 40.49円")
        assert len(result) == 4
        assert 120.0 in result
        assert 29.80 in result
        assert 300.0 in result
        assert 40.49 in result

    def test_handles_comma_separated(self):
        """Test handling of comma-separated numbers."""
        assert extract_numbers("1,234円") == [1234.0]

    def test_handles_empty_string(self):
        """Test handling of empty string."""
        assert extract_numbers("") == []


class TestParseJapaneseDate:
    """Tests for parse_japanese_date function."""

    def test_western_year_format(self):
        """Test parsing Western year format (2024年4月1日)."""
        assert parse_japanese_date("2024年4月1日") == "2024-04-01"
        assert parse_japanese_date("2025年12月31日") == "2025-12-31"

    def test_reiwa_format(self):
        """Test parsing Reiwa era format (令和6年4月1日)."""
        assert parse_japanese_date("令和6年4月1日") == "2024-04-01"
        assert parse_japanese_date("令和1年5月1日") == "2019-05-01"

    def test_abbreviated_reiwa(self):
        """Test parsing abbreviated Reiwa format (R6.4.1)."""
        assert parse_japanese_date("R6.4.1") == "2024-04-01"
        assert parse_japanese_date("R1.5.1") == "2019-05-01"

    def test_heisei_format(self):
        """Test parsing Heisei era format."""
        assert parse_japanese_date("平成31年4月30日") == "2019-04-30"
        assert parse_japanese_date("H31.4.30") == "2019-04-30"

    def test_invalid_date(self):
        """Test handling of invalid dates."""
        assert parse_japanese_date("invalid date") is None
        assert parse_japanese_date("") is None

    def test_embedded_date(self):
        """Test extracting date from longer text."""
        assert parse_japanese_date("適用開始日: 2024年4月1日より") == "2024-04-01"
