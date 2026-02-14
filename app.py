from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create animated bar-chart race visualizations from CSV data."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--time-col", required=True, help="Column name representing time")
    parser.add_argument("--category-col", required=True, help="Column name for category labels")
    parser.add_argument("--value-col", required=True, help="Numeric column used for ranking")
    parser.add_argument("--title", default="World Tourism Competition", help="Chart title")
    parser.add_argument(
        "--header",
        default="Top 20 countries by inbound tourism arrivals (millions)",
        help="Header text describing what the visualization represents",
    )
    parser.add_argument("--output", default="outputs/bar_race.mp4", help="Output MP4/GIF path")
    parser.add_argument("--top-n", type=int, default=20, help="Top N categories per frame")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second")
    parser.add_argument(
        "--steps-per-year",
        type=int,
        default=16,
        help="Interpolated frames between each pair of years",
    )
    parser.add_argument(
        "--year-hold-seconds",
        type=float,
        default=0.5,
        help="Pause duration (seconds) on each real year before transitioning",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    from datatrendyanalyst.race import RaceConfig, create_bar_race, load_and_prepare_data

    df = load_and_prepare_data(
        input_path=args.input,
        time_col=args.time_col,
        category_col=args.category_col,
        value_col=args.value_col,
    )

    config = RaceConfig(
        time_col=args.time_col,
        category_col=args.category_col,
        value_col=args.value_col,
        title=args.title,
        header_text=args.header,
        top_n=args.top_n,
        fps=args.fps,
        steps_per_year=max(1, args.steps_per_year),
        year_hold_seconds=max(0.0, args.year_hold_seconds),
    )

    output = create_bar_race(df=df, output_path=Path(args.output), config=config)
    print(f"Animation saved to: {output}")


if __name__ == "__main__":
    main()
