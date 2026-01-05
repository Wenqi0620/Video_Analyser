# 运动质量分析功能使用指南

## 功能说明

新增的运动质量分析功能实现了4个核心指标，用于检测视频中的运动质量问题：

### 1. Effective FPS & PTS Jitter（有效FPS和时间戳抖动）

- **目的**: 检测真实的掉帧和时间戳不稳定问题
- **指标**:
  - `effective_fps`: 基于实际时间戳计算的有效帧率
  - `pts_jitter_std`: 时间戳间隔的标准差（抖动程度）
  - `pts_jitter_max`: 最大时间戳抖动
  - `jitter_percentage`: 抖动百分比

### 2. Duplicate/Near-duplicate Frame Ratio（重复/近似重复帧比例）

- **目的**: 检测"看起来30帧其实在重复"的问题
- **方法**: 
  - 使用像素差异检测完全重复帧
  - 使用SSIM（结构相似性）检测近似重复帧
- **指标**:
  - `duplicate_ratio`: 完全重复帧比例
  - `near_duplicate_ratio`: 近似重复帧比例
  - `total_duplicate_ratio`: 总重复率

### 3. Motion Continuity / Jerkiness Score（运动连续性/抖动分数）

- **目的**: 检测动作连续性异常（高速掉帧、多主体掉帧）
- **方法**: 
  - 使用光流（Optical Flow）分析帧间运动
  - 计算运动幅度的Jerk（加速度变化率）：`|m_{t+1} - 2*m_t + m_{t-1}|`
  - 检测异常尖峰
- **指标**:
  - `jerkiness_score`: 抖动分数（0-100，越高越不连续）
  - `motion_continuity_score`: 运动连续性分数（0-100，越高越好）
  - `jerk_peak_ratio`: Jerk尖峰比例

### 4. Wobble / Rolling-shutter Distortion Score（果冻效应/滚动快门失真）

- **目的**: 检测果冻效应和滚动快门失真
- **方法**: 
  - 将图像分成网格，分析每个网格块的光流
  - 计算局部光流的方向和幅度方差
  - 非刚体变形（如wobble）会导致高方差
- **指标**:
  - `wobble_distortion_score`: 失真分数（0-100，越高失真越严重）

## 使用方法

### 命令行使用

```bash
# 基础分析
.venv/bin/python video_analyzer.py "视频路径.mp4" --motion-quality

# 使用采样加快速度（每5帧分析一次）
.venv/bin/python video_analyzer.py "视频路径.mp4" --motion-quality --sample-rate 5

# 输出JSON格式
.venv/bin/python video_analyzer.py "视频路径.mp4" --motion-quality --json
```

### Python API 使用

```python
from video_analyzer import VideoAnalyzer

# 创建分析器
analyzer = VideoAnalyzer("video.mp4")

# 分析运动质量（所有4个指标）
result = analyzer.analyze_motion_quality(
    sample_rate=1,           # 采样率（1=分析每一帧）
    duplicate_threshold=0.98, # 重复帧阈值
    ssim_threshold=0.95      # SSIM阈值
)

# 打印结果
analyzer.print_motion_quality(result)

# 访问特定指标
pts_data = result['effective_fps_pts_jitter']
print(f"有效FPS: {pts_data['effective_fps']}")
print(f"抖动百分比: {pts_data['jitter_percentage']}%")

dup_data = result['duplicate_frame_ratio']
print(f"重复帧率: {dup_data['total_duplicate_ratio']*100:.2f}%")

motion_data = result['motion_continuity']
print(f"运动连续性分数: {motion_data['motion_continuity_score']:.2f}/100")

wobble_data = result['wobble_distortion']
print(f"失真分数: {wobble_data['wobble_distortion_score']:.2f}/100")
```

## 输出说明

### 终端输出示例

```
==============================================================
运动质量分析: video.mp4
==============================================================
视频信息:
  声明帧率: 30.000 FPS
  总帧数: 456
  分析帧数: 456

【1. 有效FPS & 时间戳抖动】
  声明帧率: 30.000 FPS
  有效FPS: 29.866 FPS
  预期帧间隔: 33.33 ms
  实际平均间隔: 33.48 ms
  PTS抖动标准差: 0.52 ms
  PTS最大抖动: 2.10 ms
  抖动百分比: 1.56%

【2. 重复/近似重复帧比例】
  完全重复帧: 5 (1.10%)
  近似重复帧: 8 (1.75%)
  总重复率: 2.85%
  重复帧位置（前10个）: [45, 89, 134, ...]

【3. 运动连续性 / Jerkiness】
  平均运动幅度: 2.345
  运动标准差: 0.892
  平均Jerk值: 0.123
  Jerk尖峰比例: 3.52%
  Jerkiness分数: 12.45/100 (越高越不连续)
  运动连续性分数: 87.55/100 (越高越好)

【4. 果冻效应 / 滚动快门失真】
  平均Wobble分数: 0.245
  Wobble标准差: 0.089
  失真分数: 2.45/100 (越高失真越严重)
==============================================================
```

## 指标解释

### 理想值参考

- **PTS抖动百分比**: < 5% 为良好，> 10% 为有问题
- **重复帧率**: < 1% 为正常，> 5% 为严重问题
- **运动连续性分数**: > 80 为良好，< 60 为有问题
- **失真分数**: < 10 为良好，> 30 为严重失真

### 问题诊断

| 指标异常 | 可能原因 |
|---------|---------|
| 有效FPS远低于声明FPS | 真实掉帧 |
| PTS抖动大 | 时间戳不稳定，编码问题 |
| 重复帧率高 | 编码器问题，或者源视频问题 |
| Jerkiness分数高 | 动作不连续，卡顿，掉帧 |
| 失真分数高 | 果冻效应，滚动快门问题 |

## 性能提示

- **全帧分析** (`sample_rate=1`): 最准确，但速度慢（适合短视频 < 1分钟）
- **采样分析** (`sample_rate=5`): 速度快5倍，精度略降（适合长视频）
- **光流计算**: 是最耗时的部分，采样可以有效加快速度

## 注意事项

1. 光流分析需要视频中有明显的运动才能准确计算
2. 对于静态或几乎静态的视频，运动连续性指标可能不准确
3. Wobble检测对于大范围运动的效果更好
4. 重复帧检测对场景切换可能产生误报

## 与其他功能的区别

- **基础FPS分析**: 只显示整体帧率
- **FPS动态分析**: 按秒分析FPS变化
- **帧动态分析**: 分析亮度、对比度、基础运动强度
- **运动质量分析** ⭐: 深入分析运动质量问题（4个专业指标）

运动质量分析是最全面的视频质量检测功能，适合需要检测视频生成质量、编码质量等场景。
