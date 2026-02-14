# DataTrendyAnalyst

A Python app to turn tabular data into animated bar-chart races ("competition" style charts over time).

## Features

- Accepts CSV input with your own columns.
- Visualizes a **Top 20** competition by default to improve comparisons.
- Adds country flags next to country names (when recognized) for faster visual scanning.
- Includes a chart header/subtitle to explain exactly what the animation represents.
- Exports animation as GIF or MP4.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate a demo animation:

```bash
python app.py \
  --input data/world_tourism_sample.csv \
  --time-col year \
  --category-col country \
  --value-col arrivals_millions \
  --title "World Tourism Competition (1980-2025)" \
  --header "Top 20 countries by inbound tourism arrivals (millions)" \
  --output outputs/world_tourism.gif \
  --top-n 20
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

- For `.gif` output, Pillow is used automatically.
- For `.mp4` output, Matplotlib will attempt to use `ffmpeg` if installed.
- Unknown countries fall back to a neutral white-flag emoji (`🏳️`).
