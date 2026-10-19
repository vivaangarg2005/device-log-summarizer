"""
Unit Tests for Section 1: Sensor Readings Sanitization
"""

import pytest
from section1_sanitization import clean_and_normalize_sensor_readings


class TestSensorReadingsSanitization:
    """Test suite for clean_and_normalize_sensor_readings function."""

    def test_mixed_valid_and_invalid_inputs(self):
        """Tests standard conversion, filtering, and clipping."""
        raw_data = [12.5, "45.2", None, -1.0, "ERR_FLAG", 600.0, 0.0, "100", 500.0]
        expected = [12.5, 45.2, 500.0, 0.0, 100.0, 500.0]
        assert clean_and_normalize_sensor_readings(raw_data) == expected

    def test_empty_list(self):
        """Tests that an empty list returns an empty list gracefully."""
        assert clean_and_normalize_sensor_readings([]) == []

    def test_entirely_invalid_inputs(self):
        """Tests lists where no element is a valid non-negative float."""
        invalid_data = [None, "INVALID", -999.0, "-50", None, "N/A"]
        assert clean_and_normalize_sensor_readings(invalid_data) == []

    def test_non_list_inputs(self):
        """Tests graceful handling when non-list inputs are passed."""
        assert clean_and_normalize_sensor_readings(None) == []
        assert clean_and_normalize_sensor_readings(12345) == []
        assert clean_and_normalize_sensor_readings("single_string") == []

    def test_clipping_behavior(self):
        """Tests that any value > 500.0 is clipped to 500.0 exactly."""
        data = [499.9, 500.0, 500.01, 750.5, 100000.0]
        expected = [499.9, 500.0, 500.0, 500.0, 500.0]
        assert clean_and_normalize_sensor_readings(data) == expected

    def test_negative_filtering(self):
        """Tests that negative numbers and negative numeric strings are dropped."""
        data = [-0.0001, -1.0, "-45.6", -500.0]
        assert clean_and_normalize_sensor_readings(data) == []

    def test_zero_is_preserved(self):
        """Tests that zero (0.0) is not dropped as negative."""
        data = [0, 0.0, "0", "0.0"]
        assert clean_and_normalize_sensor_readings(data) == [0.0, 0.0, 0.0, 0.0]

    def test_boolean_filtering(self):
        """Tests that booleans (True/False) are not treated as 1.0/0.0."""
        data = [True, False, 25.0]
        assert clean_and_normalize_sensor_readings(data) == [25.0]

    def test_whitespace_strings(self):
        """Tests that numeric strings with surrounding whitespace convert properly."""
        data = [" 12.3 ", " 400 "]
        assert clean_and_normalize_sensor_readings(data) == [12.3, 400.0]
