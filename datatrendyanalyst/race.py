from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter


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
    fps: int = 24
    fig_width: int = 13
    fig_height: int = 8
    steps_per_year: int = 16
    year_hold_seconds: float = 0.5


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


def _smoothstep(t: float) -> float:
    """Ease in/out interpolation in [0, 1]."""
    return t * t * (3 - 2 * t)


def _build_frame_data(df: pd.DataFrame, config: RaceConfig) -> list[tuple[float, pd.Series]]:
    """Build interpolated frames with optional hold at each real year."""
    times = list(pd.unique(df[config.time_col]))
    if not times:
        return []

    pivot = (
        df.pivot_table(
            index=config.category_col,
            columns=config.time_col,
            values=config.value_col,
            aggfunc="sum",
        )
        .sort_index()
        .fillna(0.0)
    )

    frame_data: list[tuple[float, pd.Series]] = []
    hold_frames = max(0, int(round(config.year_hold_seconds * config.fps)))

    for idx, current_time in enumerate(times):
        current_series = pivot[current_time].astype(float)

        # Hold real year frame so user can read ranking changes.
        for _ in range(hold_frames):
            frame_data.append((float(current_time), current_series.copy()))

        if idx == len(times) - 1:
            continue

        next_time = times[idx + 1]
        next_series = pivot[next_time].astype(float)

        for step in range(1, max(1, config.steps_per_year) + 1):
            t_linear = step / (max(1, config.steps_per_year) + 1)
            t_eased = _smoothstep(t_linear)
            interp = current_series + (next_series - current_series) * t_eased
            interp_time = float(current_time) + (float(next_time) - float(current_time)) * t_linear
            frame_data.append((interp_time, interp))

    # Ensure last year appears even if hold is 0.
    if hold_frames == 0:
        last_time = times[-1]
        frame_data.append((float(last_time), pivot[last_time].astype(float).copy()))

    return frame_data


def create_bar_race(
    df: pd.DataFrame,
    output_path: str | Path,
    config: RaceConfig,
) -> Path:
    """Create and save bar race animation from prepared/interpolated data."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frame_data = _build_frame_data(df, config)
    if not frame_data:
        raise ValueError("No time periods found after cleaning data.")

    fig, ax = plt.subplots(figsize=(config.fig_width, config.fig_height))
    cmap = plt.cm.get_cmap("tab20")

    categories = sorted(df[config.category_col].unique())
    color_map = {cat: cmap(i % 20) for i, cat in enumerate(categories)}
    max_value = float(df[config.value_col].max())

    def draw_frame(frame_index: int) -> None:
        ax.clear()
        interp_time, frame_series = frame_data[frame_index]

        frame = (
            frame_series.rename(config.value_col)
            .reset_index()
            .rename(columns={"index": config.category_col})
        )

        frame = frame.nlargest(config.top_n, config.value_col)
        frame = frame.sort_values(config.value_col, ascending=True)
        frame["display_label"] = frame[config.category_col].astype(str).map(_label_with_flag)

        bars = ax.barh(
            frame["display_label"],
            frame[config.value_col],
            color=[color_map.get(c, "gray") for c in frame[config.category_col]],
        )

        year_text = f"{interp_time:.1f}" if not float(interp_time).is_integer() else str(int(interp_time))
        ax.set_title(f"{config.title}\n{config.time_col.capitalize()}: {year_text}", pad=18)
        ax.set_xlabel(config.value_col.replace("_", " ").title())
        ax.grid(axis="x", linestyle="--", alpha=0.3)
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
        frames=len(frame_data),
        interval=1000 / config.fps,
        repeat=False,
    )

    if output_path.suffix.lower() == ".gif":
        writer = PillowWriter(fps=config.fps)
        anim.save(output_path, writer=writer)
    else:
        writer = FFMpegWriter(fps=config.fps, codec="libx264", bitrate=3000)
        anim.save(output_path, writer=writer)

    plt.close(fig)
    return output_path
