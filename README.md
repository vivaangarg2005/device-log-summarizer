# Technical Assessment: Device Log Summarizer & Telemetry Analytics

> **Software Engineering Intern Assessment Submission**  
> Complete implementation covering **Section 1 (Data Sanitization)**, **Section 2 (Core CLI Data Processing)**, and **Section 3 (AI Prompting & Visualization Challenge)**.

---

## 📋 Overview of Deliverables

| Requirement | File / Artifact | Description |
|---|---|---|
| **Section 1: Data Sanitization** | [`section1_sanitization.py`](./section1_sanitization.py) | Pure Python function `clean_and_normalize_sensor_readings` with type conversion, clipping, and edge-case handling. |
| **Section 2: CLI Summarizer** | [`device_log_summarizer.py`](./device_log_summarizer.py) | CLI tool that ingests CSV, aggregates metrics per device, filters out `avg_temp > 80.0°C`, exports JSON, and prints a terminal table. |
| **Section 2: Sample Data & Output** | [`device_telemetry.csv`](./device_telemetry.csv)<br>[`summary_output.json`](./summary_output.json) | Sample input dataset and resulting JSON export demonstrating aggregation and filtering. |
| **Section 3: Visualization Module** | [`visualize_temperatures.py`](./visualize_temperatures.py)<br>[`device_temperatures.png`](./device_temperatures.png) | Matplotlib bar chart script and exported 300 DPI visualization comparing average temperatures. |
| **Section 3: AI Prompting Log** | [`PROMPT_LOG.md`](./PROMPT_LOG.md) | Detailed prompt log documenting initial prompt, identified flaws, and the follow-up prompt. |
| **Automated Test Suite** | [`tests/`](./tests/) | 22 comprehensive `pytest` unit tests covering all functions and edge cases (100% pass rate). |

---

## 🚀 Quick Start & How to Run

### 1. Prerequisites
- Python 3.9+ (tested on Python 3.13)
- Required packages:
  ```bash
  pip install matplotlib pandas pytest
  ```

---

### 2. Running Section 1: Coding Logic & Sanitization
Run the standalone script to execute built-in test assertions:
```bash
python section1_sanitization.py
```
**Sample Output:**
```text
Running Section 1: Sensor Readings Sanitization Tests...

Test 1 (Mixed Input):
  Input:    [12.5, '45.2', None, -1.0, 'ERR_FLAG', 600.0, 0.0, '100', 500.0]
  Output:   [12.5, 45.2, 500.0, 0.0, 100.0, 500.0] -> PASSED

Test 2 (Entirely Invalid Input):
  Input:    [None, 'SENSOR_TIMEOUT', -999.0, '-42.5', None, 'N/A']
  Output:   [] -> PASSED

Test 3 (Empty List):
  Input:    []
  Output:   [] -> PASSED

Bonus Boundary & Edge Tests -> PASSED
All Section 1 test cases passed successfully!
```

---

### 3. Running Section 2: Core Data Processing CLI Tool
Run the summarizer CLI with the default telemetry file:
```bash
python device_log_summarizer.py
```

Or specify custom inputs, output path, and filter threshold:
```bash
python device_log_summarizer.py device_telemetry.csv -o summary_output.json -m 80.0
```

**Terminal Output Example:**
```text
========================================================================
                    DEVICE TELEMETRY SUMMARY REPORT                     
========================================================================
| Device ID    | Total Records |  Avg Temp (C) | Error Count | Filter Status   |
|--------------|---------------|---------------|-------------|-----------------|
| DEV_A        |             6 |         68.50 |           1 | PASS (<= 80.0)  |
| DEV_B        |             5 |         74.38 |           0 | PASS (<= 80.0)  |
| DEV_C        |             6 |         44.40 |           2 | PASS (<= 80.0)  |
| DEV_E        |             6 |         58.00 |           0 | PASS (<= 80.0)  |
| DEV_D        |             - |         86.64 |           - | EXCLUDED (> 80.0) |
------------------------------------------------------------------------
 Telemetry Rows Processed : 28
 Devices Retained (<= 80.0 C) : 4
 Devices Excluded (> 80.0 C)  : 1
========================================================================
[INFO] Successfully saved summary JSON to: .../summary_output.json
```

---

### 4. Running Section 3: AI Charting & Visualization
Generate the bar chart from `summary_output.json`:
```bash
python visualize_temperatures.py
```
This saves `device_temperatures.png` (300 DPI, styled layout with reference threshold at 80.0°C and numeric labels).

---

### 5. Running the Automated Test Suite
Run the full test suite with verbose reporting:
```bash
pytest -v
```

All 22 test cases pass without any errors:
```text
tests/test_sanitization.py::TestSensorReadingsSanitization::test_mixed_valid_and_invalid_inputs PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_empty_list PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_entirely_invalid_inputs PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_non_list_inputs PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_clipping_behavior PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_negative_filtering PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_zero_is_preserved PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_boolean_filtering PASSED
tests/test_sanitization.py::TestSensorReadingsSanitization::test_whitespace_strings PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_accumulator_calculations PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_accumulator_empty PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_processing_and_filtering PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_corrupted_rows_handling PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_missing_file_error PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_empty_file_error PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_missing_headers_error PASSED
tests/test_summarizer.py::TestDeviceLogSummarizer::test_json_export PASSED
tests/test_visualizer.py::TestVisualizer::test_load_telemetry_summary_valid PASSED
tests/test_visualizer.py::TestVisualizer::test_load_telemetry_summary_missing_file PASSED
tests/test_visualizer.py::TestVisualizer::test_load_telemetry_summary_invalid_json PASSED
tests/test_visualizer.py::TestVisualizer::test_generate_chart_creates_image PASSED
tests/test_visualizer.py::TestVisualizer::test_generate_chart_empty_dataset PASSED

============================= 22 passed in 1.97s ==============================
```

---

## 🛡️ Robustness & Evaluation Criteria Compliance

### 1. Readability
- Follows PEP 8 standards with strict type annotations (`typing`), clear docstrings, and meaningful variable names.
- Logical separation of concerns across ingestion, processing, filtering, output formatting, and visualization.

### 2. Robustness
- **Missing CSV / Bad Path**: Catches `FileNotFoundError` and terminates with a clean, descriptive message and non-zero exit code instead of an unhandled crash.
- **Corrupt / Empty CSV**: Gracefully detects missing headers, empty files, non-numeric temperature entries, and malformed rows. Invalid rows are skipped without interrupting the processing of valid device data.
- **Empty / Edge Case Inputs**: Section 1 and Section 2 functions safely return empty collections without throwing `ZeroDivisionError` or `IndexError`.
- **Headless Backend**: Visualization uses the `Agg` backend to operate in CI/CD without requiring Tkinter or X11 displays.

### 3. AI Collaboration
- Detailed in [`PROMPT_LOG.md`](./PROMPT_LOG.md): Documents the progression from a basic AI-generated plot to an enterprise-ready visualization, detailing identified layout bugs (label collision, margin clipping, lack of annotations) and targeted follow-up prompts.
