import math
from typing import Any, List


def clean_and_normalize_sensor_readings(readings: Any) -> List[float]:
    """
    Cleans raw sensor values by:
    - Converting elements to floats where possible
    - Dropping None, booleans, invalid types, and negative values (< 0)
    - Clipping values above 500.0 down to 500.0
    - Handling empty or non-iterable inputs gracefully
    """
    if not isinstance(readings, (list, tuple, set)):
        return []

    cleaned: List[float] = []

    for item in readings:
        # Skip None and booleans (in Python bool is a subclass of int)
        if item is None or isinstance(item, bool):
            continue

        try:
            val = float(item)
        except (ValueError, TypeError):
            continue

        # Drop NaN and negative numbers
        if math.isnan(val) or val < 0.0:
            continue

        # Cap at 500.0
        if val > 500.0:
            val = 500.0

        cleaned.append(float(val))

    return cleaned


if __name__ == "__main__":
    # Test Case 1: Mixed inputs (valid numbers, strings, negative flag, value > 500)
    sample_1 = [12.5, "45.2", None, -1.0, "ERR_FLAG", 600.0, 0.0, "100", 500.0]
    out_1 = clean_and_normalize_sensor_readings(sample_1)
    print("Test 1 Result:", out_1)
    assert out_1 == [12.5, 45.2, 500.0, 0.0, 100.0, 500.0]

    # Test Case 2: List with only invalid values
    sample_2 = [None, "SENSOR_TIMEOUT", -999.0, "-42.5", None, "N/A"]
    out_2 = clean_and_normalize_sensor_readings(sample_2)
    print("Test 2 Result:", out_2)
    assert out_2 == []

    # Test Case 3: Empty list
    sample_3 = []
    out_3 = clean_and_normalize_sensor_readings(sample_3)
    print("Test 3 Result:", out_3)
    assert out_3 == []

    print("\nAll sample test cases passed.")
