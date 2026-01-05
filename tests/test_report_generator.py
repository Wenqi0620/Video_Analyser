"""Tests for the report generator module."""

import json
import tempfile
from pathlib import Path

import pytest

from video_analyser.analyzer import VideoAnalysisResult
from video_analyser.report_generator import ReportGenerator


def create_test_result(filepath: str = "/test/video.mp4") -> VideoAnalysisResult:
    """Create a test VideoAnalysisResult."""
    return VideoAnalysisResult(
        filepath=filepath,
        total_frames=100,
        duration=10.0,
        fps=10.0,
        actual_fps=10.0,
        resolution=(1920, 1080),
        fps_variance=0.001,
        duplicate_frames=[1, 2, 3],
        motion_discontinuities=[10],
        wobble_frames=[15, 20],
        fps_quality_score=95.0,
        motion_quality_score=90.0,
        duplicate_quality_score=94.0,
        wobble_quality_score=90.0,
        overall_quality_score=92.0,
    )


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_init_default_output_dir(self):
        """Test default output directory."""
        generator = ReportGenerator()
        assert generator.output_dir == Path.cwd()

    def test_init_custom_output_dir(self):
        """Test custom output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            assert generator.output_dir == Path(tmpdir)

    def test_init_creates_output_dir(self):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_dir"
            ReportGenerator(output_dir=new_dir)
            assert new_dir.exists()

    def test_generate_csv(self):
        """Test CSV report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [create_test_result()]

            filepath = generator.generate_csv(results, "test_report.csv")

            assert filepath.exists()
            assert filepath.suffix == ".csv"

            content = filepath.read_text()
            assert "filepath" in content
            assert "overall_quality_score" in content

    def test_generate_csv_empty_results(self):
        """Test CSV generation with empty results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)

            filepath = generator.generate_csv([], "empty.csv")

            assert filepath.exists()

    def test_generate_csv_auto_filename(self):
        """Test CSV generation with auto-generated filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [create_test_result()]

            filepath = generator.generate_csv(results)

            assert filepath.exists()
            assert "video_analysis_" in filepath.name

    def test_generate_json(self):
        """Test JSON report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [create_test_result()]

            filepath = generator.generate_json(results, "test_report.json")

            assert filepath.exists()

            with open(filepath) as f:
                data = json.load(f)

            assert "generated_at" in data
            assert "total_videos" in data
            assert data["total_videos"] == 1
            assert "results" in data

    def test_generate_json_structure(self):
        """Test JSON report structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [
                create_test_result("/test/video1.mp4"),
                create_test_result("/test/video2.mp4"),
            ]

            filepath = generator.generate_json(results, "test.json")

            with open(filepath) as f:
                data = json.load(f)

            assert data["total_videos"] == 2
            assert len(data["results"]) == 2

    def test_generate_html(self):
        """Test HTML report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [create_test_result()]

            filepath = generator.generate_html(results, "test_report.html")

            assert filepath.exists()

            content = filepath.read_text()
            assert "<!DOCTYPE html>" in content
            assert "Video Analysis Report" in content

    def test_generate_html_contains_results(self):
        """Test HTML report contains results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [create_test_result("/test/my_video.mp4")]

            filepath = generator.generate_html(results)
            content = filepath.read_text()

            assert "my_video.mp4" in content
            assert "92" in content  # overall quality score

    def test_generate_excel(self):
        """Test Excel report generation."""
        pytest.importorskip("openpyxl")

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [create_test_result()]

            filepath = generator.generate_excel(results, "test_report.xlsx")

            assert filepath.exists()
            assert filepath.suffix == ".xlsx"

    def test_generate_excel_sheets(self):
        """Test Excel report has expected sheets."""
        openpyxl = pytest.importorskip("openpyxl")

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [create_test_result()]

            filepath = generator.generate_excel(results)

            wb = openpyxl.load_workbook(filepath)
            sheet_names = wb.sheetnames

            assert "Summary" in sheet_names
            assert "Detailed Results" in sheet_names
            assert "Quality Scores" in sheet_names

    def test_multiple_results(self):
        """Test report generation with multiple results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ReportGenerator(output_dir=tmpdir)
            results = [
                create_test_result("/test/video1.mp4"),
                create_test_result("/test/video2.mp4"),
                create_test_result("/test/video3.mp4"),
            ]

            csv_path = generator.generate_csv(results, "multi.csv")
            json_path = generator.generate_json(results, "multi.json")
            html_path = generator.generate_html(results, "multi.html")

            assert csv_path.exists()
            assert json_path.exists()
            assert html_path.exists()

            # Verify CSV has all rows
            lines = csv_path.read_text().strip().split("\n")
            assert len(lines) == 4  # header + 3 results
