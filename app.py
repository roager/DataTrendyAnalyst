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
    parser.add_argument("--output", default="outputs/bar_race.mp4", help="Output GIF/MP4 path")
    parser.add_argument("--top-n", type=int, default=20, help="Top N categories per frame")
    parser.add_argument("--fps", type=int, default=8, help="Frames per second")
    parser.add_argument("--steps-per-period", type=int, default=48, help="Number of interpolation steps between time periods")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    from datatrendyanalyst.race import RaceConfig, create_bar_race, load_and_prepare_data

    df = load_and_prepare_data(
        input_path=args.input,
        time_col=args.time_col,
        category_col=args.category_col,
        value_col=args.value_col,
        steps_per_period=args.steps_per_period,
    )

    config = RaceConfig(
        time_col=args.time_col,
        category_col=args.category_col,
        value_col=args.value_col,
        title=args.title,
        header_text=args.header,
        top_n=args.top_n,
        fps=args.fps,
        steps_per_period=args.steps_per_period,
    )

    output = create_bar_race(df=df, output_path=Path(args.output), config=config)
    print(f"Animation saved to: {output}")


if __name__ == "__main__":
    main()
