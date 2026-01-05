#!/bin/bash
# 安装依赖脚本

echo "=== 视频分析工具 - 依赖安装 ==="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    exit 1
fi

echo "Python 版本: $(python3 --version)"
echo ""

# 安装方式选择
echo "请选择安装方式："
echo "1. 安装 OpenCV (推荐，简单快速)"
echo "2. 安装 ffmpeg (更准确，功能更全面)"
echo "3. 两者都安装"
echo ""
read -p "请输入选择 (1/2/3): " choice

case $choice in
    1)
        echo "正在安装 OpenCV..."
        pip3 install opencv-python numpy
        ;;
    2)
        echo "正在安装 ffmpeg..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install ffmpeg
            else
                echo "错误: 需要先安装 Homebrew"
                echo "访问: https://brew.sh"
                exit 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        else
            echo "请手动安装 ffmpeg: https://ffmpeg.org/download.html"
            exit 1
        fi
        ;;
    3)
        echo "正在安装 OpenCV..."
        pip3 install opencv-python numpy
        echo ""
        echo "正在安装 ffmpeg..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew &> /dev/null; then
                brew install ffmpeg
            else
                echo "警告: Homebrew 未安装，请手动安装 ffmpeg"
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        else
            echo "警告: 请手动安装 ffmpeg"
        fi
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "安装完成！"
echo ""
echo "使用方法:"
echo "  python3 video_analyzer.py <视频文件路径>"
