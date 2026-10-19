"""
CLI tool for ingesting device telemetry CSV data, calculating per-device summary
statistics, filtering by average temperature, and exporting results to JSON.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger("DeviceLogSummarizer")


@dataclass
class DeviceAccumulator:
    """Internal accumulator for streaming device telemetry records."""
    total_records: int = 0
    total_temperature: float = 0.0
    error_count: int = 0
    temperatures: List[float] = field(default_factory=list)

    def add_record(self, status: str, temperature: float) -> None:
        """Adds a valid telemetry record to the accumulator."""
        self.total_records += 1
        self.total_temperature += temperature
        self.temperatures.append(temperature)
        if status.strip().upper() == "ERROR":
            self.error_count += 1

    @property
    def average_temperature(self) -> float:
        """Computes mean temperature, rounded to 2 decimal places."""
        if self.total_records == 0:
            return 0.0
        return round(self.total_temperature / self.total_records, 2)


@dataclass
class DeviceSummary:
    """Export-ready aggregated summary for a single device."""
    device_id: str
    total_records: int
    average_temperature: float
    error_count: int

    def to_dict(self) -> Dict[str, object]:
        """Converts summary object to standard dictionary representation."""
        return {
            "device_id": self.device_id,
            "total_records": self.total_records,
            "average_temperature": self.average_temperature,
            "error_count": self.error_count
        }


class DeviceLogSummarizer:
    """
    Core engine for ingesting, aggregating, filtering, and exporting device telemetry.
    """

    REQUIRED_COLUMNS = {"device_id", "status", "temperature"}

    def __init__(self, max_temp_threshold: float = 80.0, verbose: bool = False) -> None:
        self.max_temp_threshold = float(max_temp_threshold)
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)

    def parse_csv(self, file_path: str | Path) -> Tuple[Dict[str, DeviceAccumulator], int, int]:
        """
        Reads CSV file and aggregates device statistics.

        Args:
            file_path: Path to the telemetry CSV file.

        Returns:
            Tuple of (device_accumulators, valid_row_count, skipped_row_count)

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If required CSV headers are missing or file is unreadable.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Telemetry CSV file not found: {path.resolve()}")

        accumulators: Dict[str, DeviceAccumulator] = {}
        valid_rows = 0
        skipped_rows = 0

        with path.open(mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)

            try:
                raw_header = next(reader)
            except StopIteration:
                raise ValueError("Telemetry CSV file is empty.")

            # Normalize header names (lowercase & stripped)
            headers = [h.strip().lower() for h in raw_header]
            header_map = {name: idx for idx, name in enumerate(headers)}

            missing_cols = self.REQUIRED_COLUMNS - set(header_map.keys())
            if missing_cols:
                raise ValueError(
                    f"CSV missing required columns: {sorted(list(missing_cols))}. "
                    f"Found columns: {headers}"
                )

            device_id_idx = header_map["device_id"]
            status_idx = header_map["status"]
            temp_idx = header_map["temperature"]

            for line_no, row in enumerate(reader, start=2):
                # Guard against short or empty rows
                if not row or len(row) <= max(device_id_idx, status_idx, temp_idx):
                    skipped_rows += 1
                    if self.verbose:
                        logger.warning(f"Line {line_no}: Incomplete row, skipped. ({row})")
                    continue

                raw_device = row[device_id_idx].strip()
                raw_status = row[status_idx].strip()
                raw_temp = row[temp_idx].strip()

                if not raw_device:
                    skipped_rows += 1
                    if self.verbose:
                        logger.warning(f"Line {line_no}: Missing device_id, skipped.")
                    continue

                try:
                    temp_val = float(raw_temp)
                    if math.isnan(temp_val) or math.isinf(temp_val):
                        raise ValueError("Non-finite temperature")
                except (ValueError, TypeError):
                    skipped_rows += 1
                    if self.verbose:
                        logger.warning(f"Line {line_no}: Invalid temperature '{raw_temp}', skipped.")
                    continue

                if raw_device not in accumulators:
                    accumulators[raw_device] = DeviceAccumulator()

                accumulators[raw_device].add_record(raw_status, temp_val)
                valid_rows += 1

        return accumulators, valid_rows, skipped_rows

    def process(self, file_path: str | Path) -> Tuple[List[DeviceSummary], List[Tuple[str, float]], int, int]:
        """
        Parses data, computes metrics, and applies temperature filtering.

        Returns:
            Tuple of:
            - kept_summaries (List[DeviceSummary])
            - filtered_out_devices (List of (device_id, avg_temp))
            - valid_rows count
            - skipped_rows count
        """
        accumulators, valid_rows, skipped_rows = self.parse_csv(file_path)

        kept: List[DeviceSummary] = []
        filtered_out: List[Tuple[str, float]] = []

        # Sort by device_id for deterministic and clean reporting
        for device_id in sorted(accumulators.keys()):
            acc = accumulators[device_id]
            avg_temp = acc.average_temperature

            if avg_temp > self.max_temp_threshold:
                filtered_out.append((device_id, avg_temp))
            else:
                summary = DeviceSummary(
                    device_id=device_id,
                    total_records=acc.total_records,
                    average_temperature=avg_temp,
                    error_count=acc.error_count
                )
                kept.append(summary)

        return kept, filtered_out, valid_rows, skipped_rows

    def export_json(self, summaries: List[DeviceSummary], output_path: str | Path) -> Path:
        """
        Exports summarized device metrics to formatted JSON.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        payload = [s.to_dict() for s in summaries]

        with out_file.open(mode="w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

        return out_file

    def print_terminal_table(
        self,
        kept: List[DeviceSummary],
        filtered: List[Tuple[str, float]],
        valid_rows: int,
        skipped_rows: int
    ) -> None:
        """
        Prints an aesthetically formatted summary table in the terminal.
        Compatible across all OS consoles (Windows cmd/PowerShell/Linux).
        """
        title = "DEVICE TELEMETRY SUMMARY REPORT"
        sep_len = 72
        print("\n" + "=" * sep_len)
        print(f"{title:^{sep_len}}")
        print("=" * sep_len)

        # Header
        col_dev = "Device ID"
        col_rec = "Total Records"
        col_avg = "Avg Temp (C)"
        col_err = "Error Count"
        col_status = "Filter Status"

        header_line = f"| {col_dev:<12} | {col_rec:>13} | {col_avg:>13} | {col_err:>11} | {col_status:<15} |"
        divider_line = f"|{'-' * 14}|{'-' * 15}|{'-' * 15}|{'-' * 13}|{'-' * 17}|"

        print(header_line)
        print(divider_line)

        # Active kept devices
        if kept:
            for s in kept:
                status_str = f"PASS (<= {self.max_temp_threshold:.1f})"
                print(
                    f"| {s.device_id:<12} | {s.total_records:>13} | "
                    f"{s.average_temperature:>13.2f} | {s.error_count:>11} | "
                    f"{status_str:<15} |"
                )
        else:
            print(f"| {'No devices passed the filter':^68} |")

        # Filtered out devices
        if filtered:
            for dev_id, avg_t in filtered:
                status_str = f"EXCLUDED (> {self.max_temp_threshold:.1f})"
                print(
                    f"| {dev_id:<12} | {'-':>13} | {avg_t:>13.2f} | {'-':>11} | "
                    f"{status_str:<15} |"
                )

        print("-" * sep_len)
        print(f" Telemetry Rows Processed : {valid_rows}")
        if skipped_rows > 0:
            print(f" Skipped / Corrupted Rows : {skipped_rows}")
        print(f" Devices Retained (<= {self.max_temp_threshold} C) : {len(kept)}")
        print(f" Devices Excluded (> {self.max_temp_threshold} C)  : {len(filtered)}")
        print("=" * sep_len + "\n")


def build_arg_parser() -> argparse.ArgumentParser:
    """Builds and configures the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="device_log_summarizer",
        description="Device Log Summarizer CLI: Ingests telemetry CSV, aggregates statistics, filters, and exports JSON."
    )
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="device_telemetry.csv",
        help="Path to telemetry CSV file (default: device_telemetry.csv)"
    )
    parser.add_argument(
        "-o", "--output",
        default="summary_output.json",
        help="Path to output JSON file (default: summary_output.json)"
    )
    parser.add_argument(
        "-m", "--max-temp",
        type=float,
        default=80.0,
        help="Maximum allowable average temperature threshold in °C (default: 80.0)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed diagnostic logging for skipped or corrupted rows"
    )
    return parser


def main() -> int:
    """CLI entrypoint."""
    parser = build_arg_parser()
    args = parser.parse_args()

    summarizer = DeviceLogSummarizer(
        max_temp_threshold=args.max_temp,
        verbose=args.verbose
    )

    try:
        kept, filtered, valid_rows, skipped_rows = summarizer.process(args.input_csv)
    except FileNotFoundError as err:
        logger.error(f"Error: {err}")
        return 1
    except ValueError as err:
        logger.error(f"Data Validation Error: {err}")
        return 1
    except Exception as err:
        logger.error(f"Unexpected error while processing telemetry: {err}")
        return 1

    # Export to JSON
    try:
        exported_path = summarizer.export_json(kept, args.output)
    except Exception as err:
        logger.error(f"Failed to write output JSON to '{args.output}': {err}")
        return 1

    # Print summary table in terminal
    summarizer.print_terminal_table(kept, filtered, valid_rows, skipped_rows)
    logger.info(f"Successfully saved summary JSON to: {exported_path.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
