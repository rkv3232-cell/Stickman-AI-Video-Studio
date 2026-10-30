@echo off
chcp 65001 >nul
title Stickman AI Video Studio — GitHub Auto-Sync
color 0B

echo =====================================================================
echo    🚀 STICKMAN AI VIDEO STUDIO — GITHUB ONE-CLICK REPO UPDATE
echo =====================================================================
echo.

:: Check Git installation
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [ERROR] Git is not installed or not in PATH!
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

:: Ensure we are in a git repository
if not exist ".git" (
    color 0C
    echo [ERROR] Current directory is not a Git repository!
    pause
    exit /b 1
)

:: Check for changes
echo [1/4] Checking repository status...
git status --short > "%temp%\git_status_check.txt"

for /f %%i in ("%temp%\git_status_check.txt") do set STATUS_SIZE=%%~zi
if "%STATUS_SIZE%"=="0" (
    color 0A
    echo.
    echo ✅ Everything is already up to date! No changes to commit.
    echo.
    del "%temp%\git_status_check.txt" >nul 2>&1
    pause
    exit /b 0
)

echo.
echo Found the following changes:
echo ---------------------------------------------------------------------
git status --short
echo ---------------------------------------------------------------------
echo.
del "%temp%\git_status_check.txt" >nul 2>&1

:: Get commit message from user or use default
set "DEFAULT_MSG=Update Stickman Studio: voiceover & automation upgrades (%date% %time%)"
set "USER_MSG="
set /p "USER_MSG=Enter commit message (Press Enter to use default): "

if "%USER_MSG%"=="" (
    set "COMMIT_MSG=%DEFAULT_MSG%"
) else (
    set "COMMIT_MSG=%USER_MSG%"
)

echo.
echo [2/4] Staging files...
git add -A

echo [3/4] Creating commit...
git commit -m "%COMMIT_MSG%"
if %ERRORLEVEL% neq 0 (
    echo.
    echo ℹ️ Nothing new to commit or commit skipped.
)

echo [4/4] Pushing to GitHub (origin/main)...
echo.
git push origin main

if %ERRORLEVEL% equ 0 (
    color 0A
    echo.
    echo =====================================================================
    echo    ✅ SUCCESS! Repository has been successfully updated on GitHub!
    echo    🔗 https://github.com/rkv3232-cell/Stickman-AI-Video-Studio
    echo =====================================================================
) else (
    color 0C
    echo.
    echo =====================================================================
    echo    ❌ [ERROR] Push to GitHub failed!
    echo    Check your internet connection or run: git pull --rebase origin main
    echo =====================================================================
)

echo.
pause
