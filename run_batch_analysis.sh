#!/bin/bash
# 批量分析脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境（尝试多个可能的位置）
if [ -d "../.venv" ]; then
    VENV_PYTHON="../.venv/bin/python"
elif [ -d ".venv" ]; then
    VENV_PYTHON=".venv/bin/python"
else
    echo "警告: 未找到虚拟环境，使用系统Python"
    VENV_PYTHON="python3"
fi

echo "开始批量分析所有视频..."
echo "这可能需要较长时间，请耐心等待..."
echo ""

$VENV_PYTHON batch_analyze.py

echo ""
echo "分析完成！请查看生成的CSV/Excel文件"
