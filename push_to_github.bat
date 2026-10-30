@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo    STICKMAN AI VIDEO STUDIO 3.0 -- GITHUB UPLOAD HELPER
echo ======================================================================
echo.

git status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [Error] Git repository not initialized!
    pause
    exit /b 1
)

echo Checking git remote origin...
git remote get-url origin >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%u in ('git remote get-url origin') do set CURRENT_REMOTE=%%u
    echo Current remote: !CURRENT_REMOTE!
    echo.
    set /p CONFIRM="Do you want to push to this repository? (Y/N): "
    if /i "!CONFIRM!"=="Y" (
        goto PUSH
    )
)

echo.
echo Please create a new empty repository on GitHub:
echo   1. Open https://github.com/new
echo   2. Set Repository Name (e.g. stickman-ai-video-studio)
echo   3. Set Public
echo   4. Do NOT initialize with README, .gitignore or license
echo   5. Click 'Create repository'
echo   6. Copy the repository URL (e.g. https://github.com/username/stickman-ai-video-studio.git)
echo.

set /p REPO_URL="Enter your GitHub Repository URL: "
if "%REPO_URL%"=="" (
    echo [Error] No repository URL provided!
    pause
    exit /b 1
)

git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
echo [Success] Configured remote origin: %REPO_URL%
echo.

:PUSH
echo Pushing project to GitHub (branch: main)...
git branch -M main
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo   [SUCCESS] Your project has been successfully uploaded to GitHub!
    echo ======================================================================
) else (
    echo.
    echo [Note] If authentication failed, Git Credential Manager or GitHub Token may be needed.
)

pause
