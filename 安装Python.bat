@echo off
chcp 65001 >nul
title 自动安装 Python
color 0C

echo.
echo ========================================
echo    自动安装 Python 3.12
echo ========================================
echo.

:: 设置 Python 版本和下载链接
set PYTHON_VERSION=3.12.7
set PYTHON_INSTALLER=python-%PYTHON_VERSION%-amd64.exe
set DOWNLOAD_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_INSTALLER%

echo [1/4] 准备下载 Python %PYTHON_VERSION%...
echo.

:: 检查是否已下载
if exist "%PYTHON_INSTALLER%" (
    echo [提示] 找到已下载的安装程序，跳过下载
    echo.
    goto :install
)

:: 下载 Python 安装程序
echo 正在从官方镜像下载 Python...
echo 下载地址: %DOWNLOAD_URL%
echo 文件大小: 约 25 MB
echo.
echo 请稍候...（下载时间取决于网络速度）
echo.

powershell -Command "& {
    $ProgressPreference = 'SilentlyContinue';
    Write-Host '开始下载...' -ForegroundColor Green;
    try {
        Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing;
        Write-Host '下载完成！' -ForegroundColor Green;
    } catch {
        Write-Host '下载失败：' $_.Exception.Message -ForegroundColor Red;
        exit 1;
    }
}"

if %errorlevel% neq 0 (
    echo.
    echo [错误] 下载失败！
    echo.
    echo 可能的原因:
    echo 1. 网络连接问题
    echo 2. 防火墙阻止
    echo.
    echo 建议手动下载:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载 Python 3.12.x (64位)
    echo 3. 运行安装程序，勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:install
echo.
echo [2/4] 检查安装程序...
if not exist "%PYTHON_INSTALLER%" (
    echo [错误] 安装程序不存在！
    pause
    exit /b 1
)

echo [✓] 安装程序已准备好
echo 文件: %PYTHON_INSTALLER%
echo.

echo [3/4] 开始安装 Python...
echo.
echo 安装选项:
echo - 添加 Python 到 PATH
echo - 安装 pip
echo - 安装 tcl/tk
echo - 安装文档
echo.
echo 正在安装，请稍候...
echo （安装窗口可能会在后台，请等待完成）
echo.

:: 静默安装 Python，添加到 PATH
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0

if %errorlevel% neq 0 (
    echo.
    echo [错误] 安装失败！
    echo.
    echo 尝试交互式安装...
    echo 请在安装界面勾选 "Add Python to PATH"
    echo.
    "%PYTHON_INSTALLER%"
    pause
    exit /b 1
)

echo.
echo [4/4] 验证安装...
echo.

:: 刷新环境变量
echo 刷新环境变量...
call :RefreshEnv
timeout /t 2 /nobreak >nul

:: 验证 Python 安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] Python 命令未找到
    echo.
    echo 可能需要：
    echo 1. 关闭并重新打开命令提示符
    echo 2. 重启电脑
    echo 3. 手动添加 Python 到系统 PATH
    echo.
) else (
    python --version
    echo [✓] Python 安装成功！
    echo.
    
    :: 升级 pip
    echo 升级 pip...
    python -m pip install --upgrade pip --quiet
    echo [✓] pip 已升级
    echo.
)

:: 验证 pip
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    pip --version
    echo [✓] pip 已就绪
)

echo.
echo ========================================
echo  Python 安装完成！
echo ========================================
echo.

:: 清理安装文件（可选）
set /p cleanup="是否删除安装文件 %PYTHON_INSTALLER%？(Y/N): "
if /i "%cleanup%"=="Y" (
    del "%PYTHON_INSTALLER%"
    echo [✓] 已删除安装文件
)

echo.
echo === 下一步 ===
echo.
echo 1. 关闭此窗口
echo 2. 重新运行 "首次安装.bat" 或 "启动.bat"
echo 3. 如果仍提示未找到 Python，请重启电脑
echo.
pause
exit /b 0

:: 刷新环境变量的函数
:RefreshEnv
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "UserPath=%%b"
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SystemPath=%%b"
set "PATH=%UserPath%;%SystemPath%"
goto :eof
