"""
Unit Tests for Section 3: Visualization Script
"""

import json
import pytest
from pathlib import Path
from visualize_temperatures import generate_temperature_chart, load_telemetry_summary


class TestVisualizer:
    """Test suite for the temperature visualization module."""

    def test_load_telemetry_summary_valid(self, tmp_path: Path):
        """Tests reading a valid summary JSON."""
        json_file = tmp_path / "valid.json"
        content = [
            {"device_id": "DEV_A", "total_records": 5, "average_temperature": 70.0, "error_count": 0}
        ]
        json_file.write_text(json.dumps(content), encoding="utf-8")

        data = load_telemetry_summary(json_file)
        assert len(data) == 1
        assert data[0]["device_id"] == "DEV_A"

    def test_load_telemetry_summary_missing_file(self):
        """Tests that missing JSON raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_telemetry_summary("non_existent_summary.json")

    def test_load_telemetry_summary_invalid_json(self, tmp_path: Path):
        """Tests that malformed JSON raises ValueError."""
        json_file = tmp_path / "corrupt.json"
        json_file.write_text("{ incomplete json", encoding="utf-8")
        with pytest.raises(ValueError):
            load_telemetry_summary(json_file)

    def test_generate_chart_creates_image(self, tmp_path: Path):
        """Tests that chart generation produces a valid non-empty PNG file."""
        chart_png = tmp_path / "test_chart.png"
        sample_data = [
            {"device_id": "DEV_A", "total_records": 5, "average_temperature": 65.5, "error_count": 1},
            {"device_id": "DEV_B", "total_records": 8, "average_temperature": 72.0, "error_count": 0}
        ]

        saved_path = generate_temperature_chart(sample_data, chart_png)
        assert saved_path.is_file()
        assert saved_path.stat().st_size > 1000  # Check image is not empty

    def test_generate_chart_empty_dataset(self, tmp_path: Path):
        """Tests that chart generator handles empty input gracefully without raising."""
        chart_png = tmp_path / "empty_chart.png"
        saved_path = generate_temperature_chart([], chart_png)
        assert saved_path.is_file()
        assert saved_path.stat().st_size > 1000
