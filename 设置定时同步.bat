@echo off
chcp 65001 >nul
title 设置定时同步

echo.
echo ═══════════════════════════════════════
echo   ⏰ 设置每 10 分钟自动同步 Gitee
echo ═══════════════════════════════════════
echo.

cd /d "%~dp0"

:: 创建拉取脚本
(
echo @echo off
echo cd /d "%~dp0"
echo git pull --rebase
) > auto-pull.bat

:: 创建计划任务（每10分钟执行一次）
schtasks /create /tn "第二大脑-Gitee同步" /tr "\"%~dp0auto-pull.bat\"" /sc minute /mo 10 /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ 定时任务创建成功！
    echo    每 10 分钟自动从 Gitee 同步最新内容
    echo.
    echo 📌 如需取消，运行"取消定时同步.bat"
    echo.
) else (
    echo.
    echo ❌ 创建失败，请以管理员身份运行此脚本
    echo    右键 → 以管理员身份运行
    echo.
)

pause
