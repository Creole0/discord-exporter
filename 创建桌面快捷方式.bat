@echo off
chcp 65001 >nul
title 创建桌面快捷方式
color 0B

echo.
echo ========================================
echo    创建桌面快捷方式
echo ========================================
echo.

:: 获取当前目录
set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop

echo 当前目录: %SCRIPT_DIR%
echo 桌面位置: %DESKTOP%
echo.

:: 创建快捷方式的 VBScript
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\Discord导出工具.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%SCRIPT_DIR%启动.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Discord 频道导出工具 - 快速启动" >> CreateShortcut.vbs
echo oLink.IconLocation = "C:\Windows\System32\shell32.dll,43" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

:: 执行 VBScript
cscript //nologo CreateShortcut.vbs

:: 删除临时文件
del CreateShortcut.vbs

if exist "%DESKTOP%\Discord导出工具.lnk" (
    echo.
    echo ========================================
    echo  快捷方式创建成功！
    echo ========================================
    echo.
    echo 已在桌面创建快捷方式: "Discord导出工具"
    echo.
    echo 现在你可以：
    echo 1. 双击桌面的 "Discord导出工具" 图标启动
    echo 2. 也可以将快捷方式拖到任务栏固定
    echo.
) else (
    echo.
    echo [错误] 快捷方式创建失败！
    echo.
)

pause
