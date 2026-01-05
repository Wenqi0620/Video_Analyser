#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频分析工具 - 分析视频的帧率和清晰度
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from collections import defaultdict

# OpenCV 作为可选依赖
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None

# Matplotlib 作为可选依赖（用于可视化）
try:
    import matplotlib
    # 使用非交互式后端（避免在无图形界面环境崩溃）
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    matplotlib = None


class VideoAnalyzer:
    """视频分析器类"""
    
    def __init__(self, video_path: str):
        """
        初始化视频分析器
        
        Args:
            video_path: 视频文件路径
        """
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        self.video = None
        self.metadata = {}
    
    def analyze_with_opencv(self) -> Dict:
        """
        使用OpenCV分析视频
        
        Returns:
            包含视频信息的字典
        """
        if not OPENCV_AVAILABLE:
            raise ImportError(
                "OpenCV未安装。请安装: pip install opencv-python\n"
                "或者使用 ffprobe 方法（需要安装 ffmpeg）"
            )
        
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")
        
        try:
            # 获取基本信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # 读取第一帧来验证分辨率
            ret, frame = cap.read()
            if ret:
                actual_height, actual_width = frame.shape[:2]
            else:
                actual_width, actual_height = width, height
            
            result = {
                'file_path': str(self.video_path),
                'file_size_mb': self.video_path.stat().st_size / (1024 * 1024),
                'fps': round(fps, 3),
                'frame_count': frame_count,
                'duration_seconds': round(duration, 3),
                'resolution': {
                    'width': width,
                    'height': height,
                    'aspect_ratio': round(width / height, 3) if height > 0 else 0
                },
                'actual_resolution': {
                    'width': actual_width,
                    'height': actual_height
                },
                'method': 'OpenCV'
            }
            
            return result
            
        finally:
            cap.release()
    
    def analyze_with_ffprobe(self) -> Dict:
        """
        使用ffprobe分析视频（更准确，但需要安装ffmpeg）
        
        Returns:
            包含详细视频信息的字典
        """
        try:
            # 使用ffprobe获取详细的视频信息
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(self.video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            
            # 提取视频流信息
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                raise ValueError("未找到视频流")
            
            # 提取信息
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            # 获取帧率（可能有多种格式）
            fps_str = video_stream.get('r_frame_rate', '0/1')
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                fps = num / den if den > 0 else 0
            else:
                fps = float(fps_str)
            
            # 获取总帧数
            frame_count = int(video_stream.get('nb_frames', 0))
            if frame_count == 0:
                # 如果nb_frames不可用，尝试从duration和fps计算
                duration_str = video_stream.get('duration') or data.get('format', {}).get('duration', '0')
                duration = float(duration_str)
                frame_count = int(duration * fps)
            
            # 获取比特率
            bitrate = int(data.get('format', {}).get('bit_rate', 0))
            
            result = {
                'file_path': str(self.video_path),
                'file_size_mb': self.video_path.stat().st_size / (1024 * 1024),
                'fps': round(fps, 3),
                'frame_count': frame_count,
                'duration_seconds': round(float(data.get('format', {}).get('duration', 0)), 3),
                'resolution': {
                    'width': width,
                    'height': height,
                    'aspect_ratio': round(width / height, 3) if height > 0 else 0
                },
                'codec': video_stream.get('codec_name', 'unknown'),
                'bitrate_kbps': round(bitrate / 1000, 2) if bitrate > 0 else None,
                'pixel_format': video_stream.get('pix_fmt', 'unknown'),
                'method': 'ffprobe'
            }
            
            return result
            
        except FileNotFoundError:
            raise FileNotFoundError(
                "ffprobe未找到。请安装ffmpeg:\n"
                "macOS: brew install ffmpeg\n"
                "Ubuntu: sudo apt-get install ffmpeg\n"
                "Windows: 从 https://ffmpeg.org/download.html 下载"
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffprobe执行失败: {e}")
    
    def analyze(self, prefer_ffprobe: bool = True) -> Dict:
        """
        分析视频（优先使用ffprobe，失败则使用OpenCV）
        
        Args:
            prefer_ffprobe: 是否优先使用ffprobe
            
        Returns:
            包含视频信息的字典
        """
        if prefer_ffprobe:
            try:
                return self.analyze_with_ffprobe()
            except (FileNotFoundError, RuntimeError) as e:
                if OPENCV_AVAILABLE:
                    print(f"警告: ffprobe不可用 ({e})，使用OpenCV分析", file=sys.stderr)
                    return self.analyze_with_opencv()
                else:
                    raise RuntimeError(
                        f"ffprobe不可用 ({e})，且OpenCV也未安装。\n"
                        "请安装以下任一工具:\n"
                        "  - ffmpeg (推荐): brew install ffmpeg\n"
                        "  - OpenCV: pip install opencv-python"
                    )
        else:
            if not OPENCV_AVAILABLE:
                # 如果指定用OpenCV但不可用，尝试ffprobe
                print("警告: OpenCV未安装，尝试使用ffprobe", file=sys.stderr)
                try:
                    return self.analyze_with_ffprobe()
                except Exception as e:
                    raise ImportError(
                        f"OpenCV未安装，且ffprobe也失败 ({e})\n"
                        "请安装: pip install opencv-python"
                    )
            return self.analyze_with_opencv()
    
    def print_analysis(self, result: Optional[Dict] = None):
        """
        打印分析结果
        
        Args:
            result: 分析结果字典，如果为None则重新分析
        """
        if result is None:
            result = self.analyze()
        
        print("\n" + "="*60)
        print(f"视频分析结果: {self.video_path.name}")
        print("="*60)
        print(f"文件路径: {result['file_path']}")
        print(f"文件大小: {result['file_size_mb']:.2f} MB")
        print(f"\n【帧率信息】")
        print(f"  帧率 (FPS): {result['fps']}")
        print(f"  总帧数: {result['frame_count']}")
        print(f"  时长: {result['duration_seconds']:.2f} 秒")
        print(f"\n【清晰度信息】")
        print(f"  分辨率: {result['resolution']['width']} x {result['resolution']['height']}")
        print(f"  宽高比: {result['resolution']['aspect_ratio']}")
        if 'actual_resolution' in result:
            actual = result['actual_resolution']
            print(f"  实际分辨率: {actual['width']} x {actual['height']}")
        if 'codec' in result:
            print(f"  编解码器: {result['codec']}")
        if 'bitrate_kbps' in result and result['bitrate_kbps']:
            print(f"  比特率: {result['bitrate_kbps']:.2f} kbps")
        if 'pixel_format' in result:
            print(f"  像素格式: {result['pixel_format']}")
        print(f"\n分析方法: {result['method']}")
        print("="*60 + "\n")
        
        return result
    
    def analyze_fps_dynamics(self) -> Dict:
        """
        按秒分析视频的FPS动态变化
        
        Returns:
            包含每秒FPS信息的字典
        """
        if not OPENCV_AVAILABLE:
            raise ImportError(
                "OpenCV未安装。FPS动态分析需要OpenCV。\n"
                "请安装: pip install opencv-python numpy"
            )
        
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")
        
        try:
            # 获取基本信息
            declared_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 存储每秒的帧数
            frames_per_second = defaultdict(int)
            frame_timestamps = []
            
            print(f"正在逐秒分析FPS... (声明帧率: {declared_fps:.3f} FPS)", file=sys.stderr)
            
            frame_number = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 基于帧数和FPS计算时间戳（更准确）
                timestamp = frame_number / declared_fps if declared_fps > 0 else 0
                second = int(timestamp)
                
                frames_per_second[second] += 1
                frame_timestamps.append({
                    'frame_number': frame_number,
                    'timestamp': timestamp,
                    'second': second
                })
                
                frame_number += 1
                
                # 进度提示
                if frame_number % 100 == 0:
                    print(f"  已处理 {frame_number}/{total_frame_count} 帧 ({frame_number*100//total_frame_count}%)", 
                          file=sys.stderr, end='\r')
            
            print("", file=sys.stderr)  # 换行
            
            # 找出最后一秒（可能不完整）
            all_seconds = sorted(frames_per_second.keys())
            last_second = all_seconds[-1] if all_seconds else None
            
            # 计算实际的视频时长（基于总帧数和FPS）
            actual_duration = frame_number / declared_fps if declared_fps > 0 else 0
            
            # 计算每秒的实际FPS
            per_second_fps = {}
            for second, frame_count in sorted(frames_per_second.items()):
                is_complete = (second != last_second)  # 最后一秒可能不完整
                
                if is_complete:
                    # 完整秒：直接使用帧数作为FPS
                    fps = float(frame_count)
                else:
                    # 不完整秒：计算实际时长内的FPS
                    # 最后一秒的实际时长 = 总时长 - 完整秒数
                    actual_duration_of_last_second = actual_duration - last_second
                    if actual_duration_of_last_second > 0:
                        # 实际FPS = 帧数 / 实际时长（秒）
                        fps = frame_count / actual_duration_of_last_second
                    else:
                        fps = float(frame_count)  # 如果计算异常，使用帧数
                
                per_second_fps[second] = {
                    'fps': float(fps),
                    'frame_count': frame_count,
                    'is_complete_second': is_complete,
                    'actual_duration': actual_duration if is_complete else (actual_duration_of_last_second if last_second is not None and not is_complete else 1.0)
                }
            
            # 计算统计信息（排除最后一秒，因为它可能不完整）
            complete_seconds_fps = [data['fps'] for data in per_second_fps.values() 
                                   if data.get('is_complete_second', True)]
            all_fps_values = [data['fps'] for data in per_second_fps.values()]
            
            if complete_seconds_fps:
                overall_stats = {
                    'declared_fps': float(declared_fps),
                    'mean_fps': float(np.mean(complete_seconds_fps)),
                    'std_fps': float(np.std(complete_seconds_fps)),
                    'min_fps': float(np.min(complete_seconds_fps)),
                    'max_fps': float(np.max(complete_seconds_fps)),
                    'median_fps': float(np.median(complete_seconds_fps)),
                    'last_second_fps': per_second_fps[last_second]['fps'] if last_second else None,
                    'last_second_excluded': True,  # 标记最后一秒已被排除
                    'complete_seconds_count': len(complete_seconds_fps),
                    'total_seconds_count': len(all_fps_values)
                }
            elif all_fps_values:
                # 如果没有完整秒（视频很短），使用所有数据
                overall_stats = {
                    'declared_fps': float(declared_fps),
                    'mean_fps': float(np.mean(all_fps_values)),
                    'std_fps': float(np.std(all_fps_values)),
                    'min_fps': float(np.min(all_fps_values)),
                    'max_fps': float(np.max(all_fps_values)),
                    'median_fps': float(np.median(all_fps_values)),
                    'last_second_fps': per_second_fps[last_second]['fps'] if last_second else None,
                    'last_second_excluded': False,
                    'complete_seconds_count': 0,
                    'total_seconds_count': len(all_fps_values)
                }
            else:
                overall_stats = {
                    'declared_fps': float(declared_fps),
                    'mean_fps': 0.0,
                    'std_fps': 0.0,
                    'min_fps': 0.0,
                    'max_fps': 0.0,
                    'median_fps': 0.0,
                    'last_second_fps': None,
                    'last_second_excluded': False,
                    'complete_seconds_count': 0,
                    'total_seconds_count': 0
                }
            
            result = {
                'video_info': {
                    'declared_fps': float(declared_fps),
                    'total_frame_count': total_frame_count,
                    'resolution': {'width': width, 'height': height},
                    'total_seconds': len(frames_per_second)
                },
                'per_second_fps': per_second_fps,
                'overall_stats': overall_stats
            }
            
            return result
            
        finally:
            cap.release()
    
    def print_fps_dynamics(self, result: Optional[Dict] = None):
        """
        打印FPS动态分析结果
        
        Args:
            result: 分析结果，如果为None则重新分析
        """
        if result is None:
            result = self.analyze_fps_dynamics()
        
        video_info = result['video_info']
        overall_stats = result['overall_stats']
        per_second_fps = result['per_second_fps']
        
        print("\n" + "="*60)
        print(f"FPS动态变化分析: {self.video_path.name}")
        print("="*60)
        print(f"视频信息:")
        print(f"  声明帧率: {video_info['declared_fps']:.3f} FPS")
        print(f"  总帧数: {video_info['total_frame_count']}")
        print(f"  总时长: {video_info['total_seconds']} 秒")
        print(f"  分辨率: {video_info['resolution']['width']}x{video_info['resolution']['height']}")
        
        print(f"\n【整体FPS统计】")
        print(f"  声明帧率: {overall_stats['declared_fps']:.3f} FPS")
        print(f"  平均实际FPS: {overall_stats['mean_fps']:.3f} FPS (基于 {overall_stats.get('complete_seconds_count', 0)} 个完整秒)")
        print(f"  中位数FPS: {overall_stats['median_fps']:.3f} FPS")
        print(f"  标准差: {overall_stats['std_fps']:.3f} FPS")
        print(f"  FPS范围: {overall_stats['min_fps']:.3f} - {overall_stats['max_fps']:.3f} FPS")
        
        # 计算并显示更多统计信息
        complete_seconds_fps = [data['fps'] for data in per_second_fps.values() 
                               if data.get('is_complete_second', True)]
        if complete_seconds_fps and len(complete_seconds_fps) > 0:
            fps_array = np.array(complete_seconds_fps)
            variance = np.var(fps_array)
            mean_fps = overall_stats['mean_fps']
            
            # 分位数
            q25 = np.percentile(fps_array, 25)
            q75 = np.percentile(fps_array, 75)
            iqr = q75 - q25  # 四分位距
            
            # 变异系数（CV）
            cv = (overall_stats['std_fps'] / mean_fps * 100) if mean_fps > 0 else 0
            
            # 与声明FPS的偏差
            deviation_from_declared = mean_fps - overall_stats['declared_fps']
            deviation_percentage = (deviation_from_declared / overall_stats['declared_fps'] * 100) if overall_stats['declared_fps'] > 0 else 0
            
            print(f"\n【FPS变异分析】")
            print(f"  方差: {variance:.6f}")
            print(f"  标准差: {overall_stats['std_fps']:.6f} FPS")
            print(f"  变异系数 (CV): {cv:.2f}%")
            print(f"  四分位距 (IQR): {iqr:.3f} FPS (Q1: {q25:.3f}, Q3: {q75:.3f})")
            print(f"  与声明FPS偏差: {deviation_from_declared:+.3f} FPS ({deviation_percentage:+.2f}%)")
            
            # 稳定性评分
            if cv < 1.0:
                stability_level = "优秀"
            elif cv < 3.0:
                stability_level = "良好"
            elif cv < 5.0:
                stability_level = "一般"
            else:
                stability_level = "较差"
            
            stability_score = max(0, 100 - cv * 10)  # 基于CV的稳定性分数
            print(f"  稳定性评分: {stability_score:.1f}/100 ({stability_level})")
            
            # 检测异常值（使用IQR方法，如果IQR为0则使用标准差方法）
            if iqr > 0:
                lower_bound = q25 - 1.5 * iqr
                upper_bound = q75 + 1.5 * iqr
                outliers = [fps for fps in fps_array if fps < lower_bound or fps > upper_bound]
            else:
                # 如果IQR为0，使用均值±2倍标准差方法
                lower_bound = mean_fps - 2 * overall_stats['std_fps']
                upper_bound = mean_fps + 2 * overall_stats['std_fps']
                outliers = [fps for fps in fps_array if fps < lower_bound or fps > upper_bound]
            
            if outliers:
                print(f"  异常值数量: {len(outliers)} (超出范围: {lower_bound:.3f} - {upper_bound:.3f})")
                print(f"  异常值: {[round(float(x), 3) for x in sorted(set(outliers))]}")
            else:
                print(f"  异常值: 无")
        
        # 显示最后一秒信息（如果存在）
        if overall_stats.get('last_second_fps') is not None:
            last_sec = overall_stats['last_second_fps']
            last_sec_data = None
            all_seconds = sorted(per_second_fps.keys())
            if all_seconds:
                last_sec_data = per_second_fps[all_seconds[-1]]
            if last_sec_data and not last_sec_data.get('is_complete_second', True):
                actual_dur = last_sec_data.get('actual_duration', 1.0)
                print(f"\n【最后一秒信息】")
                print(f"  FPS: {last_sec:.3f} FPS")
                print(f"  实际时长: {actual_dur:.3f} 秒")
                print(f"  帧数: {last_sec_data['frame_count']}")
                print(f"  状态: 不完整（已排除在统计之外）")
        
        print(f"\n【逐秒FPS统计】")
        print(f"{'秒':<6} {'FPS':<12} {'帧数':<8} {'与声明帧率差异':<18} {'备注':<10}")
        print("-" * 70)
        
        declared = overall_stats['declared_fps']
        sorted_seconds = sorted(per_second_fps.keys())
        display_count = min(30, len(sorted_seconds))
        
        for second in sorted_seconds[:display_count]:
            data = per_second_fps[second]
            fps = data['fps']
            diff = fps - declared
            diff_str = f"{diff:+.3f}" if diff != 0 else "0.000"
            # 标记不完整的秒，并显示实际时长
            if not data.get('is_complete_second', True):
                actual_dur = data.get('actual_duration', 1.0)
                note = f"(不完整,{actual_dur:.2f}s)"
            else:
                note = ""
            print(f"{second:<6} {fps:>10.3f}   {data['frame_count']:<8} {diff_str:>18} {note:<12}")
        
        if len(per_second_fps) > 30:
            print(f"... (共 {len(per_second_fps)} 秒，仅显示前30秒)")
            if sorted_seconds and not per_second_fps[sorted_seconds[-1]].get('is_complete_second', True):
                print(f"注: 最后一秒({sorted_seconds[-1]})可能不完整，已排除在整体统计之外")
            print(f"\n使用 --json 查看完整数据，或使用 --plot 查看可视化图表")
        
        print("="*60 + "\n")
        
        return result
    
    def plot_fps_dynamics(self, result: Optional[Dict] = None, 
                         output_path: Optional[str] = None):
        """
        绘制FPS动态变化的可视化图表
        
        Args:
            result: 分析结果，如果为None则重新分析
            output_path: 保存图片的路径，如果为None则显示
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "Matplotlib未安装。可视化功能需要matplotlib。\n"
                "请安装: pip install matplotlib"
            )
        
        if result is None:
            result = self.analyze_fps_dynamics()
        
        per_second_fps = result['per_second_fps']
        overall_stats = result['overall_stats']
        video_info = result['video_info']
        
        # 提取数据（排除不完整的最后一秒用于主要图表）
        all_seconds = sorted(per_second_fps.keys())
        if not all_seconds:
            print("警告: 没有数据可绘制", file=sys.stderr)
            return
        
        # 只使用完整秒的数据绘制主要图表
        complete_seconds = [s for s in all_seconds 
                          if per_second_fps[s].get('is_complete_second', True)]
        fps_values_complete = [per_second_fps[s]['fps'] for s in complete_seconds] if complete_seconds else []
        fps_values_all = [per_second_fps[s]['fps'] for s in all_seconds]
        declared_fps = overall_stats['declared_fps']
        
        if not fps_values_all:
            print("警告: 没有FPS数据可绘制", file=sys.stderr)
            return
        
        # 创建图表
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(f'FPS动态变化分析: {self.video_path.name}', fontsize=14, fontweight='bold')
        
        # 1. FPS随时间变化（使用所有秒的数据，但标注不完整的）
        ax1 = axes[0]
        ax1.plot(all_seconds, fps_values_all, 'b-o', markersize=4, linewidth=1.5, label='实际FPS', alpha=0.7)
        ax1.axhline(y=declared_fps, color='r', linestyle='--', linewidth=2, label=f'声明FPS ({declared_fps:.3f})')
        ax1.axhline(y=overall_stats['mean_fps'], color='g', linestyle='--', linewidth=2, 
                   label=f'平均FPS ({overall_stats["mean_fps"]:.3f})')
        
        ax1.set_xlabel('时间 (秒)', fontsize=11)
        ax1.set_ylabel('FPS (帧/秒)', fontsize=11)
        ax1.set_title('FPS随时间变化', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best', fontsize=10)
        
        # 添加统计信息文本框
        stats_text = (f'平均: {overall_stats["mean_fps"]:.3f} FPS\n'
                     f'中位数: {overall_stats["median_fps"]:.3f} FPS\n'
                     f'标准差: {overall_stats["std_fps"]:.3f} FPS\n'
                     f'范围: {overall_stats["min_fps"]:.3f} - {overall_stats["max_fps"]:.3f} FPS')
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 2. FPS分布直方图（使用完整秒的数据）
        ax2 = axes[1]
        hist_data = fps_values_complete if fps_values_complete else fps_values_all
        unique_values = len(set(hist_data)) if hist_data else 1
        bins_count = min(30, max(1, unique_values))
        n, bins, patches = ax2.hist(hist_data, bins=bins_count, 
                                    edgecolor='black', alpha=0.7, color='skyblue')
        ax2.axvline(x=declared_fps, color='r', linestyle='--', linewidth=2, 
                   label=f'声明FPS ({declared_fps:.3f})')
        ax2.axvline(x=overall_stats['mean_fps'], color='g', linestyle='--', linewidth=2,
                   label=f'平均FPS ({overall_stats["mean_fps"]:.3f})')
        ax2.axvline(x=overall_stats['median_fps'], color='orange', linestyle='--', linewidth=2,
                   label=f'中位数FPS ({overall_stats["median_fps"]:.3f})')
        
        ax2.set_xlabel('FPS (帧/秒)', fontsize=11)
        ax2.set_ylabel('频次 (秒数)', fontsize=11)
        ax2.set_title('FPS分布直方图', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.legend(loc='best', fontsize=10)
        
        plt.tight_layout()
        
        if output_path:
            try:
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"FPS动态变化图表已保存到: {output_path}")
            except Exception as e:
                print(f"保存图表时出错: {e}", file=sys.stderr)
        else:
            # 在非图形环境中，直接保存到默认文件
            default_path = "fps_dynamics.png"
            try:
                plt.savefig(default_path, dpi=150, bbox_inches='tight')
                print(f"FPS动态变化图表已保存到: {default_path}")
            except Exception as e:
                print(f"保存图表时出错: {e}", file=sys.stderr)
                # 如果保存失败，尝试不显示（避免在无图形界面环境崩溃）
                try:
                    import matplotlib
                    matplotlib.use('Agg')  # 使用非交互式后端
                    plt.savefig(default_path, dpi=150, bbox_inches='tight')
                    print(f"FPS动态变化图表已保存到: {default_path}")
                except:
                    pass
        
        plt.close()
    
    def analyze_frame_dynamics(self, sample_rate: int = 1, use_gray: bool = True) -> Dict:
        """
        分析视频每秒的帧动态变化
        
        Args:
            sample_rate: 采样率，1表示分析每一帧，2表示每2帧分析一次，以此类推
            use_gray: 是否使用灰度图进行分析（更快）
            
        Returns:
            包含帧动态变化信息的字典
        """
        if not OPENCV_AVAILABLE:
            raise ImportError(
                "OpenCV未安装。帧动态分析需要OpenCV。\n"
                "请安装: pip install opencv-python numpy"
            )
        
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 存储每帧的数据
            frame_data = []
            prev_frame = None
            frame_number = 0
            
            print(f"正在分析帧动态变化... (共 {frame_count} 帧)", file=sys.stderr)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 按采样率采样
                if frame_number % sample_rate != 0:
                    frame_number += 1
                    continue
                
                # 转换为灰度图（如果需要）
                if use_gray:
                    current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                else:
                    current_frame = frame
                
                # 计算帧属性
                frame_stats = self._calculate_frame_stats(current_frame)
                
                # 计算帧间差异
                if prev_frame is not None:
                    frame_diff = self._calculate_frame_difference(prev_frame, current_frame)
                    frame_stats.update(frame_diff)
                else:
                    frame_stats['frame_diff'] = 0.0
                    frame_stats['motion_intensity'] = 0.0
                
                frame_stats['frame_number'] = frame_number
                frame_stats['timestamp'] = frame_number / fps if fps > 0 else 0
                
                frame_data.append(frame_stats)
                prev_frame = current_frame.copy()
                frame_number += 1
                
                # 进度提示
                if frame_number % 30 == 0:
                    print(f"  已处理 {frame_number}/{frame_count} 帧 ({frame_number*100//frame_count}%)", 
                          file=sys.stderr, end='\r')
            
            print("", file=sys.stderr)  # 换行
            
            # 按秒聚合数据
            per_second_stats = self._aggregate_by_second(frame_data, fps)
            
            # 计算整体统计
            overall_stats = self._calculate_overall_stats(frame_data)
            
            result = {
                'video_info': {
                    'fps': round(fps, 3),
                    'frame_count': frame_count,
                    'resolution': {'width': width, 'height': height},
                    'analyzed_frames': len(frame_data)
                },
                'per_frame_data': frame_data,
                'per_second_stats': per_second_stats,
                'overall_stats': overall_stats
            }
            
            return result
            
        finally:
            cap.release()
    
    def _calculate_frame_stats(self, frame: np.ndarray) -> Dict:
        """计算单帧的统计信息"""
        if len(frame.shape) == 3:
            # 彩色图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # 亮度统计
        brightness = np.mean(gray)
        
        # 对比度（标准差）
        contrast = np.std(gray)
        
        # 直方图统计
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        return {
            'brightness': float(brightness),
            'contrast': float(contrast),
            'min_intensity': int(np.min(gray)),
            'max_intensity': int(np.max(gray)),
            'histogram_peak': int(np.argmax(hist))
        }
    
    def _calculate_frame_difference(self, prev_frame: np.ndarray, current_frame: np.ndarray) -> Dict:
        """计算两帧之间的差异"""
        # 绝对差异
        diff = cv2.absdiff(prev_frame, current_frame)
        frame_diff = np.mean(diff)
        
        # 运动强度（差异的标准差）
        motion_intensity = np.std(diff)
        
        # 差异百分比（相对于最大可能差异）
        max_diff = 255.0 if prev_frame.dtype == np.uint8 else 1.0
        diff_percentage = (frame_diff / max_diff) * 100
        
        return {
            'frame_diff': float(frame_diff),
            'motion_intensity': float(motion_intensity),
            'diff_percentage': float(diff_percentage)
        }
    
    def _aggregate_by_second(self, frame_data: List[Dict], fps: float) -> Dict:
        """按秒聚合数据"""
        per_second = defaultdict(lambda: {
            'brightness': [],
            'contrast': [],
            'frame_diff': [],
            'motion_intensity': [],
            'frame_count': 0
        })
        
        for frame in frame_data:
            second = int(frame['timestamp'])
            per_second[second]['brightness'].append(frame['brightness'])
            per_second[second]['contrast'].append(frame['contrast'])
            per_second[second]['frame_diff'].append(frame['frame_diff'])
            per_second[second]['motion_intensity'].append(frame['motion_intensity'])
            per_second[second]['frame_count'] += 1
        
        # 计算每秒的统计值
        result = {}
        for second, data in sorted(per_second.items()):
            result[second] = {
                'brightness': {
                    'mean': float(np.mean(data['brightness'])),
                    'std': float(np.std(data['brightness'])),
                    'min': float(np.min(data['brightness'])),
                    'max': float(np.max(data['brightness']))
                },
                'contrast': {
                    'mean': float(np.mean(data['contrast'])),
                    'std': float(np.std(data['contrast'])),
                    'min': float(np.min(data['contrast'])),
                    'max': float(np.max(data['contrast']))
                },
                'motion': {
                    'mean_intensity': float(np.mean(data['motion_intensity'])),
                    'max_intensity': float(np.max(data['motion_intensity'])),
                    'mean_diff': float(np.mean(data['frame_diff'])),
                    'max_diff': float(np.max(data['frame_diff']))
                },
                'frame_count': data['frame_count']
            }
        
        return result
    
    def _calculate_overall_stats(self, frame_data: List[Dict]) -> Dict:
        """计算整体统计信息"""
        if not frame_data:
            return {}
        
        brightnesses = [f['brightness'] for f in frame_data]
        contrasts = [f['contrast'] for f in frame_data]
        frame_diffs = [f['frame_diff'] for f in frame_data]
        motion_intensities = [f['motion_intensity'] for f in frame_data]
        
        return {
            'brightness': {
                'mean': float(np.mean(brightnesses)),
                'std': float(np.std(brightnesses)),
                'min': float(np.min(brightnesses)),
                'max': float(np.max(brightnesses))
            },
            'contrast': {
                'mean': float(np.mean(contrasts)),
                'std': float(np.std(contrasts)),
                'min': float(np.min(contrasts)),
                'max': float(np.max(contrasts))
            },
            'motion': {
                'mean_intensity': float(np.mean(motion_intensities)),
                'max_intensity': float(np.max(motion_intensities)),
                'mean_diff': float(np.mean(frame_diffs)),
                'max_diff': float(np.max(frame_diffs))
            }
        }
    
    def print_frame_dynamics(self, result: Optional[Dict] = None, sample_rate: int = 1):
        """
        打印帧动态分析结果
        
        Args:
            result: 分析结果，如果为None则重新分析
            sample_rate: 采样率
        """
        if result is None:
            result = self.analyze_frame_dynamics(sample_rate=sample_rate)
        
        video_info = result['video_info']
        overall_stats = result['overall_stats']
        per_second = result['per_second_stats']
        
        print("\n" + "="*60)
        print(f"帧动态变化分析: {self.video_path.name}")
        print("="*60)
        print(f"视频信息:")
        print(f"  帧率: {video_info['fps']} FPS")
        print(f"  分辨率: {video_info['resolution']['width']}x{video_info['resolution']['height']}")
        print(f"  分析帧数: {video_info['analyzed_frames']}/{video_info['frame_count']}")
        
        print(f"\n【整体统计】")
        print(f"亮度 (0-255):")
        print(f"  平均值: {overall_stats['brightness']['mean']:.2f}")
        print(f"  范围: {overall_stats['brightness']['min']:.2f} - {overall_stats['brightness']['max']:.2f}")
        print(f"  标准差: {overall_stats['brightness']['std']:.2f}")
        
        print(f"\n对比度 (标准差):")
        print(f"  平均值: {overall_stats['contrast']['mean']:.2f}")
        print(f"  范围: {overall_stats['contrast']['min']:.2f} - {overall_stats['contrast']['max']:.2f}")
        
        print(f"\n运动/变化:")
        print(f"  平均运动强度: {overall_stats['motion']['mean_intensity']:.2f}")
        print(f"  最大运动强度: {overall_stats['motion']['max_intensity']:.2f}")
        print(f"  平均帧差异: {overall_stats['motion']['mean_diff']:.2f}")
        
        print(f"\n【逐秒统计】")
        print(f"{'秒':<6} {'亮度均值':<12} {'对比度均值':<14} {'运动强度':<12} {'帧数':<6}")
        print("-" * 60)
        
        for second in sorted(per_second.keys())[:20]:  # 只显示前20秒
            stats = per_second[second]
            print(f"{second:<6} {stats['brightness']['mean']:>10.2f}   "
                  f"{stats['contrast']['mean']:>12.2f}   "
                  f"{stats['motion']['mean_intensity']:>10.2f}   "
                  f"{stats['frame_count']:<6}")
        
        if len(per_second) > 20:
            print(f"... (共 {len(per_second)} 秒，仅显示前20秒)")
            print(f"\n使用 --json 查看完整数据，或使用 --plot 查看可视化图表")
        
        print("="*60 + "\n")
        
        return result
    
    def plot_frame_dynamics(self, result: Optional[Dict] = None, 
                           output_path: Optional[str] = None,
                           sample_rate: int = 1):
        """
        绘制帧动态变化的可视化图表
        
        Args:
            result: 分析结果，如果为None则重新分析
            output_path: 保存图片的路径，如果为None则显示
            sample_rate: 采样率
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "Matplotlib未安装。可视化功能需要matplotlib。\n"
                "请安装: pip install matplotlib"
            )
        
        if result is None:
            result = self.analyze_frame_dynamics(sample_rate=sample_rate)
        
        frame_data = result['per_frame_data']
        per_second = result['per_second_stats']
        
        # 提取数据
        timestamps = [f['timestamp'] for f in frame_data]
        brightnesses = [f['brightness'] for f in frame_data]
        contrasts = [f['contrast'] for f in frame_data]
        motion_intensities = [f['motion_intensity'] for f in frame_data]
        
        seconds = sorted(per_second.keys())
        sec_brightness = [per_second[s]['brightness']['mean'] for s in seconds]
        sec_contrast = [per_second[s]['contrast']['mean'] for s in seconds]
        sec_motion = [per_second[s]['motion']['mean_intensity'] for s in seconds]
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'帧动态变化分析: {self.video_path.name}', fontsize=14, fontweight='bold')
        
        # 1. 亮度变化
        axes[0, 0].plot(timestamps, brightnesses, alpha=0.6, linewidth=0.5)
        axes[0, 0].plot(seconds, sec_brightness, 'r-', linewidth=2, label='每秒均值')
        axes[0, 0].set_xlabel('时间 (秒)')
        axes[0, 0].set_ylabel('亮度')
        axes[0, 0].set_title('亮度变化')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()
        
        # 2. 对比度变化
        axes[0, 1].plot(timestamps, contrasts, alpha=0.6, linewidth=0.5)
        axes[0, 1].plot(seconds, sec_contrast, 'g-', linewidth=2, label='每秒均值')
        axes[0, 1].set_xlabel('时间 (秒)')
        axes[0, 1].set_ylabel('对比度')
        axes[0, 1].set_title('对比度变化')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].legend()
        
        # 3. 运动强度
        axes[1, 0].plot(timestamps, motion_intensities, alpha=0.6, linewidth=0.5)
        axes[1, 0].plot(seconds, sec_motion, 'b-', linewidth=2, label='每秒均值')
        axes[1, 0].set_xlabel('时间 (秒)')
        axes[1, 0].set_ylabel('运动强度')
        axes[1, 0].set_title('运动强度变化')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].legend()
        
        # 4. 综合视图（每秒统计）
        ax4 = axes[1, 1]
        ax4_twin = ax4.twinx()
        
        line1 = ax4.plot(seconds, sec_brightness, 'r-o', markersize=4, label='亮度', linewidth=2)
        line2 = ax4_twin.plot(seconds, sec_contrast, 'g-s', markersize=4, label='对比度', linewidth=2)
        line3 = ax4_twin.plot(seconds, sec_motion, 'b-^', markersize=4, label='运动强度', linewidth=2)
        
        ax4.set_xlabel('时间 (秒)')
        ax4.set_ylabel('亮度', color='r')
        ax4_twin.set_ylabel('对比度 / 运动强度', color='g')
        ax4.set_title('综合变化（每秒统计）')
        ax4.grid(True, alpha=0.3)
        
        # 合并图例
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax4.legend(lines, labels, loc='upper left')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存到: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def analyze_motion_quality(self, sample_rate: int = 1, 
                               duplicate_threshold: float = 0.98,
                               ssim_threshold: float = 0.95) -> Dict:
        """
        分析视频的运动质量问题（4个核心指标）
        
        Args:
            sample_rate: 采样率，1表示分析每一帧
            duplicate_threshold: 重复帧检测阈值（像素差异百分比，低于此值视为重复）
            ssim_threshold: SSIM阈值（高于此值视为相似/重复）
            
        Returns:
            包含4个运动质量指标的字典
        """
        if not OPENCV_AVAILABLE:
            raise ImportError(
                "OpenCV未安装。运动质量分析需要OpenCV。\n"
                "请安装: pip install opencv-python numpy"
            )
        
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")
        
        try:
            declared_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"正在分析运动质量问题... (共 {total_frame_count} 帧)", file=sys.stderr)
            
            # ========== 1. Effective FPS & PTS Jitter ==========
            print("  [1/4] 分析有效FPS和时间戳抖动...", file=sys.stderr)
            pts_data = self._analyze_pts_jitter(cap, declared_fps)
            
            # 重置视频流
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # ========== 2. Duplicate/Near-duplicate Frame Ratio ==========
            print("  [2/4] 检测重复/近似重复帧...", file=sys.stderr)
            duplicate_data = self._analyze_duplicate_frames(
                cap, sample_rate, duplicate_threshold, ssim_threshold
            )
            
            # 重置视频流
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # ========== 3. Motion Continuity / Jerkiness Score ==========
            print("  [3/4] 分析运动连续性（光流分析）...", file=sys.stderr)
            motion_continuity_data = self._analyze_motion_continuity(
                cap, sample_rate
            )
            
            # 重置视频流
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # ========== 4. Wobble / Rolling-shutter Distortion Score ==========
            print("  [4/4] 分析果冻效应/滚动快门失真...", file=sys.stderr)
            wobble_data = self._analyze_wobble_distortion(
                cap, sample_rate
            )
            
            result = {
                'video_info': {
                    'declared_fps': float(declared_fps),
                    'total_frame_count': total_frame_count,
                    'analyzed_frames': duplicate_data['analyzed_frame_count']
                },
                'effective_fps_pts_jitter': pts_data,
                'duplicate_frame_ratio': duplicate_data,
                'motion_continuity': motion_continuity_data,
                'wobble_distortion': wobble_data
            }
            
            return result
            
        finally:
            cap.release()
    
    def _analyze_pts_jitter(self, cap: cv2.VideoCapture, declared_fps: float) -> Dict:
        """分析PTS抖动和有效FPS"""
        pts_list = []
        frame_times = []
        frame_number = 0
        
        while True:
            ret = cap.grab()  # 只读取时间戳，不读取图像（更快）
            if not ret:
                break
            
            # 获取时间戳（毫秒）
            pts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            pts_sec = pts_ms / 1000.0
            
            if frame_number > 0:
                # 计算相邻帧的时间间隔
                delta_pts = pts_sec - pts_list[-1]
                frame_times.append(delta_pts)
            
            pts_list.append(pts_sec)
            frame_number += 1
            
            if frame_number % 100 == 0:
                print(f"    已处理 {frame_number} 帧", file=sys.stderr, end='\r')
        
        print("", file=sys.stderr)
        
        if len(frame_times) == 0:
            return {
                'effective_fps': declared_fps,
                'pts_jitter_std': 0.0,
                'pts_jitter_max': 0.0,
                'expected_delta': 1.0 / declared_fps if declared_fps > 0 else 0.0,
                'mean_delta': 0.0
            }
        
        expected_delta = 1.0 / declared_fps if declared_fps > 0 else 0.0
        mean_delta = np.mean(frame_times)
        effective_fps = 1.0 / mean_delta if mean_delta > 0 else 0.0
        
        # 计算时间间隔的方差（抖动）
        jitter_std = np.std(frame_times)
        jitter_max = np.max(np.abs(np.array(frame_times) - expected_delta))
        
        return {
            'effective_fps': float(effective_fps),
            'declared_fps': float(declared_fps),
            'pts_jitter_std': float(jitter_std),
            'pts_jitter_max': float(jitter_max),
            'expected_delta': float(expected_delta),
            'mean_delta': float(mean_delta),
            'jitter_percentage': float((jitter_std / expected_delta * 100) if expected_delta > 0 else 0.0)
        }
    
    def _analyze_duplicate_frames(self, cap: cv2.VideoCapture, 
                                  sample_rate: int,
                                  diff_threshold: float,
                                  ssim_threshold: float) -> Dict:
        """分析重复/近似重复帧"""
        prev_frame = None
        duplicate_count = 0
        near_duplicate_count = 0
        frame_number = 0
        analyzed_count = 0
        duplicate_frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % sample_rate != 0:
                frame_number += 1
                continue
            
            analyzed_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 下采样以加快计算
            small = cv2.resize(gray, (160, 120))
            
            if prev_frame is not None:
                prev_small = cv2.resize(prev_frame, (160, 120))
                
                # 方法1: 绝对差异
                diff = cv2.absdiff(small, prev_small)
                mean_diff = np.mean(diff) / 255.0
                diff_percentage = 1.0 - mean_diff
                
                # 方法2: SSIM（如果OpenCV版本支持）
                ssim_score = 1.0
                try:
                    # 尝试计算SSIM（需要自己实现或使用skimage）
                    # 这里用简化的版本：基于结构相似性
                    ssim_score = self._calculate_simple_ssim(small, prev_small)
                except:
                    pass
                
                # 判断是否为重复帧
                if diff_percentage >= diff_threshold or ssim_score >= ssim_threshold:
                    if diff_percentage >= 0.995 or ssim_score >= 0.99:
                        duplicate_count += 1
                        duplicate_frames.append(frame_number)
                    else:
                        near_duplicate_count += 1
            
            prev_frame = gray.copy()
            frame_number += 1
            
            if analyzed_count % 50 == 0:
                print(f"    已分析 {analyzed_count} 帧", file=sys.stderr, end='\r')
        
        print("", file=sys.stderr)
        
        total_frames = analyzed_count
        duplicate_ratio = duplicate_count / total_frames if total_frames > 0 else 0.0
        near_duplicate_ratio = near_duplicate_count / total_frames if total_frames > 0 else 0.0
        total_duplicate_ratio = (duplicate_count + near_duplicate_count) / total_frames if total_frames > 0 else 0.0
        
        return {
            'duplicate_frame_count': duplicate_count,
            'near_duplicate_frame_count': near_duplicate_count,
            'total_analyzed_frames': total_frames,
            'analyzed_frame_count': analyzed_count,
            'duplicate_ratio': float(duplicate_ratio),
            'near_duplicate_ratio': float(near_duplicate_ratio),
            'total_duplicate_ratio': float(total_duplicate_ratio),
            'duplicate_frame_indices': duplicate_frames[:100]  # 只保存前100个
        }
    
    def _calculate_simple_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """简化的SSIM计算"""
        # 简化的SSIM：基于均值、方差和协方差
        mu1 = np.mean(img1)
        mu2 = np.mean(img2)
        sigma1_sq = np.var(img1)
        sigma2_sq = np.var(img2)
        sigma12 = np.mean((img1 - mu1) * (img2 - mu2))
        
        C1 = 0.01 ** 2
        C2 = 0.03 ** 2
        
        ssim = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) * (sigma1_sq + sigma2_sq + C2))
        
        return float(ssim)
    
    def _analyze_motion_continuity(self, cap: cv2.VideoCapture, 
                                   sample_rate: int) -> Dict:
        """分析运动连续性（光流分析）"""
        prev_gray = None
        motion_magnitudes = []
        jerk_values = []
        frame_number = 0
        analyzed_count = 0
        
        # 光流参数
        flow_params = dict(
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % sample_rate != 0:
                frame_number += 1
                continue
            
            analyzed_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_gray is not None:
                # 计算光流（Farneback方法）
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None, **flow_params
                )
                
                # 计算光流幅度
                magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
                mean_magnitude = np.mean(magnitude)
                motion_magnitudes.append(mean_magnitude)
                
                # 计算jerk（加速度的变化率）
                if len(motion_magnitudes) >= 3:
                    # jerk = |m_{t+1} - 2*m_t + m_{t-1}|
                    jerk = abs(motion_magnitudes[-1] - 2 * motion_magnitudes[-2] + motion_magnitudes[-3])
                    jerk_values.append(jerk)
            
            prev_gray = gray.copy()
            frame_number += 1
            
            if analyzed_count % 20 == 0:
                print(f"    已分析 {analyzed_count} 帧", file=sys.stderr, end='\r')
        
        print("", file=sys.stderr)
        
        if len(motion_magnitudes) == 0:
            return {
                'mean_motion_magnitude': 0.0,
                'motion_std': 0.0,
                'mean_jerk': 0.0,
                'jerk_peak_ratio': 0.0,
                'jerkiness_score': 0.0
            }
        
        # 计算运动连续性指标
        mean_motion = np.mean(motion_magnitudes)
        motion_std = np.std(motion_magnitudes)
        
        # Jerkiness分析
        if len(jerk_values) > 0:
            mean_jerk = np.mean(jerk_values)
            # 定义异常尖峰：超过均值+2倍标准差
            threshold = mean_jerk + 2 * np.std(jerk_values)
            jerk_peaks = sum(1 for j in jerk_values if j > threshold)
            jerk_peak_ratio = jerk_peaks / len(jerk_values) if len(jerk_values) > 0 else 0.0
            
            # Jerkiness分数（0-100，越高越不连续）
            jerkiness_score = min(100.0, (jerk_peak_ratio * 50 + mean_jerk / mean_motion * 50) if mean_motion > 0 else 0.0)
        else:
            mean_jerk = 0.0
            jerk_peak_ratio = 0.0
            jerkiness_score = 0.0
        
        return {
            'mean_motion_magnitude': float(mean_motion),
            'motion_std': float(motion_std),
            'mean_jerk': float(mean_jerk),
            'jerk_peak_ratio': float(jerk_peak_ratio),
            'jerkiness_score': float(jerkiness_score),
            'motion_continuity_score': float(100.0 - jerkiness_score)  # 连续性分数（越高越好）
        }
    
    def _analyze_wobble_distortion(self, cap: cv2.VideoCapture,
                                   sample_rate: int) -> Dict:
        """分析果冻效应/滚动快门失真"""
        prev_gray = None
        grid_variance_scores = []
        frame_number = 0
        analyzed_count = 0
        
        # 光流参数
        flow_params = dict(
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
        
        # 网格大小（用于局部分析）
        grid_size = 8
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % sample_rate != 0:
                frame_number += 1
                continue
            
            analyzed_count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_gray is not None:
                # 计算光流
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None, **flow_params
                )
                
                # 将图像分成网格，分析每个网格块的光流
                h, w = flow.shape[:2]
                grid_h = h // grid_size
                grid_w = w // grid_size
                
                block_variances = []
                
                for i in range(grid_size):
                    for j in range(grid_size):
                        y_start = i * grid_h
                        y_end = (i + 1) * grid_h if i < grid_size - 1 else h
                        x_start = j * grid_w
                        x_end = (j + 1) * grid_w if j < grid_size - 1 else w
                        
                        block_flow = flow[y_start:y_end, x_start:x_end]
                        block_magnitude = np.sqrt(block_flow[..., 0] ** 2 + block_flow[..., 1] ** 2)
                        block_direction = np.arctan2(block_flow[..., 1], block_flow[..., 0])
                        
                        # 计算方向和幅度的方差（非刚体变形会导致高方差）
                        mag_variance = np.var(block_magnitude)
                        dir_variance = np.var(block_direction)
                        
                        # 综合方差分数
                        block_variance = (mag_variance + dir_variance * 10)  # 方向方差权重更高
                        block_variances.append(block_variance)
                
                # 计算所有块的方差分数（高方差表示wobble）
                grid_variance_score = np.mean(block_variances)
                grid_variance_scores.append(grid_variance_score)
            
            prev_gray = gray.copy()
            frame_number += 1
            
            if analyzed_count % 20 == 0:
                print(f"    已分析 {analyzed_count} 帧", file=sys.stderr, end='\r')
        
        print("", file=sys.stderr)
        
        if len(grid_variance_scores) == 0:
            return {
                'mean_wobble_score': 0.0,
                'wobble_std': 0.0,
                'wobble_distortion_score': 0.0
            }
        
        mean_wobble = np.mean(grid_variance_scores)
        wobble_std = np.std(grid_variance_scores)
        
        # Wobble失真分数（0-100，越高失真越严重）
        # 需要归一化，这里用经验阈值
        normalized_wobble = min(100.0, mean_wobble * 10)
        
        return {
            'mean_wobble_score': float(mean_wobble),
            'wobble_std': float(wobble_std),
            'wobble_distortion_score': float(normalized_wobble)
        }
    
    def print_motion_quality(self, result: Optional[Dict] = None):
        """打印运动质量分析结果"""
        if result is None:
            result = self.analyze_motion_quality()
        
        video_info = result['video_info']
        pts_data = result['effective_fps_pts_jitter']
        dup_data = result['duplicate_frame_ratio']
        motion_data = result['motion_continuity']
        wobble_data = result['wobble_distortion']
        
        print("\n" + "="*70)
        print(f"运动质量分析: {self.video_path.name}")
        print("="*70)
        print(f"视频信息:")
        print(f"  声明帧率: {video_info['declared_fps']:.3f} FPS")
        print(f"  总帧数: {video_info['total_frame_count']}")
        print(f"  分析帧数: {video_info['analyzed_frames']}")
        
        print(f"\n【1. 有效FPS & 时间戳抖动】")
        print(f"  声明帧率: {pts_data['declared_fps']:.3f} FPS")
        print(f"  有效FPS: {pts_data['effective_fps']:.3f} FPS")
        print(f"  预期帧间隔: {pts_data['expected_delta']*1000:.2f} ms")
        print(f"  实际平均间隔: {pts_data['mean_delta']*1000:.2f} ms")
        print(f"  PTS抖动标准差: {pts_data['pts_jitter_std']*1000:.2f} ms")
        print(f"  PTS最大抖动: {pts_data['pts_jitter_max']*1000:.2f} ms")
        print(f"  抖动百分比: {pts_data['jitter_percentage']:.2f}%")
        
        print(f"\n【2. 重复/近似重复帧比例】")
        print(f"  完全重复帧: {dup_data['duplicate_frame_count']} ({dup_data['duplicate_ratio']*100:.2f}%)")
        print(f"  近似重复帧: {dup_data['near_duplicate_frame_count']} ({dup_data['near_duplicate_ratio']*100:.2f}%)")
        print(f"  总重复率: {dup_data['total_duplicate_ratio']*100:.2f}%")
        if dup_data['duplicate_frame_indices']:
            print(f"  重复帧位置（前10个）: {dup_data['duplicate_frame_indices'][:10]}")
        
        print(f"\n【3. 运动连续性 / Jerkiness】")
        print(f"  平均运动幅度: {motion_data['mean_motion_magnitude']:.3f}")
        print(f"  运动标准差: {motion_data['motion_std']:.3f}")
        print(f"  平均Jerk值: {motion_data['mean_jerk']:.3f}")
        print(f"  Jerk尖峰比例: {motion_data['jerk_peak_ratio']*100:.2f}%")
        print(f"  Jerkiness分数: {motion_data['jerkiness_score']:.2f}/100 (越高越不连续)")
        print(f"  运动连续性分数: {motion_data['motion_continuity_score']:.2f}/100 (越高越好)")
        
        print(f"\n【4. 果冻效应 / 滚动快门失真】")
        print(f"  平均Wobble分数: {wobble_data['mean_wobble_score']:.3f}")
        print(f"  Wobble标准差: {wobble_data['wobble_std']:.3f}")
        print(f"  失真分数: {wobble_data['wobble_distortion_score']:.2f}/100 (越高失真越严重)")
        
        print("="*70 + "\n")
        
        return result


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python video_analyzer.py <视频文件路径> [选项]")
        print("\n选项:")
        print("  --json              输出JSON格式")
        print("  --fps-dynamics      分析FPS动态变化（按秒测量）并绘制图表")
        print("  --dynamics          分析帧动态变化（亮度、对比度、运动）")
        print("  --motion-quality    分析运动质量问题（4个核心指标）")
        print("  --plot [路径]       绘制动态变化图表（可选保存路径）")
        print("  --sample-rate N     采样率，默认1（分析每一帧）")
        print("\n示例:")
        print("  python video_analyzer.py video.mp4")
        print("  python video_analyzer.py video.mp4 --fps-dynamics")
        print("  python video_analyzer.py video.mp4 --fps-dynamics fps_chart.png")
        print("  python video_analyzer.py video.mp4 --dynamics")
        print("  python video_analyzer.py video.mp4 --dynamics --plot")
        print("  python video_analyzer.py video.mp4 --motion-quality")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    try:
        analyzer = VideoAnalyzer(video_path)
        
        # 检查是否是FPS动态分析
        if '--fps-dynamics' in sys.argv:
            # 执行FPS动态分析
            fps_result = analyzer.analyze_fps_dynamics()
            analyzer.print_fps_dynamics(fps_result)
            
            # 获取输出路径
            fps_idx = sys.argv.index('--fps-dynamics')
            output_path = None
            # 如果下一个参数不是选项（不以--开头），则作为输出路径
            if fps_idx + 1 < len(sys.argv) and not sys.argv[fps_idx + 1].startswith('--'):
                output_path = sys.argv[fps_idx + 1]
            else:
                # 默认文件名
                output_path = "fps_dynamics.png"
            
            # 绘制FPS动态变化图
            analyzer.plot_fps_dynamics(fps_result, output_path=output_path)
            
            # JSON输出
            if '--json' in sys.argv:
                print("\n" + "="*60)
                print("JSON输出:")
                print("="*60)
                print(json.dumps(fps_result, indent=2, ensure_ascii=False))
        
        # 检查是否是运动质量分析
        elif '--motion-quality' in sys.argv:
            sample_rate = 1
            if '--sample-rate' in sys.argv:
                idx = sys.argv.index('--sample-rate')
                if idx + 1 < len(sys.argv):
                    sample_rate = int(sys.argv[idx + 1])
            
            result = analyzer.analyze_motion_quality(sample_rate=sample_rate)
            analyzer.print_motion_quality(result)
            
            # JSON输出
            if '--json' in sys.argv:
                print("\n" + "="*60)
                print("JSON输出:")
                print("="*60)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 检查是否是帧动态分析
        elif '--dynamics' in sys.argv:
            sample_rate = 1
            if '--sample-rate' in sys.argv:
                idx = sys.argv.index('--sample-rate')
                if idx + 1 < len(sys.argv):
                    sample_rate = int(sys.argv[idx + 1])
            
            result = analyzer.analyze_frame_dynamics(sample_rate=sample_rate)
            analyzer.print_frame_dynamics(result, sample_rate=sample_rate)
            
            # 绘制图表
            if '--plot' in sys.argv:
                plot_idx = sys.argv.index('--plot')
                output_path = None
                if plot_idx + 1 < len(sys.argv) and not sys.argv[plot_idx + 1].startswith('--'):
                    output_path = sys.argv[plot_idx + 1]
                analyzer.plot_frame_dynamics(result, output_path=output_path, sample_rate=sample_rate)
            
            # JSON输出
            if '--json' in sys.argv:
                print("\n" + "="*60)
                print("JSON输出:")
                print("="*60)
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 基础分析
            result = analyzer.analyze()
            analyzer.print_analysis(result)
            
            # 返回JSON格式（可选）
            if '--json' in sys.argv:
                print("\n" + "="*60)
                print("JSON输出:")
                print("="*60)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
