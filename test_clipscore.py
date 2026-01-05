#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CLIPScore功能
"""

import sys
from pathlib import Path

def test_clip_installation():
    """测试CLIP是否安装"""
    print("="*60)
    print("检查CLIP安装状态")
    print("="*60)
    
    try:
        import torch
        print(f"✓ PyTorch已安装: {torch.__version__}")
    except ImportError:
        print("✗ PyTorch未安装")
        print("  安装: pip install torch torchvision")
        return False
    
    try:
        import clip
        print("✓ CLIP已安装")
        return True
    except ImportError:
        print("✗ CLIP未安装")
        print("\n安装方法:")
        print("  pip install git+https://github.com/openai/CLIP.git")
        print("\n或者:")
        print("  pip install torch torchvision")
        print("  pip install ftfy regex tqdm")
        print("  pip install git+https://github.com/openai/CLIP.git")
        return False

def test_opencv():
    """测试OpenCV是否安装"""
    try:
        import cv2
        print(f"✓ OpenCV已安装: {cv2.__version__}")
        return True
    except ImportError:
        print("✗ OpenCV未安装")
        print("  安装: pip install opencv-python")
        return False

def demo_usage():
    """演示使用方法"""
    print("\n" + "="*60)
    print("CLIPScore使用示例")
    print("="*60)
    
    print("\n1. 计算图像的CLIPScore:")
    print("   python clipscore_simple.py image.jpg 'a beautiful sunset'")
    
    print("\n2. 计算视频的CLIPScore:")
    print("   python clipscore_simple.py video.mp4 'flowers blooming from the ground'")
    
    print("\n3. 在Python代码中使用:")
    print("""
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
""")

def test_with_example():
    """如果有示例文件，尝试运行"""
    video_example_dir = Path("Video Example")
    if not video_example_dir.exists():
        print("\n未找到示例视频目录")
        return
    
    # 找一个示例视频
    video_files = list(video_example_dir.glob("*.mp4"))
    if not video_files:
        print("\n未找到示例视频文件")
        return
    
    example_video = video_files[0]
    print(f"\n找到示例视频: {example_video.name}")
    print(f"可以使用以下命令测试:")
    print(f"  python clipscore_simple.py '{example_video}' 'flowers blooming'")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("CLIPScore测试工具")
    print("="*60)
    
    # 检查依赖
    opencv_ok = test_opencv()
    clip_ok = test_clip_installation()
    
    print("\n" + "="*60)
    print("依赖检查结果")
    print("="*60)
    
    if opencv_ok and clip_ok:
        print("\n✓ 所有依赖已安装，可以运行CLIPScore!")
        
        # 尝试运行一个简单测试
        try:
            from clipscore_simple import CLIPScoreCalculator
            print("\n正在测试CLIPScore计算器...")
            calculator = CLIPScoreCalculator()
            print("✓ CLIPScore计算器初始化成功!")
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
    else:
        print("\n✗ 缺少依赖，请先安装")
        print("\n推荐安装命令:")
        print("  pip install opencv-python")
        print("  pip install git+https://github.com/openai/CLIP.git")
    
    # 演示用法
    demo_usage()
    
    # 测试示例
    test_with_example()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == '__main__':
    main()

