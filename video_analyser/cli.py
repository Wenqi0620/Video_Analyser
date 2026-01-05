"""
Command-line interface for Video Analyser.
"""

import argparse
import logging
import sys
from pathlib import Path

from .analyzer import VideoAnalyzer
from .batch_processor import BatchProcessor
from .report_generator import ReportGenerator


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def progress_callback(current: int, total: int, filename: str) -> None:
    """Print progress updates."""
    print(f"[{current}/{total}] Analyzed: {Path(filename).name}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="video-analyser",
        description="Comprehensive video quality analyzer for AI-generated videos.",
    )

    parser.add_argument(
        "input",
        type=str,
        help="Video file or directory to analyze",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=".",
        help="Output directory for reports (default: current directory)",
    )

    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["excel", "csv", "json", "html", "all"],
        default="excel",
        help="Output format (default: excel)",
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Search directories recursively",
    )

    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )

    parser.add_argument(
        "--duplicate-threshold",
        type=float,
        default=0.98,
        help="Similarity threshold for duplicate detection (0-1, default: 0.98)",
    )

    parser.add_argument(
        "--motion-threshold",
        type=float,
        default=0.3,
        help="Threshold for motion discontinuity detection (default: 0.3)",
    )

    parser.add_argument(
        "--wobble-threshold",
        type=float,
        default=0.02,
        help="Threshold for wobble detection (default: 0.02)",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    # Create analyzer with custom thresholds
    analyzer = VideoAnalyzer(
        duplicate_threshold=args.duplicate_threshold,
        motion_threshold=args.motion_threshold,
        wobble_threshold=args.wobble_threshold,
    )

    # Process input
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
        return 1

    print("🎬 Video Analyser v1.0.0")
    print(f"{'=' * 40}")

    if input_path.is_file():
        print(f"Analyzing single file: {input_path.name}")
        try:
            result = analyzer.analyze(input_path)
            results = [result]
        except Exception as e:
            print(f"Error analyzing {input_path}: {e}", file=sys.stderr)
            return 1
    else:
        print(f"Analyzing directory: {input_path}")
        print(f"Recursive: {args.recursive}")
        print(f"Workers: {args.workers}")
        print()

        processor = BatchProcessor(analyzer=analyzer, max_workers=args.workers)
        results = processor.process_directory(
            input_path,
            recursive=args.recursive,
            progress_callback=progress_callback,
        )

    if not results:
        print("No videos found or analyzed.")
        return 0

    # Generate reports
    print()
    print("Generating reports...")

    report_gen = ReportGenerator(output_dir=args.output)
    formats = ["excel", "csv", "json", "html"] if args.format == "all" else [args.format]

    for fmt in formats:
        try:
            if fmt == "excel":
                path = report_gen.generate_excel(results)
            elif fmt == "csv":
                path = report_gen.generate_csv(results)
            elif fmt == "json":
                path = report_gen.generate_json(results)
            elif fmt == "html":
                path = report_gen.generate_html(results)
            print(f"  ✓ Generated: {path}")
        except Exception as e:
            print(f"  ✗ Failed to generate {fmt}: {e}", file=sys.stderr)

    # Print summary
    print()
    print(f"{'=' * 40}")
    print("Summary")
    print(f"{'=' * 40}")
    print(f"Videos analyzed: {len(results)}")

    avg_quality = sum(r.overall_quality_score for r in results) / len(results)
    print(f"Average quality score: {avg_quality:.1f}/100")

    total_duplicates = sum(len(r.duplicate_frames) for r in results)
    total_motion_issues = sum(len(r.motion_discontinuities) for r in results)
    total_wobble_issues = sum(len(r.wobble_frames) for r in results)

    print(f"Total duplicate frames: {total_duplicates}")
    print(f"Total motion discontinuities: {total_motion_issues}")
    print(f"Total wobble issues: {total_wobble_issues}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
