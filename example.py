#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例 - 演示如何使用VideoAnalyzer
"""

from video_analyzer import VideoAnalyzer
import json

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===\n")
    
    # 替换为你的视频文件路径
    video_path = "your_video.mp4"
    
    try:
        # 创建分析器
        analyzer = VideoAnalyzer(video_path)
        
        # 分析视频并打印结果
        result = analyzer.analyze()
        analyzer.print_analysis(result)
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("\n请确保视频文件路径正确！")
    except Exception as e:
        print(f"错误: {e}")


def example_get_specific_info():
    """获取特定信息的示例"""
    print("\n=== 获取特定信息示例 ===\n")
    
    video_path = "your_video.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        result = analyzer.analyze()
        
        # 只获取帧率
        fps = result['fps']
        print(f"视频帧率: {fps} FPS")
        
        # 只获取分辨率
        width = result['resolution']['width']
        height = result['resolution']['height']
        print(f"视频分辨率: {width}x{height}")
        
        # 判断视频质量
        if width >= 1920 and height >= 1080:
            quality = "1080p (Full HD) 或更高"
        elif width >= 1280 and height >= 720:
            quality = "720p (HD)"
        elif width >= 640:
            quality = "标清 (SD)"
        else:
            quality = "低清晰度"
        
        print(f"清晰度等级: {quality}")
        
        # 判断帧率
        if fps >= 60:
            frame_rate_category = "高帧率"
        elif fps >= 30:
            frame_rate_category = "标准帧率"
        elif fps >= 24:
            frame_rate_category = "电影帧率"
        else:
            frame_rate_category = "低帧率"
        
        print(f"帧率类别: {frame_rate_category}")
        
    except Exception as e:
        print(f"错误: {e}")


def example_json_output():
    """输出JSON格式的示例"""
    print("\n=== JSON输出示例 ===\n")
    
    video_path = "your_video.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        result = analyzer.analyze()
        
        # 输出为JSON格式
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        print(json_str)
        
    except Exception as e:
        print(f"错误: {e}")


def example_compare_methods():
    """比较不同方法的示例"""
    print("\n=== 方法比较示例 ===\n")
    
    video_path = "your_video.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        
        # 使用OpenCV
        print("使用OpenCV分析:")
        try:
            result_opencv = analyzer.analyze_with_opencv()
            print(f"  FPS: {result_opencv['fps']}")
            print(f"  分辨率: {result_opencv['resolution']['width']}x{result_opencv['resolution']['height']}")
        except Exception as e:
            print(f"  OpenCV分析失败: {e}")
        
        # 使用ffprobe
        print("\n使用ffprobe分析:")
        try:
            result_ffprobe = analyzer.analyze_with_ffprobe()
            print(f"  FPS: {result_ffprobe['fps']}")
            print(f"  分辨率: {result_ffprobe['resolution']['width']}x{result_ffprobe['resolution']['height']}")
            if 'codec' in result_ffprobe:
                print(f"  编解码器: {result_ffprobe['codec']}")
        except Exception as e:
            print(f"  ffprobe分析失败: {e}")
            
    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    print("视频分析工具 - 使用示例")
    print("=" * 60)
    print("\n注意: 请将示例中的 'your_video.mp4' 替换为实际的视频文件路径\n")
    
    # 取消注释下面的行来运行不同的示例
    
    # example_basic_usage()
    # example_get_specific_info()
    # example_json_output()
    # example_compare_methods()
    
    print("\n请取消注释example.py中的示例函数来运行！")
