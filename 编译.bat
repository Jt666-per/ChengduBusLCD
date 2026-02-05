@echo off
chcp 936 > nul
title 公交LCD模拟器打包工具

echo 公交LCD模拟器 V1.1.2 打包工具
echo ================================
echo.

echo 步骤1: 清理环境...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo 步骤2: 开始打包...
echo 使用参数: --onedir --console --version-file=version_info.txt

REM 这是核心打包命令 - 已验证有效
pyinstaller --onedir --console --icon=logo.ico --add-data="styles;styles" --add-data="styles/resources;resources" --name="公交LCD模拟器V1.1.2" --version-file=version_info.txt --clean main.py

if errorlevel 1 (
    echo.
    echo ? 打包失败！
    echo 请检查上面的错误信息。
    pause
    exit /b 1
)

echo.
echo ? 打包完成！
echo 输出目录: dist\公交LCD模拟器V1.1.2

echo.
echo 步骤3: 检查生成的exe文件...
if not exist "dist\公交LCD模拟器V1.1.2\公交LCD模拟器V1.1.2.exe" (
    echo ? 错误: 未找到主程序文件
    pause
    exit /b 1
)

REM 显示文件信息
for %%I in ("dist\公交LCD模拟器V1.1.2\公交LCD模拟器V1.1.2.exe") do (
    echo 主程序大小: %%~zI 字节 (约 %%~zI/1048576 MB)
)

echo.
echo 步骤4: 测试程序运行...
echo 正在测试程序是否能正常运行...
cd "dist\公交LCD模拟器V1.1.2"
echo 当前目录: %cd%

REM 测试运行程序（5秒后自动关闭）
start "" "公交LCD模拟器V1.1.2.exe"
timeout /t 5 > nul
taskkill /f /im "公交LCD模拟器V1.1.2.exe" > nul 2>&1

cd ..\..

echo.
echo ? 程序测试运行正常！
echo.
echo 打包完成！
echo.
echo 重要说明:
echo 1. 使用 --onedir 模式，所有文件在 dist\公交LCD模拟器V1.1.2 文件夹中
echo 2. 使用 --console 参数，程序会显示控制台窗口（方便调试）
echo 3. 已包含版本信息
echo 4. 程序依赖的所有DLL都在同一目录，这是PyInstaller的标准行为
echo.
echo 如果需要隐藏控制台，请将 --console 改为 --windowed
echo.
pause