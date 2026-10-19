# Device Log Summarizer

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/) [![Tests](https://img.shields.io/badge/Tests-22%20passed-brightgreen.svg)](./tests/)

A command-line tool and data processing pipeline developed for the **Software Engineering Intern Technical Assessment**. The project covers sensor data sanitization, device telemetry aggregation, statistical filtering, JSON reporting, data visualization, and automated testing.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Setup and Requirements](#setup-and-requirements)
- [Section 1: Data Cleaning and Normalization](#section-1-data-cleaning-and-normalization)
- [Section 2: Core Data Processing CLI Tool](#section-2-core-data-processing-cli-tool)
- [Section 3: AI Prompting and Visualization](#section-3-ai-prompting-and-visualization)
- [Running Unit Tests](#running-unit-tests)
- [Technologies Used](#technologies-used)

---

## Project Structure

```text
.
├── section1_sanitization.py    # Section 1: Data cleaning and clipping
├── device_log_summarizer.py    # Section 2: Telemetry aggregation and CLI
├── visualize_temperatures.py   # Section 3: Temperature visualization
├── device_telemetry.csv        # Sample input telemetry dataset
├── summary_output.json         # Exported JSON summary
├── device_temperatures.png     # Generated temperature bar chart
├── PROMPT_LOG.md               # AI prompt engineering log
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── tests/
    ├── __init__.py
    ├── test_sanitization.py    # Tests for Section 1
    ├── test_summarizer.py      # Tests for Section 2
    └── test_visualizer.py      # Tests for Section 3
```

---

## Setup and Requirements

### Prerequisites

- Python 3.9 or later
- `pip` package manager

### Installation

1. Clone or download the project repository.
2. Navigate to the project directory.
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Section 1: Data Cleaning and Normalization

**File:** `section1_sanitization.py`

This module implements the `clean_and_normalize_sensor_readings(readings)` function using pure Python.

### Features

- **Type conversion:** Converts valid numeric values to `float`.
- **Invalid value handling:** Discards `None`, Boolean values, and invalid strings.
- **Negative value filtering:** Removes values less than `0`.
- **Value clipping:** Caps readings exceeding `500.0` at `500.0`.
- **Input validation:** Handles empty lists and non-list inputs gracefully without raising exceptions.

### Execution

Run the module directly:

```bash
python section1_sanitization.py
```

---

## Section 2: Core Data Processing CLI Tool

**File:** `device_log_summarizer.py`

This module processes the `device_telemetry.csv` dataset, calculates device-level statistics, filters devices based on their average temperature, displays a formatted summary report, and exports the results to JSON.

### Features

- Reads device telemetry data from a CSV file.
- Aggregates records by device ID.
- Calculates average temperature and error counts.
- Excludes devices whose average temperature exceeds the configured threshold.
- Handles malformed rows and missing headers.
- Displays a formatted summary table in the terminal.
- Exports the processed summary to a JSON file.
- Supports configurable input paths, output paths, and temperature thresholds.

### Usage

**Run with default settings:**

```bash
python device_log_summarizer.py
```

**Specify a custom input file, output file, and temperature threshold:**

```bash
python device_log_summarizer.py device_telemetry.csv -o summary_output.json -m 80.0
```

### Command-Line Arguments

| Argument               | Description                                           |
| ---------------------- | ----------------------------------------------------- |
| `input_csv`            | Input CSV file (default: `device_telemetry.csv`)      |
| `-o`, `--output`       | Path to the output JSON file (default: `summary_output.json`) |
| `-m`, `--max-temp`     | Maximum permitted average temperature in °C (default: `80.0`) |
| `-v`, `--verbose`      | Enable diagnostic logging for corrupted or skipped rows |

### Sample Terminal Output

```text
========================================================================
                    DEVICE TELEMETRY SUMMARY REPORT
========================================================================
| Device ID | Total Records | Avg Temp (C) | Error Count | Filter Status       |
|-----------|---------------|--------------|-------------|---------------------|
| DEV_A     |             6 |        68.50 |           1 | PASS (<= 80.0)      |
| DEV_B     |             5 |        74.38 |           0 | PASS (<= 80.0)      |
| DEV_C     |             6 |        44.40 |           2 | PASS (<= 80.0)      |
| DEV_E     |             6 |        58.00 |           0 | PASS (<= 80.0)      |
| DEV_D     |             - |        86.64 |           - | EXCLUDED (> 80.0)   |
------------------------------------------------------------------------
Telemetry Rows Processed       : 28
Devices Retained (<= 80.0 C)   : 4
Devices Excluded (> 80.0 C)    : 1
========================================================================
[INFO] Successfully saved summary JSON to: .../summary_output.json
```

_The output above is an example report. Actual results and file paths depend on the input dataset and command-line arguments._

---

## Section 3: AI Prompting and Visualization

**Script:** `visualize_temperatures.py`  
**Deliverable:** `PROMPT_LOG.md`

This module generates a bar chart comparing the average temperature of each device using the data in `summary_output.json`.

### Features

- Uses Matplotlib to generate a temperature comparison chart.
- Configures the `Agg` backend for headless execution.
- Avoids Tkinter-related display issues in environments without a graphical interface.
- Rotates device labels by 15 degrees for improved readability.
- Uses `plt.tight_layout()` to prevent labels from being clipped.
- Displays average temperature values and error counts above each bar.
- Draws a dashed red reference line at the configured temperature threshold of `80.0°C`.

### Execution

Ensure that `summary_output.json` exists before generating the chart.

Run:

```bash
python visualize_temperatures.py
```

### Output

The script generates the following image:

`device_temperatures.png`

![Device Temperatures Chart](device_temperatures.png)

The chart provides a visual comparison of device temperatures and helps identify devices that approach or exceed the configured temperature threshold.

### AI Prompt Engineering Log

The `PROMPT_LOG.md` file documents the AI-assisted development process, including prompts used, implementation decisions, refinements, and relevant observations.

---

## Running Unit Tests

The project uses `pytest` to run automated tests for all three sections.

### Run the Full Test Suite

```bash
pytest -v
```

### Test Coverage

The test suite contains **22 test cases** across three modules.

| Test Module            | Number of Tests | Coverage                                                                                      |
| ---------------------- | --------------: | --------------------------------------------------------------------------------------------- |
| `test_sanitization.py` |               9 | Type conversion, negative values, clipping, Boolean handling, and edge cases                  |
| `test_summarizer.py`   |               8 | Statistical calculations, filtering, malformed rows, missing headers, and missing-file errors |
| `test_visualizer.py`   |               5 | JSON parsing, empty dataset fallback, and chart generation                                    |
| **Total**              |          **22** | **All three project sections**                                                                |

### Expected Result

```text
============================= test session starts =============================
...
22 passed
============================== 22 passed =====================================
```

_The expected result assumes all tests pass in the configured environment. The actual test output may vary by pytest version._

---

## Technologies Used

- **Python 3.9+:** Core programming language
- **CSV:** Telemetry data ingestion
- **JSON:** Structured summary export
- **Matplotlib:** Temperature data visualization
- **pytest:** Automated unit testing
- **argparse:** Command-line argument parsing and flag handling

---

## Key Project Objectives

This project demonstrates the following software engineering skills:

1. **Data sanitization:** Validating, converting, filtering, and clipping sensor readings.
2. **Data processing:** Aggregating telemetry records and calculating device-level statistics.
3. **Conditional filtering:** Applying temperature thresholds to determine device eligibility.
4. **File handling:** Reading CSV files and exporting JSON summaries.
5. **Command-line development:** Supporting configurable execution parameters.
6. **Data visualization:** Generating informative temperature comparison charts.
7. **Automated testing:** Validating expected behavior and handling edge cases.
8. **AI-assisted development:** Documenting prompt engineering and implementation workflows.

---

## Conclusion

The Device Log Summarizer provides an end-to-end telemetry processing workflow, from raw sensor readings to sanitized data, statistical summaries, filtered results, JSON exports, and visual reports.

The project combines modular Python development, input validation, command-line usability, automated testing, and visualization to demonstrate practical software engineering fundamentals.
