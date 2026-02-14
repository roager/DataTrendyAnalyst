# DataTrendyAnalyst

A Python app to turn tabular data into animated bar-chart races ("competition" style charts over time).

## Features

- Accepts CSV input with your own columns.
- Visualizes a **Top 20** competition by default to improve comparisons.
- Adds country flags next to country names (when recognized) for faster visual scanning.
- Includes a chart header/subtitle to explain exactly what the animation represents.
- Uses smooth interpolation between years so values and bars grow/shrink fluidly.
- Exports animation as **MP4** (recommended) or GIF.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate a publish-ready MP4 (recommended):

```bash
python app.py \
  --input data/world_tourism_sample.csv \
  --time-col year \
  --category-col country \
  --value-col arrivals_millions \
  --title "World Tourism Competition (1980-2025)" \
  --header "Top 20 countries by inbound tourism arrivals (millions)" \
  --output outputs/world_tourism.mp4 \
  --top-n 20 \
  --fps 24 \
  --steps-per-year 16 \
  --year-hold-seconds 0.5
```

## Expected CSV format

The app expects at least three columns:

- `time` column (e.g., `year`)
- `category` column (e.g., `country`)
- `value` column (numeric, e.g., `arrivals_millions`)

Example:

| year | country       | arrivals_millions |
|------|---------------|-------------------|
| 1980 | Spain         | 23.4              |
| 1980 | France        | 30.1              |
| ...  | ...           | ...               |

## Notes

- MP4 rendering uses `ffmpeg` via Matplotlib writer (`libx264`).
- For `.gif` output, Pillow is used automatically, but emoji/flag rendering can vary by environment.
- Unknown countries fall back to a neutral white-flag emoji (`🏳️`).
