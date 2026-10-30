@echo off
title Raj Everyway Study - CLI Short Generator
echo ================================================================
echo    RAJ EVERYWAY STUDY - CLI SHORT GENERATOR 2.0
echo ================================================================
echo.

set /p PROMPT_TEXT="Enter video topic or press Enter for default: "

if "%PROMPT_TEXT%"=="" (
    .\.venv\Scripts\python.exe main.py --topic ai_study
) else (
    .\.venv\Scripts\python.exe main.py --prompt "%PROMPT_TEXT%"
)

pause
