"""
Batch processing module for analyzing multiple videos.
"""

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .analyzer import VideoAnalysisResult, VideoAnalyzer

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Batch processor for analyzing multiple videos.

    Supports parallel processing and progress callbacks.
    """

    SUPPORTED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}

    def __init__(
        self,
        analyzer: VideoAnalyzer | None = None,
        max_workers: int = 4,
    ):
        """
        Initialize the batch processor.

        Args:
            analyzer: VideoAnalyzer instance to use. Creates default if None.
            max_workers: Maximum number of parallel workers.
        """
        self.analyzer = analyzer or VideoAnalyzer()
        self.max_workers = max_workers

    def process_directory(
        self,
        directory: str | Path,
        recursive: bool = True,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> list[VideoAnalysisResult]:
        """
        Process all videos in a directory.

        Args:
            directory: Path to directory containing videos.
            recursive: Whether to search subdirectories.
            progress_callback: Optional callback(current, total, filename).

        Returns:
            List of VideoAnalysisResult objects.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Find all video files
        video_files = self._find_videos(directory, recursive)

        if not video_files:
            logger.warning(f"No video files found in {directory}")
            return []

        return self.process_files(video_files, progress_callback)

    def process_files(
        self,
        files: list[str | Path],
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> list[VideoAnalysisResult]:
        """
        Process a list of video files.

        Args:
            files: List of video file paths.
            progress_callback: Optional callback(current, total, filename).

        Returns:
            List of VideoAnalysisResult objects.
        """
        results = []
        total = len(files)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._analyze_file, f): f
                for f in files
            }

            completed = 0
            for future in as_completed(future_to_file):
                filepath = future_to_file[future]
                completed += 1

                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Analyzed: {filepath}")
                except Exception as e:
                    logger.error(f"Error analyzing {filepath}: {e}")

                if progress_callback:
                    progress_callback(completed, total, str(filepath))

        return results

    def _find_videos(self, directory: Path, recursive: bool) -> list[Path]:
        """Find all video files in a directory."""
        pattern = "**/*" if recursive else "*"
        video_files = []

        for ext in self.SUPPORTED_EXTENSIONS:
            video_files.extend(directory.glob(f"{pattern}{ext}"))
            video_files.extend(directory.glob(f"{pattern}{ext.upper()}"))

        return sorted(video_files)

    def _analyze_file(self, filepath: str | Path) -> VideoAnalysisResult:
        """Analyze a single video file."""
        return self.analyzer.analyze(filepath)
