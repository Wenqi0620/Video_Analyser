"""
Core video analysis module for detecting quality issues in AI-generated videos.
"""

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np


@dataclass
class FrameAnalysis:
    """Analysis results for a single frame."""
    frame_number: int
    timestamp: float
    is_duplicate: bool = False
    duplicate_of: int | None = None
    motion_score: float = 0.0
    wobble_score: float = 0.0


@dataclass
class VideoAnalysisResult:
    """Complete analysis results for a video."""
    filepath: str
    total_frames: int
    duration: float
    fps: float
    actual_fps: float
    resolution: tuple[int, int]

    # FPS Analysis
    fps_variance: float = 0.0
    fps_drops: list[dict] = field(default_factory=list)

    # Duplicate Frame Analysis
    duplicate_frames: list[int] = field(default_factory=list)
    duplicate_percentage: float = 0.0

    # Motion Analysis
    motion_scores: list[float] = field(default_factory=list)
    motion_discontinuities: list[int] = field(default_factory=list)
    avg_motion_score: float = 0.0

    # Wobble Analysis
    wobble_scores: list[float] = field(default_factory=list)
    wobble_frames: list[int] = field(default_factory=list)
    avg_wobble_score: float = 0.0

    # Quality Scores (0-100, higher is better)
    fps_quality_score: float = 100.0
    motion_quality_score: float = 100.0
    duplicate_quality_score: float = 100.0
    wobble_quality_score: float = 100.0
    overall_quality_score: float = 100.0

    def to_dict(self) -> dict:
        """Convert results to dictionary for serialization."""
        return {
            "filepath": self.filepath,
            "total_frames": self.total_frames,
            "duration": round(self.duration, 2),
            "fps": round(self.fps, 2),
            "actual_fps": round(self.actual_fps, 2),
            "resolution": f"{self.resolution[0]}x{self.resolution[1]}",
            "fps_variance": round(self.fps_variance, 4),
            "fps_drops_count": len(self.fps_drops),
            "duplicate_frames_count": len(self.duplicate_frames),
            "duplicate_percentage": round(self.duplicate_percentage, 2),
            "motion_discontinuities_count": len(self.motion_discontinuities),
            "avg_motion_score": round(self.avg_motion_score, 2),
            "wobble_frames_count": len(self.wobble_frames),
            "avg_wobble_score": round(self.avg_wobble_score, 4),
            "fps_quality_score": round(self.fps_quality_score, 1),
            "motion_quality_score": round(self.motion_quality_score, 1),
            "duplicate_quality_score": round(self.duplicate_quality_score, 1),
            "wobble_quality_score": round(self.wobble_quality_score, 1),
            "overall_quality_score": round(self.overall_quality_score, 1),
        }


class VideoAnalyzer:
    """
    Comprehensive video quality analyzer for AI-generated videos.

    Analyzes:
    - FPS dynamics and frame timing
    - Motion continuity between frames
    - Duplicate/frozen frames
    - Wobble/jitter distortion
    """

    def __init__(
        self,
        duplicate_threshold: float = 0.98,
        motion_threshold: float = 0.3,
        wobble_threshold: float = 0.02,
        fps_drop_threshold: float = 0.8,
    ):
        """
        Initialize the video analyzer.

        Args:
            duplicate_threshold: Similarity threshold for duplicate detection (0-1).
            motion_threshold: Threshold for motion discontinuity detection.
            wobble_threshold: Threshold for wobble/jitter detection.
            fps_drop_threshold: Ratio threshold for FPS drop detection.
        """
        self.duplicate_threshold = duplicate_threshold
        self.motion_threshold = motion_threshold
        self.wobble_threshold = wobble_threshold
        self.fps_drop_threshold = fps_drop_threshold

    def analyze(self, video_path: str | Path) -> VideoAnalysisResult:
        """
        Analyze a video file for quality issues.

        Args:
            video_path: Path to the video file.

        Returns:
            VideoAnalysisResult containing all analysis metrics.
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0

            result = VideoAnalysisResult(
                filepath=str(video_path),
                total_frames=total_frames,
                duration=duration,
                fps=fps,
                actual_fps=fps,
                resolution=(width, height),
            )

            # Analyze frames
            self._analyze_frames(cap, result)

            # Calculate quality scores
            self._calculate_quality_scores(result)

            return result

        finally:
            cap.release()

    def _analyze_frames(self, cap: cv2.VideoCapture, result: VideoAnalysisResult) -> None:
        """Analyze all frames in the video."""
        prev_frame = None
        prev_gray = None
        prev_flow = None
        frame_times = []

        frame_num = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            frame_times.append(timestamp)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is not None:
                # Duplicate frame detection
                similarity = self._calculate_similarity(prev_gray, gray)
                if similarity > self.duplicate_threshold:
                    result.duplicate_frames.append(frame_num)

                # Motion analysis
                motion_score = self._calculate_motion(prev_gray, gray)
                result.motion_scores.append(motion_score)

                # Motion discontinuity detection
                if len(result.motion_scores) > 1:
                    prev_motion = result.motion_scores[-2]
                    if prev_motion > 0:
                        motion_ratio = motion_score / prev_motion
                        if motion_ratio > (1 + self.motion_threshold) or motion_ratio < (1 - self.motion_threshold):
                            if motion_score > 5:  # Ignore very low motion
                                result.motion_discontinuities.append(frame_num)

                # Wobble detection using optical flow
                flow = self._calculate_optical_flow(prev_gray, gray)
                if prev_flow is not None:
                    wobble_score = self._calculate_wobble(prev_flow, flow)
                    result.wobble_scores.append(wobble_score)
                    if wobble_score > self.wobble_threshold:
                        result.wobble_frames.append(frame_num)
                prev_flow = flow

            prev_frame = frame
            prev_gray = gray
            frame_num += 1

        # Calculate FPS dynamics
        if len(frame_times) > 1:
            frame_intervals = np.diff(frame_times)
            frame_intervals = frame_intervals[frame_intervals > 0]  # Remove zeros
            if len(frame_intervals) > 0:
                result.fps_variance = np.var(frame_intervals)
                result.actual_fps = 1.0 / np.mean(frame_intervals) if np.mean(frame_intervals) > 0 else result.fps

                # Detect FPS drops
                expected_interval = 1.0 / result.fps
                for i, interval in enumerate(frame_intervals):
                    if interval > expected_interval / self.fps_drop_threshold:
                        result.fps_drops.append({
                            "frame": i + 1,
                            "expected_interval": expected_interval,
                            "actual_interval": interval,
                        })

        # Calculate averages
        if result.motion_scores:
            result.avg_motion_score = np.mean(result.motion_scores)
        if result.wobble_scores:
            result.avg_wobble_score = np.mean(result.wobble_scores)
        if result.total_frames > 0:
            result.duplicate_percentage = (len(result.duplicate_frames) / result.total_frames) * 100

    def _calculate_similarity(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate structural similarity between two frames."""
        # Use normalized cross-correlation for speed
        result = cv2.matchTemplate(frame1, frame2, cv2.TM_CCOEFF_NORMED)
        return float(result[0][0])

    def _calculate_motion(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> float:
        """Calculate motion magnitude between two frames."""
        diff = cv2.absdiff(prev_gray, curr_gray)
        return float(np.mean(diff))

    def _calculate_optical_flow(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> np.ndarray:
        """Calculate dense optical flow between two frames."""
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        return flow

    def _calculate_wobble(self, prev_flow: np.ndarray, curr_flow: np.ndarray) -> float:
        """Calculate wobble/jitter between consecutive optical flows."""
        flow_diff = curr_flow - prev_flow
        magnitude = np.sqrt(flow_diff[..., 0]**2 + flow_diff[..., 1]**2)
        return float(np.std(magnitude))

    def _calculate_quality_scores(self, result: VideoAnalysisResult) -> None:
        """Calculate quality scores based on analysis results."""
        # FPS Quality (penalize variance and drops)
        fps_penalty = min(result.fps_variance * 1000, 50)  # Cap at 50
        fps_penalty += len(result.fps_drops) * 2
        result.fps_quality_score = max(0, 100 - fps_penalty)

        # Duplicate Quality
        result.duplicate_quality_score = max(0, 100 - result.duplicate_percentage * 2)

        # Motion Quality (penalize discontinuities)
        if result.total_frames > 0:
            discontinuity_rate = len(result.motion_discontinuities) / result.total_frames * 100
            result.motion_quality_score = max(0, 100 - discontinuity_rate * 10)

        # Wobble Quality
        if result.total_frames > 0:
            wobble_rate = len(result.wobble_frames) / result.total_frames * 100
            result.wobble_quality_score = max(0, 100 - wobble_rate * 5)

        # Overall Quality (weighted average)
        result.overall_quality_score = (
            result.fps_quality_score * 0.2 +
            result.duplicate_quality_score * 0.3 +
            result.motion_quality_score * 0.25 +
            result.wobble_quality_score * 0.25
        )
