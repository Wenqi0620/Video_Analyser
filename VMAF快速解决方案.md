# VMAF快速解决方案

## 问题
❌ `pip install vmaf` **无法安装** - VMAF不在PyPI上

## 解决方案

### ✅ 方案1：使用FFmpeg调用VMAF（推荐）

**步骤：**

1. **安装FFmpeg**（如果还没有）：
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   ```

2. **使用提供的封装模块**：
   ```python
   from vmaf_ffmpeg_wrapper import calculate_vmaf
   
   result = calculate_vmaf('reference.mp4', 'test.mp4')
   print(f"VMAF分数: {result['vmaf_score']:.4f}")
   ```

3. **或直接使用命令行**：
   ```bash
   python vmaf_ffmpeg_wrapper.py reference.mp4 test.mp4
   ```

**优点：**
- ✅ 不需要安装Python包
- ✅ 只需要FFmpeg（通常系统已有）
- ✅ 使用简单

---

### ✅ 方案2：使用LPIPS替代（最简单）

如果不需要VMAF，**直接使用LPIPS**：

```bash
pip install lpips
```

```python
import lpips

loss_fn = lpips.LPIPS()
# 计算感知相似度
distance = loss_fn(img0, img1)
```

**优点：**
- ✅ 直接pip install
- ✅ 无需参考视频
- ✅ 感知相似度评估，准确性高

---

## 推荐方案对比

| 方案 | 安装难度 | 使用难度 | 推荐度 |
|------|----------|----------|--------|
| **FFmpeg + VMAF封装** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **LPIPS** | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ |

---

## 快速开始

### 如果你想用VMAF：

```bash
# 1. 安装FFmpeg
brew install ffmpeg  # macOS

# 2. 使用封装模块
python vmaf_ffmpeg_wrapper.py reference.mp4 test.mp4
```

### 如果你不需要VMAF：

```bash
# 直接安装LPIPS（推荐）
pip install lpips
```

---

## 文件说明

- `vmaf_ffmpeg_wrapper.py` - VMAF的FFmpeg封装模块
- `VMAF安装问题解决方案.md` - 详细解决方案文档

---

**总结：VMAF不能pip install，但可以通过FFmpeg调用，或使用LPIPS替代。**

