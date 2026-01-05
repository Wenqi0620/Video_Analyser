# 快速开始指南

## ✅ 你的虚拟环境已准备就绪！

你的虚拟环境位于：`.venv/`，pip 已安装（版本 25.3）

## 📦 安装依赖

### 方法1：直接使用虚拟环境的 pip（推荐）

在终端运行：

```bash
cd /Users/yanwenqi/Desktop/Video-Eval
.venv/bin/pip install opencv-python numpy
```

或者：

```bash
.venv/bin/python -m pip install opencv-python numpy
```

**注意**: 使用 `pip` 而不是 `pip3`（在虚拟环境中）

### 方法2：激活虚拟环境后安装

```bash
cd /Users/yanwenqi/Desktop/Video-Eval
source .venv/bin/activate
pip install opencv-python numpy
```

### 方法3：如果网络有问题，使用国内镜像

```bash
.venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-python numpy
```

## 🚀 使用工具

安装完成后，运行：

```bash
# 使用虚拟环境的 Python
.venv/bin/python video_analyzer.py <你的视频文件路径>

# 或者激活虚拟环境后
source .venv/bin/activate
python video_analyzer.py <你的视频文件路径>
```

## 📝 示例

假设你有一个视频文件 `test.mp4`：

```bash
.venv/bin/python video_analyzer.py test.mp4
```

## ❓ 常见问题

### Q: 为什么不能用 `-m pip3`？
A: `pip3` 是一个命令行工具，不是 Python 模块。正确用法是：
- `python -m pip` ✅
- `python -m pip3` ❌

### Q: 没有安装 Homebrew (brew) 怎么办？
A: 不需要 brew，直接用 pip 安装 OpenCV 即可。如果需要 ffmpeg，可以：
1. 安装 Homebrew: 访问 https://brew.sh
2. 或直接使用 OpenCV（已足够）

## ✨ 验证安装

运行以下命令检查是否安装成功：

```bash
.venv/bin/python -c "import cv2; print('OpenCV版本:', cv2.__version__)"
```

如果显示版本号，说明安装成功！
