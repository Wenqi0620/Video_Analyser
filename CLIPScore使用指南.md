# CLIPScore使用指南

## 当前状态

运行 `clipscore_simple.py` 需要以下依赖：
- ✅ OpenCV（用于视频处理）
- ✅ CLIP库（用于计算CLIPScore）

## 安装依赖

### 方法1：使用虚拟环境（推荐）

```bash
cd /Users/yanwenqi/Desktop/Video-Eval

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install opencv-python
pip install git+https://github.com/openai/CLIP.git
```

### 方法2：直接安装

```bash
# 安装OpenCV
pip install opencv-python

# 安装CLIP（需要先安装PyTorch）
pip install torch torchvision
pip install git+https://github.com/openai/CLIP.git
```

## 使用方法

### 1. 测试依赖是否安装

```bash
python test_clipscore.py
```

### 2. 计算图像的CLIPScore

```bash
python clipscore_simple.py image.jpg "a beautiful sunset"
```

### 3. 计算视频的CLIPScore

```bash
# 使用示例视频
python clipscore_simple.py "Video Example/01_即梦_flowers blooming from the ground, movie, cinematic, documentary, uhd_2024-08-06 21_54_21.mp4" "flowers blooming from the ground"
```

### 4. 在Python代码中使用

```python
from clipscore_simple import CLIPScoreCalculator

# 创建计算器
calculator = CLIPScoreCalculator()

# 计算图像CLIPScore
score = calculator.calculate_score('image.jpg', 'a beautiful sunset')
print(f"CLIPScore: {score:.4f}")

# 计算视频CLIPScore
result = calculator.calculate_video_clipscore(
    'video.mp4', 
    'flowers blooming from the ground'
)
print(f"平均CLIPScore: {result['mean_clipscore']:.4f}")
print(f"标准差: {result['std_clipscore']:.4f}")
```

## 示例视频

你的项目中有以下示例视频可以测试：

1. **花朵绽放视频**：
   ```bash
   python clipscore_simple.py "Video Example/01_即梦_flowers blooming from the ground, movie, cinematic, documentary, uhd_2024-08-06 21_54_21.mp4" "flowers blooming from the ground"
   ```

2. **绘画缩放视频**：
   ```bash
   python clipscore_simple.py "Video Example/02_即梦_zoom into a painting, uhd, k-consistent, smooth continuous, movie,cinematic,uhd_2024-08-06 21_47_43.mp4" "zoom into a painting"
   ```

3. **拳头击打视频**：
   ```bash
   python clipscore_simple.py "Video Example/03_即梦_fist smashing through the floor of an ancient ruin rubble and debris，fpv，uhd，k-consistent，smooth，con....mp4" "fist smashing through the floor"
   ```

## 常见问题

### Q: 安装CLIP时出错？

**A:** 如果遇到编译错误，可以：
1. 先安装PyTorch：`pip install torch torchvision`
2. 再安装CLIP：`pip install git+https://github.com/openai/CLIP.git`

### Q: 内存不足？

**A:** CLIP模型较大，如果内存不足：
1. 使用较小的模型：`CLIPScoreCalculator(model_name="ViT-B/32")`
2. 增加视频采样率：`calculate_video_clipscore(video_path, text, sample_rate=5)`

### Q: 运行速度慢？

**A:** 
1. 如果有GPU，CLIP会自动使用GPU加速
2. 增加采样率可以减少计算量
3. 只分析关键帧而不是所有帧

## 输出说明

CLIPScore分数范围：**-1 到 1**
- **接近1**：图像/视频与文本描述高度匹配
- **接近0**：中等匹配
- **接近-1**：不匹配

对于视频，会输出：
- `mean_clipscore`: 平均分数
- `std_clipscore`: 标准差（分数波动）
- `min_clipscore`: 最低分数
- `max_clipscore`: 最高分数
- `median_clipscore`: 中位数分数

## 下一步

安装依赖后，运行：

```bash
# 1. 测试依赖
python test_clipscore.py

# 2. 运行CLIPScore
python clipscore_simple.py "Video Example/01_即梦_flowers blooming from the ground, movie, cinematic, documentary, uhd_2024-08-06 21_54_21.mp4" "flowers blooming from the ground"
```

