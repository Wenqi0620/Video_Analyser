#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析视频并生成Excel报告
"""

import os
import sys
import csv
from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime

# 导入分析器
from video_analyzer import VideoAnalyzer

# Excel支持
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("警告: pandas未安装，无法生成Excel。请安装: pip install pandas openpyxl", file=sys.stderr)

# 模型名称映射（从文件名识别）
MODEL_KEYWORDS = {
    '即梦': ['jimeng', 'jim', '即梦'],
    '可灵': ['kling', '可灵', 'keling'],
    'Gen-2': ['gen2', 'gen-2', 'runway'],
    'PixVerse': ['pixverse', 'pix'],
    'Pika': ['pika'],
    'Haiper': ['haiper', 'hiper']
}


def detect_model_from_filename(filename: str) -> str:
    """从文件名检测模型类型"""
    filename_lower = filename.lower()
    for model, keywords in MODEL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in filename_lower:
                return model
    return '未知'


def analyze_video(video_path: Path) -> Dict:
    """分析单个视频的所有指标"""
    print(f"\n{'='*80}")
    print(f"正在分析: {video_path.name}")
    print(f"{'='*80}")
    
    try:
        analyzer = VideoAnalyzer(str(video_path))
        
        # 1. 基础分析
        print("\n[1/4] 基础分析...")
        basic_result = analyzer.analyze()
        
        # 2. FPS动态分析
        print("\n[2/4] FPS动态分析...")
        fps_result = analyzer.analyze_fps_dynamics()
        
        # 3. 帧动态分析（使用采样加快速度）
        print("\n[3/4] 帧动态分析...")
        dynamics_result = analyzer.analyze_frame_dynamics(sample_rate=5)
        
        # 4. 运动质量分析（使用采样加快速度）
        print("\n[4/4] 运动质量分析...")
        motion_result = analyzer.analyze_motion_quality(sample_rate=5)
        
        # 综合评分计算
        score = calculate_overall_score(basic_result, fps_result, dynamics_result, motion_result)
        
        return {
            'filename': video_path.name,
            'filepath': str(video_path),
            'model': detect_model_from_filename(video_path.name),
            'basic': basic_result,
            'fps_dynamics': fps_result,
            'frame_dynamics': dynamics_result,
            'motion_quality': motion_result,
            'overall_score': score
        }
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            'filename': video_path.name,
            'filepath': str(video_path),
            'model': detect_model_from_filename(video_path.name),
            'error': str(e)
        }


def calculate_overall_score(basic: Dict, fps: Dict, dynamics: Dict, motion: Dict) -> Dict:
    """计算综合评分"""
    scores = {}
    
    # 1. FPS稳定性评分 (0-25分)
    if 'overall_stats' in fps:
        fps_stats = fps['overall_stats']
        cv = (fps_stats.get('std_fps', 0) / fps_stats.get('mean_fps', 1) * 100) if fps_stats.get('mean_fps', 0) > 0 else 100
        fps_stability_score = max(0, 25 - cv * 0.5)  # CV越小分数越高
        scores['fps_stability'] = round(fps_stability_score, 2)
    else:
        scores['fps_stability'] = 0
    
    # 2. 时间戳抖动评分 (0-15分)
    if 'effective_fps_pts_jitter' in motion:
        pts_data = motion['effective_fps_pts_jitter']
        jitter_pct = pts_data.get('jitter_percentage', 100)
        pts_score = max(0, 15 - jitter_pct * 0.3)  # 抖动越小分数越高
        scores['pts_jitter'] = round(pts_score, 2)
    else:
        scores['pts_jitter'] = 0
    
    # 3. 重复帧评分 (0-15分)
    if 'duplicate_frame_ratio' in motion:
        dup_data = motion['duplicate_frame_ratio']
        dup_ratio = dup_data.get('total_duplicate_ratio', 1.0) * 100
        dup_score = max(0, 15 - dup_ratio * 3)  # 重复率越低分数越高
        scores['duplicate_frames'] = round(dup_score, 2)
    else:
        scores['duplicate_frames'] = 0
    
    # 4. 运动连续性评分 (0-25分)
    if 'motion_continuity' in motion:
        motion_data = motion['motion_continuity']
        continuity_score = motion_data.get('motion_continuity_score', 0) * 0.25  # 转换为25分制
        scores['motion_continuity'] = round(continuity_score, 2)
    else:
        scores['motion_continuity'] = 0
    
    # 5. 果冻效应评分 (0-10分)
    if 'wobble_distortion' in motion:
        wobble_data = motion['wobble_distortion']
        wobble_score_val = wobble_data.get('wobble_distortion_score', 100)
        wobble_score = max(0, 10 - wobble_score_val * 0.1)  # 失真越小分数越高
        scores['wobble'] = round(wobble_score, 2)
    else:
        scores['wobble'] = 0
    
    # 6. 视频质量基础分 (0-10分) - 基于分辨率和文件大小
    if 'resolution' in basic:
        width = basic['resolution'].get('width', 0)
        height = basic['resolution'].get('height', 0)
        # 分辨率评分：720p=5分, 1080p=8分, 4K=10分
        if width >= 3840 or height >= 2160:
            res_score = 10
        elif width >= 1920 or height >= 1080:
            res_score = 8
        elif width >= 1280 or height >= 720:
            res_score = 5
        else:
            res_score = 3
        scores['quality'] = res_score
    else:
        scores['quality'] = 0
    
    # 总分
    total_score = sum(scores.values())
    scores['total'] = round(total_score, 2)
    
    # 评级
    if total_score >= 90:
        scores['grade'] = '优秀'
    elif total_score >= 80:
        scores['grade'] = '良好'
    elif total_score >= 70:
        scores['grade'] = '一般'
    elif total_score >= 60:
        scores['grade'] = '较差'
    else:
        scores['grade'] = '很差'
    
    return scores


def create_csv_report(results: List[Dict], output_path: str):
    """创建CSV报告（不依赖pandas）"""
    
    if not results:
        return
    
    # 准备表头
    headers = [
        '文件名', '模型', '文件路径',
        '声明帧率(FPS)', '总帧数', '时长(秒)', '分辨率', '文件大小(MB)',
        '平均实际FPS', 'FPS标准差', 'FPS最小值', 'FPS最大值', 'FPS中位数', '变异系数(CV%)',
        '有效FPS', 'PTS抖动标准差(ms)', 'PTS最大抖动(ms)', '抖动百分比(%)',
        '完全重复帧数', '近似重复帧数', '总重复率(%)',
        '平均亮度', '亮度标准差', '平均对比度', '平均运动强度',
        '运动连续性分数', 'Jerkiness分数', 'Jerk尖峰比例(%)',
        'Wobble失真分数', '平均Wobble分数',
        'FPS稳定性评分', '时间戳抖动评分', '重复帧评分', '运动连续性评分', '果冻效应评分', '视频质量评分',
        '总分', '评级'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for result in results:
            if 'error' in result:
                row = [result['filename'], result['model'], result['filepath'], '分析失败', result.get('error', '')]
                row.extend([''] * (len(headers) - len(row)))
                writer.writerow(row)
                continue
            
            basic = result.get('basic', {})
            fps = result.get('fps_dynamics', {})
            dynamics = result.get('frame_dynamics', {})
            motion = result.get('motion_quality', {})
            scores = result.get('overall_score', {})
            
            fps_stats = fps.get('overall_stats', {})
            pts_data = motion.get('effective_fps_pts_jitter', {})
            dup_data = motion.get('duplicate_frame_ratio', {})
            motion_data = motion.get('motion_continuity', {})
            wobble_data = motion.get('wobble_distortion', {})
            dynamics_stats = dynamics.get('overall_stats', {})
            
            row = [
                result['filename'],
                result['model'],
                result['filepath'],
                basic.get('fps', 0),
                basic.get('frame_count', 0),
                round(basic.get('duration_seconds', 0), 2),
                f"{basic.get('resolution', {}).get('width', 0)}x{basic.get('resolution', {}).get('height', 0)}",
                round(basic.get('file_size_mb', 0), 2),
                round(fps_stats.get('mean_fps', 0), 3),
                round(fps_stats.get('std_fps', 0), 3),
                round(fps_stats.get('min_fps', 0), 3),
                round(fps_stats.get('max_fps', 0), 3),
                round(fps_stats.get('median_fps', 0), 3),
                round((fps_stats.get('std_fps', 0) / fps_stats.get('mean_fps', 1) * 100) if fps_stats.get('mean_fps', 0) > 0 else 0, 2),
                round(pts_data.get('effective_fps', 0), 3),
                round(pts_data.get('pts_jitter_std', 0) * 1000, 2),
                round(pts_data.get('pts_jitter_max', 0) * 1000, 2),
                round(pts_data.get('jitter_percentage', 0), 2),
                dup_data.get('duplicate_frame_count', 0),
                dup_data.get('near_duplicate_frame_count', 0),
                round(dup_data.get('total_duplicate_ratio', 0) * 100, 2),
                round(dynamics_stats.get('brightness', {}).get('mean', 0), 2),
                round(dynamics_stats.get('brightness', {}).get('std', 0), 2),
                round(dynamics_stats.get('contrast', {}).get('mean', 0), 2),
                round(dynamics_stats.get('motion', {}).get('mean_intensity', 0), 2),
                round(motion_data.get('motion_continuity_score', 0), 2),
                round(motion_data.get('jerkiness_score', 0), 2),
                round(motion_data.get('jerk_peak_ratio', 0) * 100, 2),
                round(wobble_data.get('wobble_distortion_score', 0), 2),
                round(wobble_data.get('mean_wobble_score', 0), 3),
                scores.get('fps_stability', 0),
                scores.get('pts_jitter', 0),
                scores.get('duplicate_frames', 0),
                scores.get('motion_continuity', 0),
                scores.get('wobble', 0),
                scores.get('quality', 0),
                scores.get('total', 0),
                scores.get('grade', ''),
            ]
            writer.writerow(row)
    
    print(f"✅ CSV报告已保存到: {output_path}")


def create_excel_report(results: List[Dict], output_path: str):
    """创建Excel报告"""
    if not PANDAS_AVAILABLE:
        # 如果没有pandas，使用CSV格式
        csv_path = output_path.replace('.xlsx', '.csv')
        create_csv_report(results, csv_path)
        print(f"\n提示: 如需Excel格式，请安装: pip install pandas openpyxl")
        return
    
    rows = []
    
    for result in results:
        if 'error' in result:
            rows.append({
                '文件名': result['filename'],
                '模型': result['model'],
                '状态': '分析失败',
                '错误': result['error'],
                **{f'指标_{i}': '' for i in range(20)}
            })
            continue
        
        basic = result.get('basic', {})
        fps = result.get('fps_dynamics', {})
        dynamics = result.get('frame_dynamics', {})
        motion = result.get('motion_quality', {})
        scores = result.get('overall_score', {})
        
        fps_stats = fps.get('overall_stats', {})
        pts_data = motion.get('effective_fps_pts_jitter', {})
        dup_data = motion.get('duplicate_frame_ratio', {})
        motion_data = motion.get('motion_continuity', {})
        wobble_data = motion.get('wobble_distortion', {})
        dynamics_stats = dynamics.get('overall_stats', {})
        
        row = {
            # 基本信息
            '文件名': result['filename'],
            '模型': result['model'],
            '文件路径': result['filepath'],
            
            # 基础分析
            '声明帧率(FPS)': basic.get('fps', 0),
            '总帧数': basic.get('frame_count', 0),
            '时长(秒)': round(basic.get('duration_seconds', 0), 2),
            '分辨率': f"{basic.get('resolution', {}).get('width', 0)}x{basic.get('resolution', {}).get('height', 0)}",
            '文件大小(MB)': round(basic.get('file_size_mb', 0), 2),
            
            # FPS动态分析
            '平均实际FPS': round(fps_stats.get('mean_fps', 0), 3),
            'FPS标准差': round(fps_stats.get('std_fps', 0), 3),
            'FPS最小值': round(fps_stats.get('min_fps', 0), 3),
            'FPS最大值': round(fps_stats.get('max_fps', 0), 3),
            'FPS中位数': round(fps_stats.get('median_fps', 0), 3),
            '变异系数(CV%)': round((fps_stats.get('std_fps', 0) / fps_stats.get('mean_fps', 1) * 100) if fps_stats.get('mean_fps', 0) > 0 else 0, 2),
            '异常值数量': 0,  # 需要从fps结果中提取
            
            # 时间戳抖动
            '有效FPS': round(pts_data.get('effective_fps', 0), 3),
            'PTS抖动标准差(ms)': round(pts_data.get('pts_jitter_std', 0) * 1000, 2),
            'PTS最大抖动(ms)': round(pts_data.get('pts_jitter_max', 0) * 1000, 2),
            '抖动百分比(%)': round(pts_data.get('jitter_percentage', 0), 2),
            
            # 重复帧
            '完全重复帧数': dup_data.get('duplicate_frame_count', 0),
            '近似重复帧数': dup_data.get('near_duplicate_frame_count', 0),
            '总重复率(%)': round(dup_data.get('total_duplicate_ratio', 0) * 100, 2),
            
            # 帧动态
            '平均亮度': round(dynamics_stats.get('brightness', {}).get('mean', 0), 2),
            '亮度标准差': round(dynamics_stats.get('brightness', {}).get('std', 0), 2),
            '平均对比度': round(dynamics_stats.get('contrast', {}).get('mean', 0), 2),
            '平均运动强度': round(dynamics_stats.get('motion', {}).get('mean_intensity', 0), 2),
            
            # 运动连续性
            '运动连续性分数': round(motion_data.get('motion_continuity_score', 0), 2),
            'Jerkiness分数': round(motion_data.get('jerkiness_score', 0), 2),
            'Jerk尖峰比例(%)': round(motion_data.get('jerk_peak_ratio', 0) * 100, 2),
            
            # 果冻效应
            'Wobble失真分数': round(wobble_data.get('wobble_distortion_score', 0), 2),
            '平均Wobble分数': round(wobble_data.get('mean_wobble_score', 0), 3),
            
            # 综合评分
            'FPS稳定性评分': scores.get('fps_stability', 0),
            '时间戳抖动评分': scores.get('pts_jitter', 0),
            '重复帧评分': scores.get('duplicate_frames', 0),
            '运动连续性评分': scores.get('motion_continuity', 0),
            '果冻效应评分': scores.get('wobble', 0),
            '视频质量评分': scores.get('quality', 0),
            '总分': scores.get('total', 0),
            '评级': scores.get('grade', ''),
        }
        
        rows.append(row)
    
    # 创建DataFrame
    df = pd.DataFrame(rows)
    
    # 按模型和总分排序
    df = df.sort_values(['模型', '总分'], ascending=[True, False])
    
    # 保存为Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # 主表：所有数据
        df.to_excel(writer, sheet_name='全部结果', index=False)
        
        # 按模型分组统计
        if '模型' in df.columns and '总分' in df.columns:
            summary_data = []
            for model in df['模型'].unique():
                model_df = df[df['模型'] == model]
                if len(model_df) > 0:
                    summary_data.append({
                        '模型': model,
                        '视频数量': len(model_df),
                        '平均总分': round(model_df['总分'].mean(), 2),
                        '最高分': round(model_df['总分'].max(), 2),
                        '最低分': round(model_df['总分'].min(), 2),
                        '平均FPS稳定性': round(model_df['FPS稳定性评分'].mean(), 2) if 'FPS稳定性评分' in model_df.columns else 0,
                        '平均运动连续性': round(model_df['运动连续性评分'].mean(), 2) if '运动连续性评分' in model_df.columns else 0,
                    })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df = summary_df.sort_values('平均总分', ascending=False)
            summary_df.to_excel(writer, sheet_name='模型统计', index=False)
    
    print(f"\n✅ Excel报告已保存到: {output_path}")


def main():
    """主函数"""
    # 使用脚本所在目录的 Video Example 子目录
    script_dir = Path(__file__).parent
    base_dir = script_dir / "Video Example"
    
    # 查找所有视频文件（只在当前目录，不递归）
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(base_dir.glob(f'*{ext}'))
        video_files.extend(base_dir.glob(f'*{ext.upper()}'))
    
    # 去重并排序
    video_files = sorted(set(video_files))
    
    if not video_files:
        print(f"在 {base_dir} 中未找到视频文件", file=sys.stderr)
        return
    
    print(f"找到 {len(video_files)} 个视频文件")
    print("开始批量分析...\n")
    print(f"预计需要较长时间，请耐心等待...\n")
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, video_path in enumerate(video_files, 1):
        print(f"\n{'='*80}")
        print(f"进度: {i}/{len(video_files)} - {video_path.name}")
        print(f"{'='*80}")
        try:
            result = analyze_video(video_path)
            results.append(result)
            success_count += 1
            if 'overall_score' in result:
                print(f"✅ 分析完成 - 总分: {result['overall_score'].get('total', 0):.2f} ({result['overall_score'].get('grade', '')})")
        except Exception as e:
            print(f"❌ 分析失败: {e}", file=sys.stderr)
            results.append({
                'filename': video_path.name,
                'filepath': str(video_path),
                'model': detect_model_from_filename(video_path.name),
                'error': str(e)
            })
            error_count += 1
    
    print(f"\n{'='*80}")
    print(f"批量分析完成!")
    print(f"成功: {success_count}, 失败: {error_count}, 总计: {len(video_files)}")
    print(f"{'='*80}\n")
    
    # 生成报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 总是生成CSV（兼容性最好，可用Excel打开）
    csv_path = base_dir / f"视频分析报告_{timestamp}.csv"
    try:
        create_csv_report(results, str(csv_path))
    except Exception as e:
        print(f"生成CSV失败: {e}", file=sys.stderr)
    
    # 如果有pandas，也生成Excel
    if PANDAS_AVAILABLE:
        excel_path = base_dir / f"视频分析报告_{timestamp}.xlsx"
        try:
            create_excel_report(results, str(excel_path))
        except Exception as e:
            print(f"生成Excel失败: {e}", file=sys.stderr)
    else:
        print(f"\n提示: CSV文件已生成（可用Excel打开）。如需原生Excel格式，请运行: pip install pandas openpyxl")
    
    # 也保存JSON备份
    json_path = base_dir / f"视频分析结果_{timestamp}.json"
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON备份已保存到: {json_path}")
    except Exception as e:
        print(f"保存JSON失败: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
