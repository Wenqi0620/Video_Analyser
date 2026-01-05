"""
Video Analyser - Comprehensive video quality analyzer for AI-generated videos.

Analyzes FPS dynamics, motion continuity, duplicate frames, and wobble distortion.
"""

from .analyzer import VideoAnalyzer
from .batch_processor import BatchProcessor
from .report_generator import ReportGenerator

__version__ = "1.0.0"
__all__ = ["VideoAnalyzer", "BatchProcessor", "ReportGenerator"]
