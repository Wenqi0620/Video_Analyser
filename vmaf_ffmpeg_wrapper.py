#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMAF计算器 - 通过FFmpeg调用VMAF
解决VMAF无法直接pip install的问题
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Optional
import tempfile


class VMAFCalculator:
    """VMAF计算器（通过FFmpeg）"""
    
    def __init__(self):
        """初始化VMAF计算器"""
        self._check_ffmpeg()
        self._check_libvmaf()
    
    def _check_ffmpeg(self):
        """检查FFmpeg是否安装"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                check=True
            )
            # 提取FFmpeg版本
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg已安装: {version_line}", file=sys.stderr)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg未安装。VMAF需要FFmpeg支持。\n"
                "安装方法:\n"
                "  macOS: brew install ffmpeg\n"
                "  Ubuntu: sudo apt-get install ffmpeg\n"
                "  Windows: 从 https://ffmpeg.org/download.html 下载"
            )
    
    def _check_libvmaf(self):
        """检查FFmpeg是否支持libvmaf"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-filters'],
                capture_output=True,
                text=True,
                check=True
            )
            if 'vmaf' in result.stdout.lower():
                print("✓ FFmpeg支持libvmaf", file=sys.stderr)
            else:
                print("⚠ 警告: FFmpeg可能不支持libvmaf", file=sys.stderr)
                print("  如果计算失败，可能需要重新编译FFmpeg（包含libvmaf）", file=sys.stderr)
        except Exception as e:
            print(f"⚠ 无法检查libvmaf支持: {e}", file=sys.stderr)
    
    def calculate(self, 
                  reference_video: str, 
                  test_video: str,
                  model_path: Optional[str] = None,
                  log_path: Optional[str] = None) -> Dict:
        """
        计算VMAF分数
        
        Args:
            reference_video: 参考视频路径
            test_video: 测试视频路径
            model_path: VMAF模型路径（可选，使用默认模型）
            log_path: 日志文件路径（可选，自动生成临时文件）
        
        Returns:
            包含VMAF分数的字典
        """
        reference_path = Path(reference_video)
        test_path = Path(test_video)
        
        if not reference_path.exists():
            raise FileNotFoundError(f"参考视频不存在: {reference_video}")
        if not test_path.exists():
            raise FileNotFoundError(f"测试视频不存在: {test_video}")
        
        # 创建临时日志文件
        if log_path is None:
            temp_log = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False
            )
            log_file = Path(temp_log.name)
            temp_log.close()
        else:
            log_file = Path(log_path)
        
        try:
            # 构建FFmpeg命令
            cmd = [
                'ffmpeg',
                '-i', str(reference_path),
                '-i', str(test_path),
                '-lavfi', f'libvmaf=log_path={log_file}:log_fmt=json',
                '-f', 'null',
                '-'
            ]
            
            # 如果指定了模型路径
            if model_path:
                cmd[4] = f'libvmaf=model_path={model_path}:log_path={log_file}:log_fmt=json'
            
            print(f"正在计算VMAF...", file=sys.stderr)
            print(f"  参考视频: {reference_path.name}", file=sys.stderr)
            print(f"  测试视频: {test_path.name}", file=sys.stderr)
            
            # 运行FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 读取VMAF结果
            if not log_file.exists():
                return {
                    'error': 'VMAF日志文件未生成',
                    'method': 'FFmpeg + libvmaf'
                }
            
            with open(log_file, 'r') as f:
                vmaf_data = json.load(f)
            
            # 提取VMAF分数
            frames = vmaf_data.get('frames', [])
            if not frames:
                return {
                    'error': '无法从日志中提取VMAF分数',
                    'method': 'FFmpeg + libvmaf',
                    'raw_data': vmaf_data
                }
            
            vmaf_scores = []
            for frame in frames:
                if 'metrics' in frame and 'vmaf' in frame['metrics']:
                    vmaf_scores.append(frame['metrics']['vmaf'])
            
            if not vmaf_scores:
                return {
                    'error': '无法提取VMAF分数',
                    'method': 'FFmpeg + libvmaf',
                    'raw_data': vmaf_data
                }
            
            # 计算统计信息
            mean_vmaf = sum(vmaf_scores) / len(vmaf_scores)
            
            return {
                'vmaf_score': float(mean_vmaf),
                'min_vmaf': float(min(vmaf_scores)),
                'max_vmaf': float(max(vmaf_scores)),
                'std_vmaf': float(
                    (sum((x - mean_vmaf) ** 2 for x in vmaf_scores) / len(vmaf_scores)) ** 0.5
                ),
                'frame_count': len(vmaf_scores),
                'method': 'FFmpeg + libvmaf',
                'reference_video': str(reference_path),
                'test_video': str(test_path)
            }
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            return {
                'error': f'FFmpeg执行失败: {error_msg}',
                'method': 'FFmpeg + libvmaf',
                'command': ' '.join(cmd)
            }
        except json.JSONDecodeError as e:
            return {
                'error': f'无法解析VMAF日志: {e}',
                'method': 'FFmpeg + libvmaf',
                'log_file': str(log_file)
            }
        except Exception as e:
            return {
                'error': f'计算VMAF时出错: {e}',
                'method': 'FFmpeg + libvmaf'
            }
        finally:
            # 清理临时文件
            if log_path is None and log_file.exists():
                try:
                    log_file.unlink()
                except:
                    pass


def calculate_vmaf(reference_video: str, test_video: str) -> Dict:
    """
    便捷函数：计算VMAF分数
    
    Args:
        reference_video: 参考视频路径
        test_video: 测试视频路径
    
    Returns:
        包含VMAF分数的字典
    """
    calculator = VMAFCalculator()
    return calculator.calculate(reference_video, test_video)


# 使用示例
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法: python vmaf_ffmpeg_wrapper.py <参考视频> <测试视频>")
        print("\n示例:")
        print("  python vmaf_ffmpeg_wrapper.py reference.mp4 test.mp4")
        sys.exit(1)
    
    reference_video = sys.argv[1]
    test_video = sys.argv[2]
    
    try:
        calculator = VMAFCalculator()
        result = calculator.calculate(reference_video, test_video)
        
        print("\n" + "="*60)
        print("VMAF计算结果")
        print("="*60)
        
        if 'error' in result:
            print(f"错误: {result['error']}")
        else:
            print(f"VMAF分数: {result['vmaf_score']:.4f}")
            print(f"最小值: {result['min_vmaf']:.4f}")
            print(f"最大值: {result['max_vmaf']:.4f}")
            print(f"标准差: {result['std_vmaf']:.4f}")
            print(f"帧数: {result['frame_count']}")
            print(f"方法: {result['method']}")
        
        print("="*60)
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

