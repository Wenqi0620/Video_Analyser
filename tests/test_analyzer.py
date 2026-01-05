"""Tests for the video analyzer module."""


import numpy as np
import pytest

from video_analyser.analyzer import FrameAnalysis, VideoAnalysisResult, VideoAnalyzer


class TestVideoAnalysisResult:
    """Tests for VideoAnalysisResult dataclass."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = VideoAnalysisResult(
            filepath="/test/video.mp4",
            total_frames=100,
            duration=10.0,
            fps=10.0,
            actual_fps=10.0,
            resolution=(1920, 1080),
        )

        data = result.to_dict()

        assert data["filepath"] == "/test/video.mp4"
        assert data["total_frames"] == 100
        assert data["duration"] == 10.0
        assert data["resolution"] == "1920x1080"

    def test_default_quality_scores(self):
        """Test default quality scores are 100."""
        result = VideoAnalysisResult(
            filepath="/test/video.mp4",
            total_frames=100,
            duration=10.0,
            fps=10.0,
            actual_fps=10.0,
            resolution=(1920, 1080),
        )

        assert result.fps_quality_score == 100.0
        assert result.motion_quality_score == 100.0
        assert result.duplicate_quality_score == 100.0
        assert result.wobble_quality_score == 100.0
        assert result.overall_quality_score == 100.0


class TestVideoAnalyzer:
    """Tests for VideoAnalyzer class."""

    def test_init_default_thresholds(self):
        """Test default threshold values."""
        analyzer = VideoAnalyzer()

        assert analyzer.duplicate_threshold == 0.98
        assert analyzer.motion_threshold == 0.3
        assert analyzer.wobble_threshold == 0.02
        assert analyzer.fps_drop_threshold == 0.8

    def test_init_custom_thresholds(self):
        """Test custom threshold values."""
        analyzer = VideoAnalyzer(
            duplicate_threshold=0.95,
            motion_threshold=0.5,
            wobble_threshold=0.05,
            fps_drop_threshold=0.7,
        )

        assert analyzer.duplicate_threshold == 0.95
        assert analyzer.motion_threshold == 0.5
        assert analyzer.wobble_threshold == 0.05
        assert analyzer.fps_drop_threshold == 0.7

    def test_analyze_file_not_found(self):
        """Test error handling for missing file."""
        analyzer = VideoAnalyzer()

        with pytest.raises(FileNotFoundError):
            analyzer.analyze("/nonexistent/video.mp4")

    def test_calculate_similarity(self):
        """Test frame similarity calculation."""
        analyzer = VideoAnalyzer()

        # Create test frames
        frame1 = np.zeros((100, 100), dtype=np.uint8)
        frame2 = np.zeros((100, 100), dtype=np.uint8)

        # Identical frames should have high similarity
        similarity = analyzer._calculate_similarity(frame1, frame2)
        assert similarity >= 0.99

    def test_calculate_motion(self):
        """Test motion calculation."""
        analyzer = VideoAnalyzer()

        # Create test frames
        frame1 = np.zeros((100, 100), dtype=np.uint8)
        frame2 = np.ones((100, 100), dtype=np.uint8) * 50

        motion = analyzer._calculate_motion(frame1, frame2)
        assert motion == 50.0

    def test_calculate_motion_identical_frames(self):
        """Test motion calculation for identical frames."""
        analyzer = VideoAnalyzer()

        frame = np.zeros((100, 100), dtype=np.uint8)

        motion = analyzer._calculate_motion(frame, frame)
        assert motion == 0.0

    def test_calculate_quality_scores(self):
        """Test quality score calculation."""
        analyzer = VideoAnalyzer()

        result = VideoAnalysisResult(
            filepath="/test/video.mp4",
            total_frames=100,
            duration=10.0,
            fps=10.0,
            actual_fps=10.0,
            resolution=(1920, 1080),
            fps_variance=0.001,
            duplicate_frames=[1, 2, 3, 4, 5],  # 5% duplicates
            motion_discontinuities=[10, 20],  # 2% discontinuities
            wobble_frames=[15],  # 1% wobble
        )

        analyzer._calculate_quality_scores(result)

        # Check that scores are calculated and within bounds
        assert 0 <= result.fps_quality_score <= 100
        assert 0 <= result.duplicate_quality_score <= 100
        assert 0 <= result.motion_quality_score <= 100
        assert 0 <= result.wobble_quality_score <= 100
        assert 0 <= result.overall_quality_score <= 100

    def test_calculate_quality_scores_perfect_video(self):
        """Test quality scores for a perfect video."""
        analyzer = VideoAnalyzer()

        result = VideoAnalysisResult(
            filepath="/test/video.mp4",
            total_frames=100,
            duration=10.0,
            fps=10.0,
            actual_fps=10.0,
            resolution=(1920, 1080),
            fps_variance=0.0,
            duplicate_frames=[],
            motion_discontinuities=[],
            wobble_frames=[],
        )

        analyzer._calculate_quality_scores(result)

        assert result.fps_quality_score == 100.0
        assert result.duplicate_quality_score == 100.0
        assert result.motion_quality_score == 100.0
        assert result.wobble_quality_score == 100.0


class TestFrameAnalysis:
    """Tests for FrameAnalysis dataclass."""

    def test_default_values(self):
        """Test default values."""
        analysis = FrameAnalysis(frame_number=0, timestamp=0.0)

        assert analysis.is_duplicate is False
        assert analysis.duplicate_of is None
        assert analysis.motion_score == 0.0
        assert analysis.wobble_score == 0.0

    def test_custom_values(self):
        """Test custom values."""
        analysis = FrameAnalysis(
            frame_number=10,
            timestamp=1.0,
            is_duplicate=True,
            duplicate_of=9,
            motion_score=25.5,
            wobble_score=0.01,
        )

        assert analysis.frame_number == 10
        assert analysis.timestamp == 1.0
        assert analysis.is_duplicate is True
        assert analysis.duplicate_of == 9
        assert analysis.motion_score == 25.5
        assert analysis.wobble_score == 0.01
