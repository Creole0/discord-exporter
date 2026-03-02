@echo off
chcp 65001 >nul
title Discord 导出工具 - 更新并启动
color 0B

echo.
echo ========================================
echo    Discord 导出工具 - 更新并启动
echo ========================================
echo.

:: 检查 Git
echo [1/6] 检查 Git 环境...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到 Git，跳过更新步骤
    echo.
) else (
    git --version
    echo [✓] Git 环境正常
    echo.
    
    :: 拉取最新代码
    echo [2/6] 拉取最新代码...
    git pull origin main
    if %errorlevel% neq 0 (
        echo [警告] 代码更新失败，继续使用本地版本
    ) else (
        echo [✓] 代码已更新到最新版本
    )
    echo.
)

:: 检查 Python
echo [3/6] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo [✓] Python 环境正常
echo.

:: 更新依赖
echo [4/6] 更新依赖包...
pip install --upgrade -r requirements.txt
if %errorlevel% neq 0 (
    echo [警告] 依赖更新失败，尝试继续...
) else (
    echo [✓] 依赖已更新
)
echo.

:: 检查目录
echo [5/6] 检查必要目录...
if not exist "exports" mkdir exports
echo [✓] 目录检查完成
echo.

:: 启动应用
echo [6/6] 启动应用...
echo.
echo ========================================
echo  应用正在启动...
echo ========================================
echo.
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 可停止服务器
echo ========================================
echo.

timeout /t 2 /nobreak >nul
start http://localhost:5000

python app.py

echo.
echo ========================================
echo  应用已停止
echo ========================================
pause
