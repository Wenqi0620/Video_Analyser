# VMAF安装问题解决方案

## 问题说明

VMAF **不能通过 `pip install vmaf` 直接安装**，因为：
1. VMAF不在PyPI上，需要从源码编译安装
2. VMAF依赖FFmpeg和C++编译环境
3. 安装过程复杂，需要编译C++代码

---

## 解决方案

### 方案1：使用FFmpeg调用VMAF（推荐，最简单）

**优点：**
- ✅ 不需要安装Python包
- ✅ 只需要安装FFmpeg（通常系统已有）
- ✅ 可以直接调用VMAF功能
- ✅ 适合生产环境

**安装FFmpeg（如果还没有）：**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载
```

**使用FFmpeg计算VMAF：**
```bash
# 基本用法
ffmpeg -i reference.mp4 -i test.mp4 \
  -lavfi libvmaf="model_path=/path/to/vmaf/model/vmaf_v0.6.1.json" \
  -f null -

# 输出VMAF分数到文件
ffmpeg -i reference.mp4 -i test.mp4 \
  -lavfi libvmaf="model_path=/path/to/vmaf/model/vmaf_v0.6.1.json:log_path=vmaf_log.json:log_fmt=json" \
  -f null -
```

**Python封装（推荐）：**
```python
import subprocess
import json
import os
from pathlib import Path

def calculate_vmaf_ffmpeg(reference_video: str, test_video: str, 
                          model_path: str = None) -> dict:
    """
    使用FFmpeg计算VMAF分数
    
    Args:
        reference_video: 参考视频路径
        test_video: 测试视频路径
        model_path: VMAF模型路径（可选，使用默认模型）
    
    Returns:
        包含VMAF分数的字典
    """
    # 检查FFmpeg是否安装
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "FFmpeg未安装。请安装FFmpeg:\n"
            "macOS: brew install ffmpeg\n"
            "Ubuntu: sudo apt-get install ffmpeg"
        )
    
    # 创建临时日志文件
    log_file = Path('vmaf_temp_log.json')
    
    # 构建FFmpeg命令
    cmd = [
        'ffmpeg',
        '-i', reference_video,
        '-i', test_video,
        '-lavfi', f'libvmaf=log_path={log_file}:log_fmt=json',
        '-f', 'null',
        '-'
    ]
    
    try:
        # 运行FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # 读取VMAF结果
        if log_file.exists():
            with open(log_file, 'r') as f:
                vmaf_data = json.load(f)
            
            # 提取VMAF分数
            frames = vmaf_data.get('frames', [])
            if frames:
                vmaf_scores = [f['metrics']['vmaf'] for f in frames]
                mean_vmaf = sum(vmaf_scores) / len(vmaf_scores)
                
                return {
                    'vmaf_score': float(mean_vmaf),
                    'min_vmaf': float(min(vmaf_scores)),
                    'max_vmaf': float(max(vmaf_scores)),
                    'frame_count': len(frames),
                    'method': 'FFmpeg + libvmaf'
                }
            else:
                return {'error': '无法从日志中提取VMAF分数'}
        else:
            return {'error': 'VMAF日志文件未生成'}
    
    except subprocess.CalledProcessError as e:
        return {
            'error': f'FFmpeg执行失败: {e.stderr}',
            'method': 'FFmpeg + libvmaf'
        }
    finally:
        # 清理临时文件
        if log_file.exists():
            log_file.unlink(missing_ok=True)
```

---

### 方案2：从源码安装VMAF（复杂，不推荐）

**步骤：**
```bash
# 1. 克隆VMAF仓库
git clone https://github.com/Netflix/vmaf.git
cd vmaf

# 2. 安装依赖
pip install -r python/requirements.txt

# 3. 编译和安装
make
cd python
python setup.py install
```

**问题：**
- ❌ 需要C++编译环境
- ❌ 依赖复杂
- ❌ 可能遇到各种编译错误
- ❌ 不适合快速部署

---

### 方案3：使用Docker（适合服务器环境）

```bash
# 拉取VMAF Docker镜像
docker pull vmaf/vmaf

# 运行VMAF容器
docker run --rm -v $(pwd):/videos vmaf/vmaf \
  ffmpeg -i /videos/reference.mp4 -i /videos/test.mp4 \
  -lavfi libvmaf -f null -
```

---

## 推荐替代方案（可以直接pip install）

既然VMAF安装困难，以下是**可以直接pip install**的替代框架：

### 1. **LPIPS** ⭐⭐⭐⭐⭐（最推荐）

```bash
pip install lpips
```

**优点：**
- ✅ 直接pip install，无需额外配置
- ✅ 感知相似度评估，比传统指标更准确
- ✅ 无需参考视频，可以评估单个视频

### 2. **IQA-PyTorch** ⭐⭐⭐⭐⭐（最全面）

```bash
pip install pyiqa
```

**优点：**
- ✅ 包含多种质量评估指标
- ✅ 统一API，易于使用
- ✅ 支持GPU加速

### 3. **使用FFmpeg + Python封装**（推荐）

创建一个Python模块来调用FFmpeg的VMAF功能：

```python
# vmaf_wrapper.py
import subprocess
import json
from pathlib import Path

class VMAFCalculator:
    """VMAF计算器（通过FFmpeg）"""
    
    def __init__(self):
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """检查FFmpeg是否安装"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                          capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg未安装。请安装FFmpeg:\n"
                "macOS: brew install ffmpeg\n"
                "Ubuntu: sudo apt-get install ffmpeg"
            )
    
    def calculate(self, reference_video: str, test_video: str) -> dict:
        """计算VMAF分数"""
        # 实现代码（见上面的示例）
        pass
```

---

## 集成到Video-Eval项目

### 方案A：使用FFmpeg封装（推荐）

在`video_analyzer.py`中添加：

```python
def analyze_with_vmaf_ffmpeg(self, reference_video: str) -> Dict:
    """
    使用FFmpeg计算VMAF分数
    
    Args:
        reference_video: 参考视频路径
    
    Returns:
        包含VMAF分数的字典
    """
    import subprocess
    import json
    from pathlib import Path
    
    # 检查FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError(
            "FFmpeg未安装。VMAF需要FFmpeg支持。\n"
            "macOS: brew install ffmpeg\n"
            "Ubuntu: sudo apt-get install ffmpeg"
        )
    
    log_file = Path('vmaf_temp_log.json')
    
    cmd = [
        'ffmpeg',
        '-i', str(Path(reference_video)),
        '-i', str(self.video_path),
        '-lavfi', f'libvmaf=log_path={log_file}:log_fmt=json',
        '-f', 'null', '-'
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                vmaf_data = json.load(f)
            
            frames = vmaf_data.get('frames', [])
            if frames:
                vmaf_scores = [f['metrics']['vmaf'] for f in frames]
                mean_vmaf = sum(vmaf_scores) / len(vmaf_scores)
                
                return {
                    'vmaf_score': float(mean_vmaf),
                    'min_vmaf': float(min(vmaf_scores)),
                    'max_vmaf': float(max(vmaf_scores)),
                    'frame_count': len(frames),
                    'method': 'FFmpeg + libvmaf'
                }
    finally:
        if log_file.exists():
            log_file.unlink(missing_ok=True)
    
    return {'error': 'VMAF计算失败'}
```

### 方案B：使用LPIPS替代（最简单）

如果不需要VMAF，可以直接使用LPIPS：

```python
def analyze_with_lpips(self) -> Dict:
    """使用LPIPS评估视频质量（无需参考视频）"""
    try:
        import lpips
        # 实现LPIPS评估
        # ... (参考之前的文档)
    except ImportError:
        raise ImportError("请安装LPIPS: pip install lpips")
```

---

## 快速解决方案总结

### 如果你需要VMAF：

1. **安装FFmpeg**（如果还没有）：
   ```bash
   brew install ffmpeg  # macOS
   ```

2. **使用FFmpeg调用VMAF**（见上面的Python封装代码）

### 如果你不需要VMAF：

**直接使用LPIPS**（推荐）：
```bash
pip install lpips
```

LPIPS的优势：
- ✅ 直接pip install
- ✅ 无需参考视频
- ✅ 感知相似度评估，准确性高
- ✅ 适合AI生成视频评估

---

## 测试FFmpeg是否支持VMAF

```bash
# 检查FFmpeg是否支持libvmaf
ffmpeg -filters | grep vmaf

# 如果输出包含vmaf，说明支持
# 如果不支持，需要重新编译FFmpeg（包含libvmaf）
```

---

## 最终推荐

**对于你的项目，我推荐：**

1. **优先使用LPIPS** - 最简单，直接pip install
2. **如果需要VMAF** - 使用FFmpeg封装（需要先安装FFmpeg）
3. **综合评估** - 使用IQA-PyTorch（包含多种指标）

**安装命令：**
```bash
# 最推荐的组合
pip install lpips pyiqa

# 如果需要VMAF，先安装FFmpeg
brew install ffmpeg  # macOS
```

---

**创建时间**：2025-01-XX
**最后更新**：2025-01-XX

