#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
帧动态变化分析示例
"""

from video_analyzer import VideoAnalyzer
import json

def example_basic_dynamics():
    """基础动态分析示例"""
    print("=== 基础动态分析示例 ===\n")
    
    video_path = "/Users/yanwenqi/Desktop/Video-Eval/Video Example/31006_1731164792.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        
        # 分析帧动态变化（分析每一帧）
        print("正在分析帧动态变化...")
        result = analyzer.analyze_frame_dynamics(sample_rate=1)
        
        # 打印结果
        analyzer.print_frame_dynamics(result)
        
    except Exception as e:
        print(f"错误: {e}")


def example_sampled_dynamics():
    """采样分析示例（更快）"""
    print("\n=== 采样分析示例（每5帧分析一次）===\n")
    
    video_path = "/Users/yanwenqi/Desktop/Video-Eval/Video Example/31006_1731164792.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        
        # 每5帧分析一次（更快）
        result = analyzer.analyze_frame_dynamics(sample_rate=5)
        
        # 打印结果
        analyzer.print_frame_dynamics(result, sample_rate=5)
        
    except Exception as e:
        print(f"错误: {e}")


def example_with_plotting():
    """带可视化的分析示例"""
    print("\n=== 带可视化的分析示例 ===\n")
    
    video_path = "/Users/yanwenqi/Desktop/Video-Eval/Video Example/31006_1731164792.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        
        # 分析（使用采样加快速度）
        result = analyzer.analyze_frame_dynamics(sample_rate=2)
        
        # 绘制图表并保存
        analyzer.plot_frame_dynamics(result, output_path="frame_dynamics.png", sample_rate=2)
        
        print("图表已保存到 frame_dynamics.png")
        
    except Exception as e:
        print(f"错误: {e}")


def example_analyze_specific_seconds():
    """分析特定时间段"""
    print("\n=== 分析特定时间段 ===\n")
    
    video_path = "/Users/yanwenqi/Desktop/Video-Eval/Video Example/31006_1731164792.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        result = analyzer.analyze_frame_dynamics()
        
        per_second = result['per_second_stats']
        
        # 分析前5秒
        print("前5秒的统计:")
        for second in range(min(5, len(per_second))):
            if second in per_second:
                stats = per_second[second]
                print(f"\n第 {second} 秒:")
                print(f"  亮度: {stats['brightness']['mean']:.2f} "
                      f"(范围: {stats['brightness']['min']:.2f} - {stats['brightness']['max']:.2f})")
                print(f"  对比度: {stats['contrast']['mean']:.2f}")
                print(f"  运动强度: {stats['motion']['mean_intensity']:.2f}")
        
        # 找出运动最激烈的秒
        max_motion_second = max(per_second.keys(), 
                               key=lambda s: per_second[s]['motion']['mean_intensity'])
        print(f"\n运动最激烈的时刻: 第 {max_motion_second} 秒 "
              f"(强度: {per_second[max_motion_second]['motion']['mean_intensity']:.2f})")
        
    except Exception as e:
        print(f"错误: {e}")


def example_json_output():
    """JSON输出示例"""
    print("\n=== JSON输出示例 ===\n")
    
    video_path = "/Users/yanwenqi/Desktop/Video-Eval/Video Example/31006_1731164792.mp4"
    
    try:
        analyzer = VideoAnalyzer(video_path)
        
        # 快速分析（采样）
        result = analyzer.analyze_frame_dynamics(sample_rate=5)
        
        # 输出JSON（可以保存到文件）
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        
        # 保存到文件
        with open('dynamics_result.json', 'w', encoding='utf-8') as f:
            f.write(json_str)
        
        print("结果已保存到 dynamics_result.json")
        print("\n前100个字符:")
        print(json_str[:100] + "...")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    print("帧动态变化分析 - 使用示例")
    print("=" * 60)
    
    # 取消注释来运行不同的示例
    
    # example_basic_dynamics()
    # example_sampled_dynamics()
    # example_with_plotting()
    # example_analyze_specific_seconds()
    # example_json_output()
    
    print("\n请取消注释 example.py 中的示例函数来运行！")
    print("\n或者使用命令行:")
    print("  python video_analyzer.py video.mp4 --dynamics")
    print("  python video_analyzer.py video.mp4 --dynamics --plot")
