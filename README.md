# Video Quality Analyzer

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Comprehensive video quality analysis tool for AI-generated videos. Analyzes FPS dynamics, motion continuity, duplicate frames, and wobble distortion. Batch processing with Excel/CSV reports.

**中文**: AI视频质量分析工具 - 分析视频帧率、清晰度、运动质量等指标，支持批量处理和Excel报告生成。

## ✨ Features

### 基础分析
- ✅ 分析视频帧率 (FPS)
- ✅ 分析视频分辨率（宽度、高度）
- ✅ 获取视频总帧数和时长
- ✅ 支持多种分析方法（OpenCV / ffprobe）
- ✅ 获取详细的视频编码信息（使用ffprobe时）

### 帧动态分析 🆕
- ✅ **帧间差异分析** - 检测相邻帧之间的变化
- ✅ **运动强度检测** - 量化视频中的运动程度
- ✅ **亮度变化分析** - 跟踪视频亮度随时间的变化
- ✅ **对比度变化分析** - 分析对比度的动态变化
- ✅ **逐秒统计** - 按秒聚合统计数据
- ✅ **可视化图表** - 生成动态变化图表（需要matplotlib）

## 安装依赖

你只需要安装以下**任一种**工具即可使用（推荐安装 OpenCV，更简单）：

### 方式1: 安装 OpenCV (推荐，简单快速)
```bash
pip3 install opencv-python numpy matplotlib
```

**注意**: 如果需要可视化功能，需要安装 matplotlib

### 方式2: 安装 ffmpeg (更准确，功能更全面)

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
从 [ffmpeg官网](https://ffmpeg.org/download.html) 下载并安装

### 方式3: 使用自动安装脚本
```bash
chmod +x install.sh
./install.sh
```

**注意**: 如果遇到 SSL 或权限错误，可以尝试：
- 使用 `pip3 install --user opencv-python numpy`
- 或使用 `sudo pip3 install opencv-python numpy` (不推荐)

## 使用方法

### 作为脚本使用

```bash
python video_analyzer.py <视频文件路径>
```

**示例:**
```bash
python video_analyzer.py video.mp4
```

**输出JSON格式:**
```bash
python video_analyzer.py video.mp4 --json
```

**分析帧动态变化:**
```bash
python video_analyzer.py video.mp4 --dynamics
```

**分析并绘制图表:**
```bash
python video_analyzer.py video.mp4 --dynamics --plot
```

**保存图表到文件:**
```bash
python video_analyzer.py video.mp4 --dynamics --plot output.png
```

**使用采样加快分析速度（每N帧分析一次）:**
```bash
python video_analyzer.py video.mp4 --dynamics --sample-rate 5 --plot
```

### 作为Python模块使用

```python
from video_analyzer import VideoAnalyzer

# 创建分析器
analyzer = VideoAnalyzer("video.mp4")

# 分析视频（优先使用ffprobe，不可用则用OpenCV）
result = analyzer.analyze()

# 打印结果
analyzer.print_analysis(result)

# 或者直接访问结果
print(f"帧率: {result['fps']} FPS")
print(f"分辨率: {result['resolution']['width']}x{result['resolution']['height']}")

# 只使用OpenCV
result_opencv = analyzer.analyze_with_opencv()

# 只使用ffprobe（如果已安装）
result_ffprobe = analyzer.analyze_with_ffprobe()

# 分析帧动态变化
result_dynamics = analyzer.analyze_frame_dynamics(sample_rate=1)
analyzer.print_frame_dynamics(result_dynamics)

# 绘制可视化图表
analyzer.plot_frame_dynamics(result_dynamics, output_path="dynamics.png")

# 访问逐秒统计
per_second = result_dynamics['per_second_stats']
print(f"第5秒的亮度: {per_second[5]['brightness']['mean']}")

# 访问整体统计
overall = result_dynamics['overall_stats']
print(f"平均运动强度: {overall['motion']['mean_intensity']}")
```

## 输出说明

分析结果包含以下信息：

- **文件路径**: 视频文件的完整路径
- **文件大小**: 以MB为单位
- **帧率 (FPS)**: 每秒帧数
- **总帧数**: 视频包含的总帧数
- **时长**: 视频时长（秒）
- **分辨率**: 宽度 x 高度
- **宽高比**: 宽度/高度
- **编解码器**: 视频编码格式（ffprobe）
- **比特率**: 视频比特率（ffprobe）
- **像素格式**: 像素格式（ffprobe）

### 帧动态分析结果包含：

- **每帧数据**: 每帧的亮度、对比度、帧间差异、运动强度
- **逐秒统计**: 按秒聚合的亮度、对比度、运动强度统计
- **整体统计**: 整个视频的亮度、对比度、运动强度统计
- **可视化图表**: 4个子图显示亮度、对比度、运动强度的变化趋势

## 方法对比

| 特性 | OpenCV | ffprobe |
|------|--------|---------|
| 安装难度 | 简单 | 需要额外安装ffmpeg |
| 帧率准确性 | 良好 | 更准确 |
| 分辨率检测 | 良好 | 更准确 |
| 编码信息 | 有限 | 详细信息 |
| 跨平台 | 是 | 是 |

默认情况下，工具会优先尝试使用ffprobe（更准确），如果不可用则自动回退到OpenCV。
