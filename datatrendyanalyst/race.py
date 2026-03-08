from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import urllib.request
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.animation import FuncAnimation, PillowWriter


FLAG_BY_COUNTRY: dict[str, str] = {
    "United States": "us",
    "France": "fr",
    "Spain": "es",
    "China": "cn",
    "Italy": "it",
    "Turkey": "tr",
    "Mexico": "mx",
    "Thailand": "th",
    "Germany": "de",
    "United Kingdom": "gb",
    "Japan": "jp",
    "Greece": "gr",
    "Austria": "at",
    "Malaysia": "my",
    "Portugal": "pt",
    "Russia": "ru",
    "Canada": "ca",
    "Vietnam": "vn",
    "Netherlands": "nl",
    "Saudi Arabia": "sa",
}

def get_flag_image(country_name: str):
    code = FLAG_BY_COUNTRY.get(country_name)
    if not code:
        return None

    flags_dir = Path("flags")
    flags_dir.mkdir(exist_ok=True)
    flag_path = flags_dir / f"{code}.png"

    if not flag_path.exists():
        url = f"https://flagcdn.com/w40/{code}.png"
        try:
            urllib.request.urlretrieve(url, flag_path)
        except Exception as e:
            print(f"Failed to download flag for {country_name}: {e}")
            return None

    try:
        return plt.imread(flag_path)
    except Exception:
        return None


@dataclass
class RaceConfig:
    time_col: str
    category_col: str
    value_col: str
    title: str
    header_text: str
    top_n: int = 20
    fps: int = 8
    fig_width: int = 13
    fig_height: int = 8
    steps_per_period: int = 48


def interpolate_data(
    df: pd.DataFrame,
    time_col: str,
    category_col: str,
    value_col: str,
    steps_per_period: int,
) -> pd.DataFrame:
    """Interpolate data between time periods for smoother animation."""
    if steps_per_period <= 1:
        return df

    # Ensure numeric for interpolation
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    # Pivot so each category is a column
    df_pivot = df.pivot(index=time_col, columns=category_col, values=value_col)

    orig_idx = df_pivot.index.tolist()
    new_idx = []
    for i in range(len(orig_idx) - 1):
        new_idx.extend(np.linspace(orig_idx[i], orig_idx[i + 1], steps_per_period, endpoint=False))
    new_idx.append(orig_idx[-1])

    # Reindex and interpolate
    df_pivot = df_pivot.reindex(pd.Index(new_idx, name=time_col)).interpolate(method="linear")

    # Melt back to long format
    df_melt = df_pivot.reset_index().melt(
        id_vars=time_col,
        var_name=category_col,
        value_name=value_col
    )

    # Drop rows where values might be NaN (e.g., if a category didn't exist early on)
    df_melt = df_melt.dropna(subset=[value_col])

    # Sort nicely again
    df_melt = df_melt.sort_values([time_col, value_col, category_col], ascending=[True, False, True])
    return df_melt


def load_and_prepare_data(
    input_path: str | Path,
    time_col: str,
    category_col: str,
    value_col: str,
    steps_per_period: int = 48,
) -> pd.DataFrame:
    """Load CSV and validate required columns."""
    df = pd.read_csv(input_path)

    missing = {time_col, category_col, value_col} - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df[[time_col, category_col, value_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[time_col, category_col, value_col])

    # Interpolate data for smoother animation
    df = interpolate_data(df, time_col, category_col, value_col, steps_per_period)

    # Stable ordering for animation consistency
    df = df.sort_values([time_col, value_col, category_col], ascending=[True, False, True])
    return df


def create_bar_race(
    df: pd.DataFrame,
    output_path: str | Path,
    config: RaceConfig,
) -> Path:
    """Create and save bar race animation from prepared data."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    times = list(pd.unique(df[config.time_col]))
    if not times:
        raise ValueError("No time periods found after cleaning data.")

    fig, ax = plt.subplots(figsize=(config.fig_width, config.fig_height))
    cmap = plt.cm.get_cmap("tab20")

    categories = sorted(df[config.category_col].unique())
    color_map = {cat: cmap(i % 20) for i, cat in enumerate(categories)}

    def draw_frame(frame_index: int) -> None:
        ax.clear()
        current_time = times[frame_index]
        frame = df[df[config.time_col] == current_time].copy()

        frame = frame.nlargest(config.top_n, config.value_col)
        frame = frame.sort_values(config.value_col, ascending=True)
        frame["display_label"] = frame[config.category_col].astype(str)

        bars = ax.barh(
            frame["display_label"],
            frame[config.value_col],
            color=[color_map[c] for c in frame[config.category_col]],
        )

        # Format current_time to avoid 1980.5 display if possible
        display_time = int(current_time) if current_time == int(current_time) else round(current_time, 1)
        ax.set_title(f"{config.title}\n{config.time_col.capitalize()}: {display_time}", pad=18)
        ax.set_xlabel(config.value_col.replace("_", " ").title())
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        max_value = float(df[config.value_col].max())
        ax.set_xlim(0, max_value * 1.15 if max_value > 0 else 1)

        for i, (bar, category_name) in enumerate(zip(bars, frame[config.category_col])):
            value = bar.get_width()
            y = bar.get_y() + bar.get_height() / 2
            ax.text(value, y, f" {value:,.2f}", va="center", fontsize=8)

            img = get_flag_image(category_name)
            if img is not None:
                imagebox = OffsetImage(img, zoom=0.6)
                # Align the image slightly to the left of the y-axis
                ab = AnnotationBbox(imagebox, (0, y), frameon=False, box_alignment=(1.2, 0.5))
                ax.add_artist(ab)

        fig.text(
            0.5,
            0.97,
            config.header_text,
            ha="center",
            va="top",
            fontsize=11,
            color="dimgray",
        )
        plt.tight_layout(rect=[0, 0, 1, 0.95])

    anim = FuncAnimation(
        fig,
        draw_frame,
        frames=len(times),
        interval=1000 / config.fps,
        repeat=False,
    )

    if output_path.suffix.lower() == ".gif":
        writer = PillowWriter(fps=config.fps)
        anim.save(output_path, writer=writer)
    else:
        # Let matplotlib choose default writer (commonly ffmpeg for mp4)
        anim.save(output_path, fps=config.fps)

    plt.close(fig)
    return output_path
