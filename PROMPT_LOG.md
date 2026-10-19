# AI Collaboration & Prompt Log (`PROMPT_LOG.md`)

This log documents the iterative prompt engineering process used to guide the AI assistant in developing the Section 3 data visualization module (`visualize_temperatures.py`), identifying mistakes in the initial generated code, and applying targeted refinements.

---

## 1. Initial Prompt to the AI

```text
Write a Python script that loads the JSON output ('summary_output.json') generated from Section 2 
and creates a bar chart comparing the average temperature per device using matplotlib. 
Save the generated chart as 'device_temperatures.png'.
```

### Initial Code Returned by AI (First Attempt):
```python
import json
import matplotlib.pyplot as plt

with open('summary_output.json') as f:
    data = json.load(f)

devices = [item['device_id'] for item in data]
temps = [item['average_temperature'] for item in data]

plt.bar(devices, temps)
plt.title("Device Temperatures")
plt.xlabel("Device")
plt.ylabel("Avg Temp")
plt.savefig("device_temperatures.png")
plt.show()
```

---

## 2. Bugs & Formatting Mistakes in First Attempt

Upon reviewing the initial script, several significant formatting, layout, and robustness issues were identified:

1. **Label Overlap & Layout Clipping Bug**:
   - The x-axis device names were rendered strictly horizontally with no padding. In scenarios with longer device identifiers (e.g., `DEVICE_CLUSTER_NORTH_01`) or a larger number of devices, the labels collided with each other and the bottom edge was truncated because `plt.tight_layout()` was omitted.
2. **Missing Numeric Annotations**:
   - The bars had no data labels on top, forcing viewers to visually estimate the values against the y-axis ticks.
3. **Missing Contextual Threshold**:
   - Section 2 enforces an 80.0°C upper filter limit. The first attempt did not visualize this threshold, making it unclear whether devices were close to the cutoff.
4. **Crash on Edge Cases & Headless Environments**:
   - The script lacked error handling for missing files (`FileNotFoundError`), malformed JSON, or empty datasets (`[]`), which causes unhandled exceptions in headless or automated CLI environments.
   - Furthermore, in automated or headless test runs, the default Tkinter backend triggered a `_tkinter.TclError` due to missing Tk bindings, necessitating the non-interactive `'Agg'` backend.
5. **Low Resolution & Default Styling**:
   - Default matplotlib figure export was low DPI (72/100 DPI) and used raw non-styled default bars without gridlines.

---

## 3. Follow-up Prompt Used to Fix the Issues

```text
The initial script works for a basic plot, but has layout, robustness, and presentation flaws:
1. Label Overlap & Margins: Rotate the x-axis tick labels by 15-30 degrees and add `plt.tight_layout()` to prevent any label overlap or margin clipping.
2. Numeric Value Labels: Add exact temperature values (e.g. '68.5°C') formatted directly above each bar, along with the error count if greater than 0.
3. Reference Threshold: Add a horizontal dashed red reference line at y = 80.0°C labeled 'Max Filter Threshold (80.0°C)'.
4. Robustness & Headless Backend:
   - Configure `matplotlib.use("Agg")` before importing pyplot to ensure headless execution in CI/CD without Tkinter dependency.
   - Wrap file loading in a try/except block to handle FileNotFoundError, JSON syntax errors, and empty JSON lists gracefully without crashing.
5. Aesthetics & Resolution: Use a modern color palette, subtle horizontal gridlines, clean spines, and export at 300 DPI.
```

---

## 4. Final Outcome

The follow-up prompt produced `visualize_temperatures.py`. The resulting chart (`device_temperatures.png`) demonstrates:
- Professional layout with zero label collisions.
- Clear data callouts above each bar (`XX.X°C`).
- Explicit visual context with the 80.0°C filter limit.
- Graceful fallback for empty or corrupt data inputs.
- High-resolution (300 DPI) publication-quality visualization.
