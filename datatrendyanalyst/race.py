from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter


FLAG_BY_COUNTRY: dict[str, str] = {
    "United States": "🇺🇸",
    "France": "🇫🇷",
    "Spain": "🇪🇸",
    "China": "🇨🇳",
    "Italy": "🇮🇹",
    "Turkey": "🇹🇷",
    "Mexico": "🇲🇽",
    "Thailand": "🇹🇭",
    "Germany": "🇩🇪",
    "United Kingdom": "🇬🇧",
    "Japan": "🇯🇵",
    "Greece": "🇬🇷",
    "Austria": "🇦🇹",
    "Malaysia": "🇲🇾",
    "Portugal": "🇵🇹",
    "Russia": "🇷🇺",
    "Canada": "🇨🇦",
    "Vietnam": "🇻🇳",
    "Netherlands": "🇳🇱",
    "Saudi Arabia": "🇸🇦",
}


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


def load_and_prepare_data(
    input_path: str | Path,
    time_col: str,
    category_col: str,
    value_col: str,
) -> pd.DataFrame:
    """Load CSV and validate required columns."""
    df = pd.read_csv(input_path)

    missing = {time_col, category_col, value_col} - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df[[time_col, category_col, value_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[time_col, category_col, value_col])

    # Stable ordering for animation consistency
    df = df.sort_values([time_col, value_col, category_col], ascending=[True, False, True])
    return df


def _label_with_flag(country_name: str) -> str:
    flag = FLAG_BY_COUNTRY.get(country_name, "🏳️")
    return f"{flag} {country_name}"


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
        frame["display_label"] = frame[config.category_col].astype(str).map(_label_with_flag)

        bars = ax.barh(
            frame["display_label"],
            frame[config.value_col],
            color=[color_map[c] for c in frame[config.category_col]],
        )

        ax.set_title(f"{config.title}\n{config.time_col.capitalize()}: {current_time}", pad=18)
        ax.set_xlabel(config.value_col.replace("_", " ").title())
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        max_value = float(df[config.value_col].max())
        ax.set_xlim(0, max_value * 1.15 if max_value > 0 else 1)

        for bar in bars:
            value = bar.get_width()
            y = bar.get_y() + bar.get_height() / 2
            ax.text(value, y, f" {value:,.2f}", va="center", fontsize=8)

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
