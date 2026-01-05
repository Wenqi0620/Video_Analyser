#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的CLIPScore实现 - 使用官方CLIP库
避免编译filterpy和openai-clip的问题
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import cv2
import numpy as np

try:
    import torch
    import clip
    from PIL import Image
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    torch = None
    clip = None
    Image = None


class CLIPScoreCalculator:
    """CLIPScore计算器（使用官方CLIP库）"""
    
    def __init__(self, model_name: str = "ViT-B/32", device: Optional[str] = None):
        """
        初始化CLIPScore计算器
        
        Args:
            model_name: CLIP模型名称，可选: "ViT-B/32", "ViT-B/16", "ViT-L/14"
            device: 设备，'cuda' 或 'cpu'，如果为None则自动选择
        """
        if not CLIP_AVAILABLE:
            raise ImportError(
                "CLIP未安装。请安装:\n"
                "  pip install git+https://github.com/openai/CLIP.git\n"
                "  或: pip install torch torchvision"
            )
        
        # 选择设备
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"正在加载CLIP模型 ({model_name})...", file=sys.stderr)
        print(f"  设备: {self.device}", file=sys.stderr)
        
        # 加载CLIP模型
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        self.model.eval()
        
        print("✓ CLIP模型加载完成", file=sys.stderr)
    
    def calculate_score(self, image_path: str, text: str) -> float:
        """
        计算单个图像的CLIPScore
        
        Args:
            image_path: 图像路径
            text: 文本描述
        
        Returns:
            CLIPScore分数（0-1之间，越高越相似）
        """
        # 加载和预处理图像
        image = Image.open(image_path)
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # 编码文本
        text_tokens = clip.tokenize([text]).to(self.device)
        
        # 计算相似度
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            text_features = self.model.encode_text(text_tokens)
            
            # 归一化
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # 计算余弦相似度
            similarity = (image_features @ text_features.T).item()
        
        return float(similarity)
    
    def calculate_video_clipscore(self, 
                                  video_path: str, 
                                  text: str,
                                  sample_rate: int = 1) -> Dict:
        """
        计算视频的CLIPScore（逐帧评估）
        
        Args:
            video_path: 视频路径
            text: 文本描述
            sample_rate: 采样率，1表示每一帧，2表示每2帧一次
        
        Returns:
            包含CLIPScore统计信息的字典
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        scores = []
        frame_count = 0
        analyzed_count = 0
        
        print(f"正在计算视频CLIPScore...", file=sys.stderr)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 按采样率采样
                if frame_count % sample_rate != 0:
                    frame_count += 1
                    continue
                
                # 保存临时图像
                temp_path = f'temp_clipscore_frame_{frame_count}.jpg'
                cv2.imwrite(temp_path, frame)
                
                try:
                    # 计算CLIPScore
                    score = self.calculate_score(temp_path, text)
                    scores.append(score)
                    analyzed_count += 1
                finally:
                    # 清理临时文件
                    Path(temp_path).unlink(missing_ok=True)
                
                frame_count += 1
                
                if analyzed_count % 10 == 0:
                    print(f"  已分析 {analyzed_count} 帧", file=sys.stderr, end='\r')
            
            print("", file=sys.stderr)
            
            if not scores:
                return {'error': '无法计算CLIPScore，视频可能为空'}
            
            return {
                'mean_clipscore': float(np.mean(scores)),
                'std_clipscore': float(np.std(scores)),
                'min_clipscore': float(np.min(scores)),
                'max_clipscore': float(np.max(scores)),
                'median_clipscore': float(np.median(scores)),
                'frame_count': frame_count,
                'analyzed_frames': analyzed_count,
                'scores': scores[:50]  # 只保存前50个
            }
        finally:
            cap.release()


def calculate_clipscore(image_path: str, text: str, 
                      model_name: str = "ViT-B/32") -> float:
    """
    便捷函数：计算CLIPScore
    
    Args:
        image_path: 图像路径
        text: 文本描述
        model_name: CLIP模型名称
    
    Returns:
        CLIPScore分数
    """
    calculator = CLIPScoreCalculator(model_name=model_name)
    return calculator.calculate_score(image_path, text)


# 使用示例
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法: python clipscore_simple.py <图像/视频路径> <文本描述>")
        print("\n示例:")
        print("  python clipscore_simple.py image.jpg 'a beautiful sunset'")
        print("  python clipscore_simple.py video.mp4 'flowers blooming'")
        sys.exit(1)
    
    path = sys.argv[1]
    text = sys.argv[2]
    
    try:
        path_obj = Path(path)
        
        if path_obj.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            # 图像
            score = calculate_clipscore(path, text)
            print(f"\nCLIPScore: {score:.4f}")
        else:
            # 视频
            calculator = CLIPScoreCalculator()
            result = calculator.calculate_video_clipscore(path, text)
            
            print("\n" + "="*60)
            print("视频CLIPScore结果")
            print("="*60)
            
            if 'error' in result:
                print(f"错误: {result['error']}")
            else:
                print(f"平均CLIPScore: {result['mean_clipscore']:.4f}")
                print(f"标准差: {result['std_clipscore']:.4f}")
                print(f"最小值: {result['min_clipscore']:.4f}")
                print(f"最大值: {result['max_clipscore']:.4f}")
                print(f"中位数: {result['median_clipscore']:.4f}")
                print(f"总帧数: {result['frame_count']}")
                print(f"分析帧数: {result['analyzed_frames']}")
            print("="*60)
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

