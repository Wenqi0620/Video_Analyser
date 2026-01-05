# GitHub 仓库设置指南

## GitHub 描述（350字符以内）

推荐使用以下描述：

```
Comprehensive video quality analyzer for AI-generated videos. Analyzes FPS dynamics, motion continuity, duplicate frames, and wobble distortion. Batch processing with Excel/CSV reports.
```

**字符数**: 185/350 ✅

## 初始化 Git 仓库

如果还没有初始化 Git 仓库，运行以下命令：

```bash
cd /Users/yanwenqi/Desktop/Video-Eval/Video_analyzer

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: Video quality analyzer for AI-generated videos"

# 添加远程仓库（替换为你的GitHub仓库URL）
git remote add origin https://github.com/yourusername/video-quality-analyzer.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 项目结构

```
Video_analyzer/
├── video_analyzer.py          # 核心分析工具
├── batch_analyze.py           # 批量分析脚本
├── README.md                  # 项目说明
├── requirements.txt           # 基础依赖
├── requirements_advanced.txt # 高级功能依赖
├── Video Example/             # 示例视频（不包含在git中）
├── CLIP/                      # CLIP模型（部分文件）
└── ... (其他文件)
```

## 注意事项

1. **大文件**: 视频文件、模型文件、分析结果已添加到 `.gitignore`
2. **敏感信息**: 确保没有包含API密钥或敏感数据
3. **许可证**: 建议添加 LICENSE 文件
4. **示例**: Video Example 目录中的视频文件不会被提交

## 推荐的 GitHub Topics

建议添加以下标签：
- `video-analysis`
- `video-quality`
- `ai-generated-video`
- `fps-analysis`
- `opencv`
- `python`
- `video-processing`
- `motion-analysis`

