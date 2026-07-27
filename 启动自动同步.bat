@echo off
chcp 65001 >nul
title 第二大脑自动同步
echo.
echo ═══════════════════════════════════════
echo   🧠 第二大脑自动同步脚本
echo ═══════════════════════════════════════
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0auto-sync.ps1"
pause
