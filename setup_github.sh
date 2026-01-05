#!/bin/bash

# GitHub 仓库初始化脚本

echo "🚀 开始初始化 Git 仓库..."

# 检查是否已初始化
if [ -d ".git" ]; then
    echo "⚠️  Git 仓库已存在"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 初始化 Git
git init

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: Video quality analyzer for AI-generated videos

- Comprehensive FPS dynamics analysis
- Frame dynamics and motion quality analysis
- Batch processing with Excel/CSV export
- Support for multiple AI video models"

echo ""
echo "✅ Git 仓库初始化完成!"
echo ""
echo "📝 下一步操作:"
echo "1. 在 GitHub 上创建新仓库"
echo "2. 运行以下命令添加远程仓库:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "3. 推送到 GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📋 GitHub 描述 (已复制到剪贴板，可直接粘贴):"
echo "Comprehensive video quality analyzer for AI-generated videos. Analyzes FPS dynamics, motion continuity, duplicate frames, and wobble distortion. Batch processing with Excel/CSV reports."
echo ""
