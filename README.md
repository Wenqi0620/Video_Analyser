# Video Analyser

[![CI](https://github.com/Wenqi0620/Video_Analyser/actions/workflows/ci.yml/badge.svg)](https://github.com/Wenqi0620/Video_Analyser/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Comprehensive video quality analyzer for AI-generated videos. Analyzes FPS dynamics, motion continuity, duplicate frames, and wobble distortion with batch processing and detailed reports.

## Features

- **FPS Analysis**: Detects frame rate variance and FPS drops
- **Duplicate Frame Detection**: Identifies frozen/duplicate frames common in AI-generated videos
- **Motion Continuity Analysis**: Detects motion discontinuities and sudden jumps
- **Wobble/Jitter Detection**: Identifies camera wobble and jitter artifacts
- **Batch Processing**: Analyze entire directories of videos in parallel
- **Multiple Report Formats**: Excel, CSV, JSON, and HTML reports
- **Quality Scoring**: 0-100 quality scores for each metric and overall quality

## Installation

```bash
# From PyPI (when published)
pip install video-analyser

# From source
git clone https://github.com/Wenqi0620/Video_Analyser.git
cd Video_Analyser
pip install -e .
```

### Requirements

- Python 3.10+
- OpenCV
- NumPy
- openpyxl (for Excel reports)

## Quick Start

### Command Line

```bash
# Analyze a single video
video-analyser video.mp4

# Analyze a directory of videos
video-analyser ./videos -r

# Generate all report formats
video-analyser ./videos -f all -o ./reports

# Customize detection thresholds
video-analyser video.mp4 --duplicate-threshold 0.95 --wobble-threshold 0.03
```

### Python API

```python
from video_analyser import VideoAnalyzer, BatchProcessor, ReportGenerator

# Analyze a single video
analyzer = VideoAnalyzer()
result = analyzer.analyze("video.mp4")

print(f"Quality Score: {result.overall_quality_score:.1f}/100")
print(f"Duplicate Frames: {len(result.duplicate_frames)}")
print(f"Motion Issues: {len(result.motion_discontinuities)}")
print(f"Wobble Issues: {len(result.wobble_frames)}")

# Batch process a directory
processor = BatchProcessor(analyzer=analyzer, max_workers=4)
results = processor.process_directory("./videos", recursive=True)

# Generate reports
report_gen = ReportGenerator(output_dir="./reports")
report_gen.generate_excel(results)
report_gen.generate_html(results)
```

## Analysis Metrics

### FPS Quality
Measures consistency of frame timing. Detects:
- Frame rate variance
- FPS drops below expected rate

### Duplicate Frame Detection
Uses structural similarity to detect:
- Frozen frames
- Repeated frames
- Near-identical consecutive frames

### Motion Continuity
Analyzes frame-to-frame motion to detect:
- Sudden motion jumps
- Motion discontinuities
- Unnatural motion patterns

### Wobble Detection
Uses optical flow analysis to detect:
- Camera shake/jitter
- Unstable footage
- Wobble artifacts

## Quality Scores

Each video receives scores from 0-100 (higher is better):

| Score | Quality |
|-------|---------|
| 80-100 | Excellent |
| 60-79 | Good |
| 40-59 | Fair |
| 0-39 | Poor |

## CLI Options

```
usage: video-analyser [-h] [-o OUTPUT] [-f FORMAT] [-r] [-w WORKERS]
                      [--duplicate-threshold DUPLICATE_THRESHOLD]
                      [--motion-threshold MOTION_THRESHOLD]
                      [--wobble-threshold WOBBLE_THRESHOLD]
                      [-v] [--version]
                      input

positional arguments:
  input                 Video file or directory to analyze

options:
  -h, --help            Show help message
  -o, --output OUTPUT   Output directory for reports (default: .)
  -f, --format FORMAT   Output format: excel, csv, json, html, all (default: excel)
  -r, --recursive       Search directories recursively
  -w, --workers WORKERS Number of parallel workers (default: 4)
  --duplicate-threshold Similarity threshold for duplicate detection (0-1)
  --motion-threshold    Threshold for motion discontinuity detection
  --wobble-threshold    Threshold for wobble detection
  -v, --verbose         Enable verbose output
  --version             Show version
```

## Report Formats

### Excel (.xlsx)
- **Summary sheet**: Overall statistics and averages
- **Detailed Results**: All metrics for each video
- **Quality Scores**: Color-coded quality scores

### CSV
Flat table format suitable for data analysis tools.

### JSON
Structured format with full metadata and results.

### HTML
Interactive report with visual styling and color-coded quality indicators.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter
ruff check .

# Run type checker
mypy video_analyser
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenCV for video processing
- NumPy for numerical operations
- openpyxl for Excel report generation
