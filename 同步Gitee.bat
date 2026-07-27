@echo off
chcp 65001 >nul
title 同步Gitee - 第二大脑
echo.
echo ═══════════════════════════════════════
echo   🔄 正在从 Gitee 同步最新内容...
echo ═══════════════════════════════════════
echo.

cd /d "%~dp0"

git pull

if %errorlevel% equ 0 (
    echo.
    echo ✅ 同步成功！Obsidian 已更新
    timeout /t 3
) else (
    echo.
    echo ❌ 同步失败，请检查网络连接
    pause
)
