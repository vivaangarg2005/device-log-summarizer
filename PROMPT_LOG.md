# AI Prompting Log (Section 3)

This document covers the AI interaction for building the Section 3 charting script (`visualize_temperatures.py`), the issues identified in the initial output, and the follow-up prompt used to resolve them.

---

### 1. Initial Prompt to the AI

```text
Write a Python script that loads the JSON output ('summary_output.json') generated from Section 2 
and creates a bar chart comparing the average temperature per device using matplotlib. 
Save the generated chart as 'device_temperatures.png'.
```

#### Initial Code Returned by AI:
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

### 2. Bugs & Formatting Mistakes in First Attempt

When I ran and reviewed the generated script, I identified the following issues:

1. **Overlapping X-Axis Labels & Clipping:**  
   The labels were rendered horizontally with no rotation or margin adjustments. When device names are long or several devices are present, the labels collide, and without `plt.tight_layout()`, the bottom labels get cut off.

2. **Missing Value Annotations:**  
   There were no temperature values displayed on top of the bars, making it difficult to read the exact values without looking at the raw JSON.

3. **Missing Threshold Indicator:**  
   The assessment specifies an 80.0°C filter cutoff in Section 2, but the chart did not provide visual context showing where the devices sit relative to that threshold.

4. **Missing Error Handling & Headless Support:**  
   The script assumes the JSON file exists and contains items. If the file is missing or empty, it throws an unhandled exception. It also relied on the default Tkinter backend, which causes issues when run in headless or automated environments.

---

### 3. Follow-up Prompt Used to Fix the Issues

```text
The initial script works for a basic plot, but has a few layout and robustness issues:
1. Rotate the x-axis tick labels slightly and add plt.tight_layout() to prevent label overlap or clipping.
2. Add exact temperature values directly above each bar (e.g., '68.5°C').
3. Add a dashed red reference line at y = 80.0°C indicating the max filter threshold.
4. Set matplotlib backend to 'Agg' before importing pyplot so it runs cleanly in headless environments.
5. Add basic error handling for missing or empty JSON files, and save the figure at 300 DPI with subtle horizontal gridlines.
```

---

### 4. Outcome

The resulting code in `visualize_temperatures.py` generates `device_temperatures.png` with proper label rotation, clear bar callouts, an 80.0°C threshold line, and headless execution support.
