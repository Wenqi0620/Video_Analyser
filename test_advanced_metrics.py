#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试最先进的视频质量评估框架
用于验证哪些框架可以直接调用
"""

import sys
from pathlib import Path

def test_imports():
    """测试所有库是否正确安装"""
    print("="*60)
    print("测试最先进的视频质量评估框架")
    print("="*60)
    
    frameworks = {
        'LPIPS': {
            'module': 'lpips',
            'description': '感知相似度评估（最推荐）',
            'install': 'pip install lpips',
            'priority': '⭐⭐⭐⭐⭐'
        },
        'VMAF (FFmpeg)': {
            'module': 'ffmpeg',
            'description': 'Netflix视频质量评估（通过FFmpeg）',
            'install': 'brew install ffmpeg (macOS) 或 sudo apt-get install ffmpeg (Ubuntu)',
            'priority': '⭐⭐⭐⭐⭐',
            'note': '注意: VMAF不能直接pip install，需要通过FFmpeg调用'
        },
        'IQA-PyTorch': {
            'module': 'pyiqa',
            'description': '综合图像质量评估工具箱',
            'install': 'pip install pyiqa',
            'priority': '⭐⭐⭐⭐⭐'
        },
        'CLIPScore': {
            'module': 'clipscore',
            'description': '语义一致性评估',
            'install': 'pip install clip-score',
            'priority': '⭐⭐⭐⭐'
        },
    }
    
    available = []
    unavailable = []
    
    for name, info in frameworks.items():
        try:
            __import__(info['module'])
            print(f"✓ {name:15} - {info['description']:30} {info['priority']}")
            available.append((name, info))
        except ImportError:
            print(f"✗ {name:15} - {info['description']:30} 未安装")
            print(f"  安装命令: {info['install']}")
            unavailable.append((name, info))
    
    print("\n" + "="*60)
    print("总结")
    print("="*60)
    print(f"✓ 可直接调用的框架: {len(available)}/{len(frameworks)}")
    print(f"✗ 需要安装的框架: {len(unavailable)}/{len(frameworks)}")
    
    if available:
        print("\n【推荐使用的框架】")
        for name, info in available:
            print(f"  • {name}: {info['description']}")
    
    if unavailable:
        print("\n【需要安装的框架】")
        print("一键安装命令:")
        install_cmds = [info['install'] for _, info in unavailable]
        print("  " + " && ".join(install_cmds))
    
    return available, unavailable


def test_lpips_simple():
    """测试LPIPS简单调用"""
    try:
        import lpips
        print("\n" + "="*60)
        print("测试LPIPS调用")
        print("="*60)
        
        # 初始化
        loss_fn = lpips.LPIPS(net='alex')
        print("✓ LPIPS模型初始化成功")
        
        # 创建测试数据
        import torch
        import numpy as np
        
        # 创建两个随机图像张量
        img0 = torch.randn(1, 3, 224, 224)
        img1 = torch.randn(1, 3, 224, 224)
        
        # 计算距离
        distance = loss_fn(img0, img1)
        print(f"✓ LPIPS计算成功: {distance.item():.4f}")
        print("  (值越小越相似，通常在0-1之间)")
        
        return True
    except ImportError:
        print("\n✗ LPIPS未安装，跳过测试")
        return False
    except Exception as e:
        print(f"\n✗ LPIPS测试失败: {e}")
        return False


def test_vmaf_simple():
    """测试VMAF简单调用（通过FFmpeg）"""
    try:
        import subprocess
        print("\n" + "="*60)
        print("测试VMAF调用（通过FFmpeg）")
        print("="*60)
        
        # 检查FFmpeg
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                check=True
            )
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg已安装: {version_line}")
            
            # 检查是否支持libvmaf
            result = subprocess.run(
                ['ffmpeg', '-filters'],
                capture_output=True,
                text=True,
                check=True
            )
            if 'vmaf' in result.stdout.lower():
                print("✓ FFmpeg支持libvmaf")
                print("  可以使用 vmaf_ffmpeg_wrapper.py 计算VMAF")
            else:
                print("⚠ FFmpeg可能不支持libvmaf")
                print("  如果计算失败，可能需要重新编译FFmpeg（包含libvmaf）")
            
            print("\n使用方法:")
            print("  from vmaf_ffmpeg_wrapper import calculate_vmaf")
            print("  result = calculate_vmaf('reference.mp4', 'test.mp4')")
            
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ FFmpeg未安装")
            print("  安装方法:")
            print("    macOS: brew install ffmpeg")
            print("    Ubuntu: sudo apt-get install ffmpeg")
            return False
    except Exception as e:
        print(f"\n✗ VMAF测试失败: {e}")
        return False


def test_pyiqa_simple():
    """测试IQA-PyTorch简单调用"""
    try:
        import pyiqa
        print("\n" + "="*60)
        print("测试IQA-PyTorch调用")
        print("="*60)
        
        # 测试创建指标
        import torch
        
        # 检查可用设备
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"✓ 使用设备: {device}")
        
        # 创建LPIPS指标
        lpips_metric = pyiqa.create_metric('lpips', device=device)
        print("✓ LPIPS指标创建成功")
        
        # 创建测试数据
        img1 = torch.randn(1, 3, 224, 224).to(device)
        img2 = torch.randn(1, 3, 224, 224).to(device)
        
        # 计算
        score = lpips_metric(img1, img2)
        print(f"✓ LPIPS计算成功: {score.item():.4f}")
        
        # 列出可用指标
        print("\n可用指标:")
        available_metrics = pyiqa.list_models()
        for metric in available_metrics[:10]:  # 只显示前10个
            print(f"  • {metric}")
        if len(available_metrics) > 10:
            print(f"  ... 共 {len(available_metrics)} 个指标")
        
        return True
    except ImportError:
        print("\n✗ IQA-PyTorch未安装，跳过测试")
        return False
    except Exception as e:
        print(f"\n✗ IQA-PyTorch测试失败: {e}")
        return False


def test_clipscore_simple():
    """测试CLIPScore简单调用"""
    try:
        from clipscore import clipscore
        print("\n" + "="*60)
        print("测试CLIPScore调用")
        print("="*60)
        
        print("✓ CLIPScore模块导入成功")
        print("  注意: CLIPScore需要图像和文本描述才能计算")
        print("  使用方法: clipscore.compute_clipscore(image_path, caption)")
        
        return True
    except ImportError:
        print("\n✗ CLIPScore未安装，跳过测试")
        return False
    except Exception as e:
        print(f"\n✗ CLIPScore测试失败: {e}")
        return False


def main():
    """主函数"""
    # 1. 测试导入
    available, unavailable = test_imports()
    
    # 2. 测试已安装的框架
    if available:
        print("\n" + "="*60)
        print("测试已安装框架的功能")
        print("="*60)
        
        for name, info in available:
            if name == 'LPIPS':
                test_lpips_simple()
            elif name == 'VMAF (FFmpeg)':
                test_vmaf_simple()
            elif name == 'IQA-PyTorch':
                test_pyiqa_simple()
            elif name == 'CLIPScore':
                test_clipscore_simple()
    
    # 3. 推荐安装命令
    print("\n" + "="*60)
    print("推荐安装命令（一键安装所有最先进的框架）")
    print("="*60)
    print("pip install lpips pyiqa clip-score")
    print("\n注意: VMAF不能直接pip install，需要通过FFmpeg调用")
    print("  安装FFmpeg: brew install ffmpeg (macOS) 或 sudo apt-get install ffmpeg (Ubuntu)")
    print("  然后使用: python vmaf_ffmpeg_wrapper.py reference.mp4 test.mp4")
    print("\n或者分别安装:")
    print("  pip install lpips      # 感知相似度评估（最推荐，可直接pip install）")
    print("  pip install pyiqa      # 综合图像质量评估工具箱（可直接pip install）")
    print("  pip install clip-score # 语义一致性评估（可直接pip install）")
    print("  brew install ffmpeg    # VMAF需要FFmpeg（macOS）")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == '__main__':
    main()

