"""
Unit Tests for Section 2: Device Log Summarizer
"""

import json
import pytest
from pathlib import Path
from device_log_summarizer import DeviceAccumulator, DeviceLogSummarizer, DeviceSummary


class TestDeviceLogSummarizer:
    """Test suite for core data processing, aggregation, and filtering."""

    @pytest.fixture
    def sample_csv(self, tmp_path: Path) -> Path:
        """Creates a temporary valid CSV file."""
        csv_file = tmp_path / "telemetry_test.csv"
        content = (
            "device_id,status,temperature\n"
            "DEV_1,ACTIVE,60.0\n"
            "DEV_1,ERROR,70.0\n"
            "DEV_2,ACTIVE,90.0\n"
            "DEV_2,WARNING,85.0\n"
            "DEV_3,ACTIVE,40.0\n"
        )
        csv_file.write_text(content, encoding="utf-8")
        return csv_file

    def test_accumulator_calculations(self):
        """Tests that accumulator correctly calculates averages and counts errors."""
        acc = DeviceAccumulator()
        acc.add_record("ACTIVE", 60.0)
        acc.add_record("ERROR", 70.0)
        acc.add_record("WARNING", 80.0)

        assert acc.total_records == 3
        assert acc.error_count == 1
        assert acc.average_temperature == 70.0

    def test_accumulator_empty(self):
        """Tests accumulator with no records."""
        acc = DeviceAccumulator()
        assert acc.total_records == 0
        assert acc.average_temperature == 0.0
        assert acc.error_count == 0

    def test_processing_and_filtering(self, sample_csv: Path):
        """Tests that devices with average temp > 80.0 are filtered out."""
        summarizer = DeviceLogSummarizer(max_temp_threshold=80.0)
        kept, filtered, valid_rows, skipped_rows = summarizer.process(sample_csv)

        assert valid_rows == 5
        assert skipped_rows == 0

        # DEV_1: avg = 65.0 (kept)
        # DEV_2: avg = 87.5 (filtered out)
        # DEV_3: avg = 40.0 (kept)
        kept_ids = [s.device_id for s in kept]
        filtered_ids = [dev_id for dev_id, _ in filtered]

        assert "DEV_1" in kept_ids
        assert "DEV_3" in kept_ids
        assert "DEV_2" in filtered_ids

        dev_1_summary = next(s for s in kept if s.device_id == "DEV_1")
        assert dev_1_summary.total_records == 2
        assert dev_1_summary.average_temperature == 65.0
        assert dev_1_summary.error_count == 1

    def test_corrupted_rows_handling(self, tmp_path: Path):
        """Tests that corrupted or malformed rows are skipped without crashing."""
        noisy_csv = tmp_path / "noisy.csv"
        content = (
            "device_id,status,temperature\n"
            "DEV_X,ACTIVE,50.0\n"
            ",ACTIVE,60.0\n"                 # Missing device_id
            "DEV_X,ERROR,NOT_A_NUMBER\n"      # Invalid temperature
            "DEV_X,WARNING,70.0\n"
            "\n"                              # Empty row
        )
        noisy_csv.write_text(content, encoding="utf-8")

        summarizer = DeviceLogSummarizer()
        kept, filtered, valid_rows, skipped_rows = summarizer.process(noisy_csv)

        assert valid_rows == 2
        assert skipped_rows == 3
        assert len(kept) == 1
        assert kept[0].device_id == "DEV_X"
        assert kept[0].average_temperature == 60.0
        assert kept[0].error_count == 0  # The ERROR row had bad temperature and was skipped

    def test_missing_file_error(self):
        """Tests that non-existent CSV raises FileNotFoundError."""
        summarizer = DeviceLogSummarizer()
        with pytest.raises(FileNotFoundError):
            summarizer.process("non_existent_file.csv")

    def test_empty_file_error(self, tmp_path: Path):
        """Tests that empty CSV raises ValueError."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("", encoding="utf-8")

        summarizer = DeviceLogSummarizer()
        with pytest.raises(ValueError, match="empty"):
            summarizer.process(empty_csv)

    def test_missing_headers_error(self, tmp_path: Path):
        """Tests that CSV missing required columns raises ValueError."""
        bad_csv = tmp_path / "bad_headers.csv"
        bad_csv.write_text("col_a,col_b\n1,2\n", encoding="utf-8")

        summarizer = DeviceLogSummarizer()
        with pytest.raises(ValueError, match="missing required columns"):
            summarizer.process(bad_csv)

    def test_json_export(self, tmp_path: Path):
        """Tests JSON export content and structure."""
        out_json = tmp_path / "output.json"
        summaries = [
            DeviceSummary("DEV_TEST", 10, 65.4, 2)
        ]

        summarizer = DeviceLogSummarizer()
        summarizer.export_json(summaries, out_json)

        assert out_json.is_file()
        with out_json.open("r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0] == {
            "device_id": "DEV_TEST",
            "total_records": 10,
            "average_temperature": 65.4,
            "error_count": 2
        }
