# FPS动态变化分析功能使用指南

## 功能说明

新增的FPS动态分析功能可以：
- **按秒测量FPS** - 统计每一秒实际包含的帧数（即该秒的实际FPS）
- **可视化展示** - 生成FPS随时间变化的图表和分布直方图
- **统计信息** - 提供平均FPS、中位数、标准差、最大值、最小值等统计

## 快速开始

### 基础使用

```bash
# 分析FPS动态变化并自动生成图表（保存为 fps_dynamics.png）
.venv/bin/python video_analyzer.py "视频路径.mp4" --fps-dynamics

# 指定输出文件名
.venv/bin/python video_analyzer.py "视频路径.mp4" --fps-dynamics my_fps_chart.png
```

### 输出说明

**终端输出包含：**
- 视频基本信息（声明帧率、总帧数、时长等）
- 整体FPS统计（平均、中位数、标准差、范围）
- FPS稳定性指标
- 逐秒FPS统计（前30秒）

**图表输出包含：**
1. **FPS随时间变化图** - 显示每一秒的实际FPS，以及声明FPS和平均FPS的参考线
2. **FPS分布直方图** - 显示FPS值的分布情况

## Python API 使用

```python
from video_analyzer import VideoAnalyzer

# 创建分析器
analyzer = VideoAnalyzer("video.mp4")

# 分析FPS动态变化
result = analyzer.analyze_fps_dynamics()

# 打印结果
analyzer.print_fps_dynamics(result)

# 绘制图表
analyzer.plot_fps_dynamics(result, output_path="fps_chart.png")

# 访问数据
per_second_fps = result['per_second_fps']
overall_stats = result['overall_stats']

# 获取第5秒的FPS
if 5 in per_second_fps:
    print(f"第5秒的FPS: {per_second_fps[5]['fps']}")

# 获取整体统计
print(f"平均FPS: {overall_stats['mean_fps']}")
print(f"FPS范围: {overall_stats['min_fps']} - {overall_stats['max_fps']}")
```

## 数据格式

### 逐秒FPS数据 (per_second_fps)

```python
{
  0: {  # 第0秒
    'fps': 30.0,        # 这一秒的实际FPS（即帧数）
    'frame_count': 30   # 这一秒包含的帧数
  },
  1: {
    'fps': 29.0,
    'frame_count': 29
  },
  # ... 其他秒
}
```

### 整体统计 (overall_stats)

```python
{
  'declared_fps': 30.0,      # 视频声明的帧率
  'mean_fps': 29.8,          # 平均实际FPS
  'std_fps': 0.5,            # FPS标准差
  'min_fps': 28.0,           # 最小FPS
  'max_fps': 31.0,           # 最大FPS
  'median_fps': 30.0         # 中位数FPS
}
```

## 应用场景

1. **检测帧率波动** - 发现视频中FPS不稳定的时段
2. **验证视频质量** - 对比实际FPS和声明FPS的差异
3. **性能分析** - 分析视频编码或播放时的帧率稳定性
4. **视频处理优化** - 识别需要优化的时间段

## 注意事项

1. 每一秒的FPS = 该秒包含的帧数（因为每秒测量的就是帧数）
2. 如果视频声明30 FPS，理想情况下每秒应该有30帧
3. 实际FPS可能因为编码、丢帧等原因与声明FPS不同
4. 图表会自动保存为PNG格式，分辨率150 DPI

## 与其他功能的区别

- **基础分析** (`--fps`): 只显示视频的整体FPS
- **FPS动态分析** (`--fps-dynamics`): 按秒测量FPS并绘制变化图
- **帧动态分析** (`--dynamics`): 分析亮度、对比度、运动强度等

三者可以独立使用，互不干扰。
