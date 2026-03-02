@echo off
chcp 65001 >nul
title Discord 导出工具 - 启动器
color 0A

echo.
echo ========================================
echo    Discord 导出工具 - 一键启动
echo ========================================
echo.

:: 检查 Python 是否安装
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo [✓] Python 环境正常
echo.

:: 检查并安装依赖
echo [2/4] 检查依赖包...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 检测到缺少依赖，正在安装...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
    echo.
    echo [✓] 依赖安装完成
) else (
    echo [✓] 依赖包已安装
)
echo.

:: 检查 exports 目录
echo [3/4] 检查导出目录...
if not exist "exports" (
    mkdir exports
    echo [✓] 已创建 exports 目录
) else (
    echo [✓] exports 目录已存在
)
echo.

:: 启动应用
echo [4/4] 启动应用...
echo.
echo ========================================
echo  应用正在启动，请稍候...
echo ========================================
echo.
echo 启动成功后会自动打开浏览器
echo 访问地址: http://localhost:5000
echo.
echo 按 Ctrl+C 可停止服务器
echo ========================================
echo.

:: 等待2秒后自动打开浏览器
timeout /t 2 /nobreak >nul
start http://localhost:5000

:: 启动 Flask 应用
python app.py

:: 如果应用异常退出
echo.
echo ========================================
echo  应用已停止
echo ========================================
pause
