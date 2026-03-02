@echo off
chcp 65001 >nul
title 推送代码到 GitHub
color 0E

echo.
echo ========================================
echo    推送代码到 GitHub
echo ========================================
echo.

:: 检查 Git
echo [1/4] 检查 Git 环境...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git！
    echo.
    echo 请先安装 Git
    echo 下载地址: https://git-scm.com/downloads
    echo.
    pause
    exit /b 1
)

git --version
echo [✓] Git 环境正常
echo.

:: 显示状态
echo [2/4] 检查文件状态...
echo.
git status
echo.

:: 添加所有更改
echo [3/4] 添加所有更改...
git add .
echo [✓] 文件已添加到暂存区
echo.

:: 提交更改
echo [4/4] 提交并推送...
echo.
set /p commit_msg="请输入提交信息 (留空使用默认): "

if "%commit_msg%"=="" (
    set commit_msg=update: update code
)

echo.
echo 提交信息: %commit_msg%
echo.

git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo [提示] 没有需要提交的更改，或提交失败
    echo.
)

echo 正在推送到 GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo.
    echo [错误] 推送失败！
    echo.
    echo 可能的原因:
    echo 1. 没有配置 Git 凭据
    echo 2. 没有推送权限
    echo 3. 网络连接问题
    echo.
    echo 请检查后重试
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  代码已成功推送到 GitHub！
echo ========================================
echo.
echo GitHub 仓库: https://github.com/Creole0/discord-exporter
echo.
echo 如果部署在 Zeabur，它会自动检测更新并重新部署
echo.
pause
