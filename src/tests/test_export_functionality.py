"""Tests for export functionality."""

import csv
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

from ai_usage_monitor.utils.export import (
    export_to_csv,
    export_to_json,
    get_default_export_filename,
    validate_export_format,
)


@pytest.fixture
def sample_daily_data() -> List[Dict[str, Any]]:
    """Create sample daily aggregated data."""
    return [
        {
            "date": "2025-01-20",
            "tools": "claude-code",
            "models": "claude-sonnet-4",
            "input_tokens": 1000,
            "output_tokens": 500,
            "cache_creation_tokens": 100,
            "cache_read_tokens": 200,
            "total_tokens": 1800,
            "total_cost": 0.05,
            "entries_count": 10,
        },
        {
            "date": "2025-01-21",
            "tools": "claude-code",
            "models": "claude-sonnet-4",
            "input_tokens": 1500,
            "output_tokens": 750,
            "cache_creation_tokens": 150,
            "cache_read_tokens": 300,
            "total_tokens": 2700,
            "total_cost": 0.075,
            "entries_count": 15,
        },
    ]


@pytest.fixture
def sample_monthly_data() -> List[Dict[str, Any]]:
    """Create sample monthly aggregated data."""
    return [
        {
            "month": "2025-01",
            "tools": "claude-code,cline",
            "models": "claude-sonnet-4,claude-opus-4",
            "input_tokens": 50000,
            "output_tokens": 25000,
            "cache_creation_tokens": 5000,
            "cache_read_tokens": 10000,
            "total_tokens": 90000,
            "total_cost": 2.5,
            "entries_count": 500,
        },
    ]


class TestValidateExportFormat:
    """Tests for validate_export_format function."""

    def test_valid_json_format(self) -> None:
        """Test JSON format validation."""
        assert validate_export_format("json") is True
        assert validate_export_format("JSON") is True

    def test_valid_csv_format(self) -> None:
        """Test CSV format validation."""
        assert validate_export_format("csv") is True
        assert validate_export_format("CSV") is True

    def test_invalid_format(self) -> None:
        """Test invalid format validation."""
        assert validate_export_format("xml") is False
        assert validate_export_format("txt") is False
        assert validate_export_format("") is False


class TestGetDefaultExportFilename:
    """Tests for get_default_export_filename function."""

    def test_daily_json_filename(self) -> None:
        """Test default filename for daily JSON export."""
        filename = get_default_export_filename("daily", "json")
        assert filename.startswith("ai_usage_daily_")
        assert filename.endswith(".json")

    def test_monthly_csv_filename(self) -> None:
        """Test default filename for monthly CSV export."""
        filename = get_default_export_filename("monthly", "csv")
        assert filename.startswith("ai_usage_monthly_")
        assert filename.endswith(".csv")

    def test_filename_with_tool_name(self) -> None:
        """Test filename includes tool name."""
        filename = get_default_export_filename("daily", "json", "claude-code")
        assert "claude-code" in filename
        assert filename.endswith(".json")

    def test_filename_without_all_tool(self) -> None:
        """Test filename doesn't include 'all' tool name."""
        filename = get_default_export_filename("daily", "json", "all")
        assert "all" not in filename or filename.count("_") == 2  # Only timestamp


class TestExportToJSON:
    """Tests for export_to_json function."""

    def test_export_daily_json_to_file(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test exporting daily data to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.json"

            success = export_to_json(
                sample_daily_data,
                output_path,
                view_type="daily",
                tool_name="claude-code",
            )

            assert success is True
            assert output_path.exists()

            # Verify content
            with open(output_path, encoding="utf-8") as f:
                exported = json.load(f)

            assert exported["format"] == "ai-usage-monitor-export"
            assert exported["version"] == "1.0"
            assert exported["view_type"] == "daily"
            assert exported["tool"] == "claude-code"
            assert "exported_at" in exported
            assert len(exported["data"]) == 2
            assert exported["data"] == sample_daily_data

    def test_export_monthly_json_to_file(
        self, sample_monthly_data: List[Dict[str, Any]]
    ) -> None:
        """Test exporting monthly data to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "monthly.json"

            success = export_to_json(
                sample_monthly_data, output_path, view_type="monthly", tool_name="all"
            )

            assert success is True
            assert output_path.exists()

            with open(output_path, encoding="utf-8") as f:
                exported = json.load(f)

            assert exported["view_type"] == "monthly"
            assert exported["tool"] == "all"
            assert len(exported["data"]) == 1

    def test_export_json_creates_parent_directory(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test that export creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "nested" / "export.json"

            success = export_to_json(sample_daily_data, output_path, view_type="daily")

            assert success is True
            assert output_path.exists()
            assert output_path.parent.exists()

    def test_export_json_to_stdout(
        self, sample_daily_data: List[Dict[str, Any]], capsys
    ) -> None:
        """Test exporting JSON to stdout."""
        success = export_to_json(sample_daily_data, None, view_type="daily")

        assert success is True

        captured = capsys.readouterr()
        exported = json.loads(captured.out)

        assert exported["format"] == "ai-usage-monitor-export"
        assert len(exported["data"]) == 2

    def test_export_json_unknown_tool(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test export with no tool name defaults to 'unknown'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.json"

            success = export_to_json(sample_daily_data, output_path, view_type="daily")

            assert success is True

            with open(output_path, encoding="utf-8") as f:
                exported = json.load(f)

            assert exported["tool"] == "unknown"


class TestExportToCSV:
    """Tests for export_to_csv function."""

    def test_export_daily_csv_to_file(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test exporting daily data to CSV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"

            success = export_to_csv(
                sample_daily_data, output_path, view_type="daily"
            )

            assert success is True
            assert output_path.exists()

            # Verify content
            with open(output_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert len(rows) == 2
            assert rows[0]["date"] == "2025-01-20"
            assert rows[0]["input_tokens"] == "1000"
            assert rows[0]["total_cost"] == "0.05"

    def test_export_monthly_csv_to_file(
        self, sample_monthly_data: List[Dict[str, Any]]
    ) -> None:
        """Test exporting monthly data to CSV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "monthly.csv"

            success = export_to_csv(
                sample_monthly_data, output_path, view_type="monthly"
            )

            assert success is True
            assert output_path.exists()

            with open(output_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert len(rows) == 1
            assert rows[0]["month"] == "2025-01"
            assert rows[0]["total_tokens"] == "90000"

    def test_export_csv_creates_parent_directory(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test that CSV export creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "export.csv"

            success = export_to_csv(sample_daily_data, output_path, view_type="daily")

            assert success is True
            assert output_path.exists()

    def test_export_csv_to_stdout(
        self, sample_daily_data: List[Dict[str, Any]], capsys
    ) -> None:
        """Test exporting CSV to stdout."""
        success = export_to_csv(sample_daily_data, None, view_type="daily")

        assert success is True

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")

        # Check header
        assert "date" in lines[0]
        assert "input_tokens" in lines[0]

        # Check data rows
        assert len(lines) == 3  # Header + 2 data rows

    def test_export_csv_empty_data(self) -> None:
        """Test exporting empty data returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "empty.csv"

            success = export_to_csv([], output_path, view_type="daily")

            assert success is False
            assert not output_path.exists()

    def test_export_csv_correct_columns_daily(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test CSV has correct columns for daily view."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"

            export_to_csv(sample_daily_data, output_path, view_type="daily")

            with open(output_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)

            expected_columns = [
                "date",
                "tools",
                "models",
                "input_tokens",
                "output_tokens",
                "cache_creation_tokens",
                "cache_read_tokens",
                "total_tokens",
                "total_cost",
                "entries_count",
            ]

            assert header == expected_columns

    def test_export_csv_correct_columns_monthly(
        self, sample_monthly_data: List[Dict[str, Any]]
    ) -> None:
        """Test CSV has correct columns for monthly view."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"

            export_to_csv(sample_monthly_data, output_path, view_type="monthly")

            with open(output_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)

            expected_columns = [
                "month",
                "tools",
                "models",
                "input_tokens",
                "output_tokens",
                "cache_creation_tokens",
                "cache_read_tokens",
                "total_tokens",
                "total_cost",
                "entries_count",
            ]

            assert header == expected_columns


class TestExportIntegration:
    """Integration tests for export functionality."""

    def test_export_json_then_reimport(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test exporting to JSON and reimporting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.json"

            # Export
            export_to_json(sample_daily_data, output_path, view_type="daily")

            # Reimport
            with open(output_path, encoding="utf-8") as f:
                reimported = json.load(f)

            # Verify round-trip
            assert reimported["data"] == sample_daily_data

    def test_export_csv_then_reimport(
        self, sample_daily_data: List[Dict[str, Any]]
    ) -> None:
        """Test exporting to CSV and reimporting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "export.csv"

            # Export
            export_to_csv(sample_daily_data, output_path, view_type="daily")

            # Reimport
            with open(output_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                reimported = list(reader)

            # Verify data (note: CSV converts everything to strings)
            assert len(reimported) == len(sample_daily_data)
            assert reimported[0]["date"] == sample_daily_data[0]["date"]
            assert float(reimported[0]["total_cost"]) == sample_daily_data[0]["total_cost"]
