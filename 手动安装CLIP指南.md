# 手动安装CLIP指南

由于网络权限限制，无法自动安装CLIP。请按照以下步骤手动安装：

## 方法1：使用pip安装（推荐）

在终端中运行以下命令：

```bash
cd /Users/yanwenqi/Desktop/Video-Eval

# 激活虚拟环境
source .venv/bin/activate

# 安装CLIP依赖
pip install ftfy regex tqdm

# 安装CLIP
pip install git+https://github.com/openai/CLIP.git
```

如果遇到SSL证书问题，可以：

```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ftfy regex tqdm
pip install git+https://github.com/openai/CLIP.git
```

## 方法2：手动克隆和安装

```bash
cd /Users/yanwenqi/Desktop/Video-Eval

# 克隆CLIP仓库
git clone https://github.com/openai/CLIP.git
cd CLIP

# 安装依赖
pip install ftfy regex tqdm

# 安装CLIP
pip install -e .
```

## 方法3：如果不需要CLIP功能

如果你不需要CLIPScore功能，可以：

1. **使用LPIPS替代**（推荐）：
   ```bash
   pip install lpips
   ```
   LPIPS可以直接pip install，无需编译。

2. **使用IQA-PyTorch**：
   ```bash
   pip install pyiqa
   ```

## 验证安装

安装完成后，运行：

```bash
python test_clipscore.py
```

如果显示"✓ CLIP已安装"，说明安装成功。

## 如果仍然遇到问题

### SSL证书问题

```bash
# 临时禁用SSL验证（不推荐，但可以解决证书问题）
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org git+https://github.com/openai/CLIP.git
```

### 网络问题

使用国内镜像：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ftfy regex tqdm
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple git+https://github.com/openai/CLIP.git
```

### 权限问题

如果遇到权限问题，使用用户安装：

```bash
pip install --user git+https://github.com/openai/CLIP.git
```

## 测试CLIPScore

安装完成后，可以测试：

```bash
# 测试依赖
python test_clipscore.py

# 运行CLIPScore（如果有示例视频）
python clipscore_simple.py "Video Example/01_即梦_flowers blooming from the ground, movie, cinematic, documentary, uhd_2024-08-06 21_54_21.mp4" "flowers blooming from the ground"
```

