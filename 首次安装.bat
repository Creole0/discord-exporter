@echo off
chcp 65001 >nul
title Discord 导出工具 - 首次安装
color 0D

echo.
echo ========================================
echo    Discord 导出工具 - 首次安装
echo ========================================
echo.
echo 此脚本将帮助你完成初始化设置
echo.

:: 检查 Python
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    echo.
    echo === 安装 Python 的步骤 ===
    echo 1. 访问: https://www.python.org/downloads/
    echo 2. 下载最新的 Python 3.x 版本
    echo 3. 安装时务必勾选 "Add Python to PATH"
    echo 4. 安装完成后重新运行此脚本
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

python --version
echo [✓] Python 已安装
echo.

:: 检查 pip
echo [2/5] 检查 pip 环境...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] pip 未找到，尝试修复...
    python -m ensurepip --default-pip
)
pip --version
echo [✓] pip 已安装
echo.

:: 升级 pip
echo [3/5] 升级 pip 到最新版本...
python -m pip install --upgrade pip
echo [✓] pip 已升级
echo.

:: 安装依赖
echo [4/5] 安装项目依赖...
echo.
echo 依赖列表:
type requirements.txt
echo.
echo 正在安装...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [错误] 依赖安装失败！
    echo.
    echo 请检查网络连接，或尝试使用国内镜像源:
    echo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    pause
    exit /b 1
)
echo.
echo [✓] 依赖安装完成
echo.

:: 创建必要目录
echo [5/5] 创建必要目录...
if not exist "exports" (
    mkdir exports
    echo [✓] 已创建 exports 目录
)
echo.

:: 显示使用说明
echo ========================================
echo  安装完成！
echo ========================================
echo.
echo 已安装的依赖:
pip list | findstr /C:"Flask" /C:"requests" /C:"openpyxl" /C:"gunicorn"
echo.
echo === 下一步操作 ===
echo.
echo 1. 获取 Discord Bot Token:
echo    - 访问 https://discord.com/developers/applications
echo    - 创建应用并获取 Bot Token
echo.
echo 2. 启动应用:
echo    - 双击 "启动.bat" 即可运行
echo    - 首次使用需要在网页中设置 Bot Token
echo.
echo 3. 使用帮助:
echo    - 查看 "使用说明.md" 了解详细使用方法
echo    - 查看 "测试指南.md" 了解测试步骤
echo.
echo ========================================
echo.

set /p start_now="是否现在启动应用？(Y/N): "
if /i "%start_now%"=="Y" (
    echo.
    echo 正在启动...
    call 启动.bat
) else (
    echo.
    echo 安装完成！稍后可双击 "启动.bat" 来运行应用
    echo.
    pause
)
