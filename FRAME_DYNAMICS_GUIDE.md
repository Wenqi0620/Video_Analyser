# 帧动态变化分析指南

## 功能说明

帧动态变化分析功能可以帮你研究视频中每一秒的帧变化情况，包括：

1. **帧间差异** - 相邻帧之间的像素差异，反映场景变化速度
2. **运动强度** - 量化视频中的运动程度
3. **亮度变化** - 视频亮度随时间的变化趋势
4. **对比度变化** - 对比度的动态变化

## 快速开始

### 1. 安装依赖

```bash
.venv/bin/pip install matplotlib
```

### 2. 基础使用

```bash
# 分析帧动态变化
.venv/bin/python video_analyzer.py "视频路径.mp4" --dynamics

# 分析并显示图表
.venv/bin/python video_analyzer.py "视频路径.mp4" --dynamics --plot

# 保存图表到文件
.venv/bin/python video_analyzer.py "视频路径.mp4" --dynamics --plot dynamics.png
```

### 3. 使用采样加快速度

对于长视频，可以每N帧分析一次：

```bash
# 每5帧分析一次（快5倍）
.venv/bin/python video_analyzer.py "视频路径.mp4" --dynamics --sample-rate 5 --plot
```

## 输出说明

### 终端输出

分析会显示：
- **整体统计**: 整个视频的亮度、对比度、运动强度统计
- **逐秒统计**: 每一秒的详细统计（显示前20秒）

### 图表输出

如果使用 `--plot`，会生成包含4个子图的图表：

1. **亮度变化图** - 显示亮度随时间的变化
2. **对比度变化图** - 显示对比度随时间的变化
3. **运动强度图** - 显示运动强度随时间的变化
4. **综合视图** - 将所有指标叠加在一个图中

## Python API 使用

```python
from video_analyzer import VideoAnalyzer

# 创建分析器
analyzer = VideoAnalyzer("video.mp4")

# 分析帧动态变化
result = analyzer.analyze_frame_dynamics(sample_rate=1)

# 打印结果
analyzer.print_frame_dynamics(result)

# 绘制图表
analyzer.plot_frame_dynamics(result, output_path="output.png")

# 访问数据
per_second = result['per_second_stats']
overall = result['overall_stats']

# 获取第5秒的数据
second_5 = per_second[5]
print(f"第5秒亮度: {second_5['brightness']['mean']}")
print(f"第5秒运动强度: {second_5['motion']['mean_intensity']}")

# 获取整体统计
print(f"平均亮度: {overall['brightness']['mean']}")
print(f"最大运动强度: {overall['motion']['max_intensity']}")
```

## 数据格式

### 逐秒统计 (per_second_stats)

```python
{
  0: {  # 第0秒
    'brightness': {
      'mean': 120.5,    # 平均亮度
      'std': 15.2,      # 亮度标准差
      'min': 80.0,      # 最小亮度
      'max': 200.0      # 最大亮度
    },
    'contrast': {
      'mean': 45.3,     # 平均对比度
      'std': 5.1,
      'min': 30.0,
      'max': 60.0
    },
    'motion': {
      'mean_intensity': 12.5,  # 平均运动强度
      'max_intensity': 45.0,   # 最大运动强度
      'mean_diff': 8.3,        # 平均帧差异
      'max_diff': 35.0         # 最大帧差异
    },
    'frame_count': 30  # 这一秒的帧数
  },
  # ... 其他秒
}
```

### 整体统计 (overall_stats)

```python
{
  'brightness': {
    'mean': 125.0,
    'std': 20.0,
    'min': 50.0,
    'max': 255.0
  },
  'contrast': {
    'mean': 48.0,
    'std': 8.0,
    'min': 20.0,
    'max': 100.0
  },
  'motion': {
    'mean_intensity': 15.0,
    'max_intensity': 80.0,
    'mean_diff': 10.0,
    'max_diff': 60.0
  }
}
```

## 应用场景

1. **视频质量评估** - 检测视频中是否有卡顿、闪烁等问题
2. **运动分析** - 识别运动最激烈的时刻
3. **亮度变化检测** - 检测场景切换或光照变化
4. **视频编辑辅助** - 找出需要剪辑的关键时刻
5. **内容分析** - 分析视频内容的动态特征

## 性能提示

- **短视频 (< 1分钟)**: 可以使用 `sample_rate=1` 分析每一帧
- **中等视频 (1-5分钟)**: 使用 `sample_rate=2-5` 加快分析
- **长视频 (> 5分钟)**: 使用 `sample_rate=5-10` 或更高

## 注意事项

1. 分析长视频可能需要较长时间
2. 使用采样（sample_rate > 1）可以加快速度，但会降低精度
3. 可视化功能需要 matplotlib，如果没有安装会提示错误
4. 内存使用取决于视频长度和分辨率
