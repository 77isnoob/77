@echo off
chcp 65001 >nul
title 取消定时同步

echo.
echo ═══════════════════════════════════════
echo   🛑 取消第二大脑定时同步
echo ═══════════════════════════════════════
echo.

schtasks /delete /tn "第二大脑-Gitee同步" /f

if %errorlevel% equ 0 (
    echo ✅ 已取消定时同步任务
) else (
    echo ❌ 未找到定时任务，或需要以管理员身份运行
)

echo.
pause
