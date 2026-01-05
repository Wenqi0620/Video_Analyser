"""Tests for the batch processor module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from video_analyser.analyzer import VideoAnalysisResult, VideoAnalyzer
from video_analyser.batch_processor import BatchProcessor


class TestBatchProcessor:
    """Tests for BatchProcessor class."""

    def test_init_default_values(self):
        """Test default initialization."""
        processor = BatchProcessor()

        assert processor.analyzer is not None
        assert processor.max_workers == 4

    def test_init_custom_values(self):
        """Test custom initialization."""
        analyzer = VideoAnalyzer(duplicate_threshold=0.95)
        processor = BatchProcessor(analyzer=analyzer, max_workers=8)

        assert processor.analyzer == analyzer
        assert processor.max_workers == 8

    def test_supported_extensions(self):
        """Test supported video extensions."""
        expected = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}
        assert BatchProcessor.SUPPORTED_EXTENSIONS == expected

    def test_process_directory_not_found(self):
        """Test error handling for missing directory."""
        processor = BatchProcessor()

        with pytest.raises(FileNotFoundError):
            processor.process_directory("/nonexistent/directory")

    def test_find_videos_empty_directory(self):
        """Test finding videos in empty directory."""
        processor = BatchProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            videos = processor._find_videos(Path(tmpdir), recursive=True)
            assert videos == []

    def test_find_videos_with_files(self):
        """Test finding video files."""
        processor = BatchProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test files
            (tmpdir / "video1.mp4").touch()
            (tmpdir / "video2.avi").touch()
            (tmpdir / "document.txt").touch()
            (tmpdir / "image.jpg").touch()

            videos = processor._find_videos(tmpdir, recursive=False)

            assert len(videos) == 2
            assert all(v.suffix.lower() in BatchProcessor.SUPPORTED_EXTENSIONS for v in videos)

    def test_find_videos_recursive(self):
        """Test recursive video finding."""
        processor = BatchProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create nested structure
            subdir = tmpdir / "subdir"
            subdir.mkdir()

            (tmpdir / "video1.mp4").touch()
            (subdir / "video2.mp4").touch()

            # Non-recursive should find only root video
            videos = processor._find_videos(tmpdir, recursive=False)
            assert len(videos) == 1

            # Recursive should find both
            videos = processor._find_videos(tmpdir, recursive=True)
            assert len(videos) == 2

    def test_process_files_empty_list(self):
        """Test processing empty file list."""
        processor = BatchProcessor()

        results = processor.process_files([])
        assert results == []

    def test_progress_callback(self):
        """Test progress callback is called."""
        processor = BatchProcessor()
        callback_calls = []

        def callback(current, total, filename):
            callback_calls.append((current, total, filename))

        # Mock the analyzer
        mock_result = VideoAnalysisResult(
            filepath="test.mp4",
            total_frames=100,
            duration=10.0,
            fps=10.0,
            actual_fps=10.0,
            resolution=(1920, 1080),
        )

        with patch.object(processor.analyzer, 'analyze', return_value=mock_result):
            with tempfile.TemporaryDirectory() as tmpdir:
                test_file = Path(tmpdir) / "test.mp4"
                test_file.touch()

                processor.process_files([test_file], progress_callback=callback)

        assert len(callback_calls) == 1
        assert callback_calls[0][0] == 1
        assert callback_calls[0][1] == 1

    def test_process_directory_empty(self):
        """Test processing empty directory."""
        processor = BatchProcessor()

        with tempfile.TemporaryDirectory() as tmpdir:
            results = processor.process_directory(tmpdir)
            assert results == []
