"""
Section 1: Coding Logic & Sanitization
--------------------------------------
Problem: Clean and Normalize Sensor Readings

Function:
    clean_and_normalize_sensor_readings(readings)

Requirements:
    1. Type Conversion & Filtering: Convert elements to floats where possible.
       Drop values that cannot be converted, are None, or are negative (< 0).
    2. Clipping: If any valid number exceeds 500.0, cap/limit it to 500.0.
    3. Edge Case Handling: Handle empty lists or lists with entirely invalid
       entries gracefully without throwing an unhandled exception.
"""

from typing import Any, List
import math


def clean_and_normalize_sensor_readings(readings: Any) -> List[float]:
    """
    Cleans and normalizes a sequence of raw sensor readings.

    Processing Steps:
    1. Gracefully handles None or non-iterable inputs by returning an empty list.
    2. Filters out None, booleans, non-numeric strings, and unconvertible types.
    3. Converts valid inputs to float.
    4. Drops negative readings (< 0.0) and non-numeric NaN values.
    5. Clips/caps any values exceeding 500.0 to 500.0.

    Args:
        readings (Any): An iterable of mixed sensor values (numbers, strings, None, etc.).

    Returns:
        List[float]: A list of sanitized and clipped floating-point sensor values.
    """
    if readings is None:
        return []

    # Handle cases where non-iterable or invalid types are passed
    if not isinstance(readings, (list, tuple, set)):
        return []

    cleaned: List[float] = []

    for item in readings:
        # None and booleans are dropped (in Python bool is a subclass of int, e.g. True == 1)
        if item is None or isinstance(item, bool):
            continue

        try:
            val = float(item)
        except (ValueError, TypeError):
            # Drop unconvertible strings or complex types
            continue

        # Drop NaN (Not a Number)
        if math.isnan(val):
            continue

        # Drop negative readings (< 0)
        if val < 0.0:
            continue

        # Clipping: Cap values exceeding 500.0 to 500.0
        if val > 500.0:
            val = 500.0

        cleaned.append(float(val))

    return cleaned


# =====================================================================
# Test Cases & Verification
# =====================================================================
def run_tests():
    """Runs deliverable test cases demonstrating all functional requirements."""
    print("Running Section 1: Sensor Readings Sanitization Tests...\n")

    # Test Case 1: Standard Mixed Input (Conversion, Filtering, Clipping)
    input_1 = [12.5, "45.2", None, -1.0, "ERR_FLAG", 600.0, 0.0, "100", 500.0]
    expected_1 = [12.5, 45.2, 500.0, 0.0, 100.0, 500.0]
    result_1 = clean_and_normalize_sensor_readings(input_1)
    assert result_1 == expected_1, f"Test 1 Failed: Expected {expected_1}, got {result_1}"
    print(f"Test 1 (Mixed Input):\n  Input:    {input_1}\n  Output:   {result_1} -> PASSED\n")

    # Test Case 2: Entirely Invalid Input (All items dropped gracefully)
    input_2 = [None, "SENSOR_TIMEOUT", -999.0, "-42.5", None, "N/A"]
    expected_2 = []
    result_2 = clean_and_normalize_sensor_readings(input_2)
    assert result_2 == expected_2, f"Test 2 Failed: Expected {expected_2}, got {result_2}"
    print(f"Test 2 (Entirely Invalid Input):\n  Input:    {input_2}\n  Output:   {result_2} -> PASSED\n")

    # Test Case 3: Empty List & Non-List Edge Cases
    input_3 = []
    expected_3 = []
    result_3 = clean_and_normalize_sensor_readings(input_3)
    assert result_3 == expected_3, f"Test 3 Failed: Expected {expected_3}, got {result_3}"
    print(f"Test 3 (Empty List):\n  Input:    {input_3}\n  Output:   {result_3} -> PASSED\n")

    # Bonus Edge Cases: Boundary Values & None input
    assert clean_and_normalize_sensor_readings(None) == []
    assert clean_and_normalize_sensor_readings([0.0, 500.0, 500.1, 12000.0]) == [0.0, 500.0, 500.0, 500.0]
    assert clean_and_normalize_sensor_readings([True, False, 25.0]) == [25.0]
    print("Bonus Boundary & Edge Tests -> PASSED\n")
    print("All Section 1 test cases passed successfully!")


if __name__ == "__main__":
    run_tests()
