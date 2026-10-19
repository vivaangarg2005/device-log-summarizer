"""
Generates a bar chart comparing average temperatures per device from summary JSON.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")  # Non-interactive, headless, robust backend (no Tkinter required)
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("DeviceVisualizer")


def load_telemetry_summary(json_path: str | Path) -> List[Dict[str, Any]]:
    """
    Safely loads and validates JSON summary data.

    Args:
        json_path: Path to the JSON summary file.

    Returns:
        List of device summary dictionaries.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        ValueError: If JSON syntax is invalid or schema is unexpected.
    """
    path = Path(json_path)
    if not path.is_file():
        raise FileNotFoundError(f"JSON summary file not found: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as err:
            raise ValueError(f"Failed to parse JSON: {err}")

    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of device summary objects.")

    return data


def generate_temperature_chart(
    summary_data: List[Dict[str, Any]],
    output_image_path: str | Path = "device_temperatures.png",
    threshold: float = 80.0
) -> Path:
    """
    Generates and saves a styled bar chart comparing average temperatures.

    Args:
        summary_data: List of device summary objects.
        output_image_path: Destination path for the generated chart image.
        threshold: The filtering threshold value to plot as a reference.

    Returns:
        Path to the saved image file.
    """
    out_path = Path(output_image_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Edge Case: Handle empty dataset gracefully
    if not summary_data:
        logger.warning("No device records provided in summary data. Generating placeholder graphic.")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(
            0.5, 0.5, "No devices to display (Empty Dataset)",
            horizontalalignment="center", verticalalignment="center",
            fontsize=14, color="#666666"
        )
        ax.axis("off")
        fig.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return out_path

    # Extract data series
    device_ids = [d.get("device_id", "Unknown") for d in summary_data]
    avg_temps = [float(d.get("average_temperature", 0.0)) for d in summary_data]
    error_counts = [int(d.get("error_count", 0)) for d in summary_data]

    # Chart Styling & Palette
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Professional color gradient: cooler cyan-blues for low temps, warmer orange-coral for higher temps
    bar_colors = ["#2b6cb0" if temp < 60.0 else "#dd6b20" if temp >= 75.0 else "#319795" for temp in avg_temps]

    bars = ax.bar(
        device_ids,
        avg_temps,
        color=bar_colors,
        width=0.55,
        edgecolor="#1a202c",
        linewidth=1.2,
        zorder=3
    )

    # Add numeric labels on top of each bar
    max_temp_val = max(avg_temps) if avg_temps else 100.0
    for bar, temp, errors in zip(bars, avg_temps, error_counts):
        height = bar.get_height()
        err_badge = f" ({errors} err)" if errors > 0 else ""
        ax.annotate(
            f"{temp:.1f}°C{err_badge}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),  # 5 points vertical offset
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9.5, fontweight="bold",
            color="#2d3748"
        )

    # Add threshold reference line (80.0°C)
    ax.axhline(
        y=threshold,
        color="#e53e3e",
        linestyle="--",
        linewidth=1.5,
        label=f"Max Filter Threshold ({threshold:.1f}°C)",
        zorder=4
    )

    # Axes, Title, and Labels
    ax.set_title("Average Temperature per Device (Filtered <= 80.0°C)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Device Identifier", fontsize=11, fontweight="semibold", labelpad=10)
    ax.set_ylabel("Average Temperature (°C)", fontsize=11, fontweight="semibold", labelpad=10)

    # Dynamic Y limits to ensure annotations fit comfortably
    upper_limit = max(threshold + 10.0, max_temp_val + 15.0)
    ax.set_ylim(0, upper_limit)

    # X-axis label layout protection: slight rotation and alignment to prevent overlapping
    ax.tick_params(axis="x", rotation=15, labelsize=10)
    ax.tick_params(axis="y", labelsize=10)

    # Gridlines and aesthetics
    ax.grid(axis="y", linestyle=":", alpha=0.5, color="#a0aec0", zorder=1)
    ax.set_axisbelow(True)

    # Spines styling
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#4a5568")

    ax.legend(loc="upper right", framealpha=0.9, fontsize=9.5)

    # Protect layout against clipping
    plt.tight_layout()

    # Save output
    fig.savefig(out_path, dpi=300)
    plt.close(fig)

    return out_path


def main() -> int:
    """CLI execution for chart generator."""
    input_json = "summary_output.json"
    output_png = "device_temperatures.png"

    if len(sys.argv) > 1:
        input_json = sys.argv[1]
    if len(sys.argv) > 2:
        output_png = sys.argv[2]

    logger.info(f"Loading summary JSON from: {input_json}")
    try:
        data = load_telemetry_summary(input_json)
    except Exception as err:
        logger.error(f"Error loading summary data: {err}")
        return 1

    logger.info(f"Loaded {len(data)} device records. Generating chart...")
    try:
        saved_file = generate_temperature_chart(data, output_png)
        logger.info(f"Chart successfully generated and saved to: {saved_file.resolve()}")
    except Exception as err:
        logger.error(f"Error rendering chart: {err}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
