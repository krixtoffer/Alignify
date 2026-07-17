@echo off
title Alignify! v1.0.0 Launcher
echo =============================================
echo           Starting Alignify! v1.0.0
echo =============================================
echo.

:: === Locate Conda automatically ===
set "CONDAPATH="
for %%P in ("%USERPROFILE%\anaconda3" "%USERPROFILE%\miniconda3" "%ProgramData%\anaconda3" "%ProgramData%\miniconda3") do (
    if exist "%%~P\Scripts\activate.bat" set "CONDAPATH=%%~P"
)

if "%CONDAPATH%"=="" (
    echo [ERROR] Could not find a Conda installation automatically.
    echo If Conda is installed somewhere else, edit this file and set
    echo CONDAPATH manually to your Anaconda/Miniconda folder.
    pause
    exit /b 1
)

:: === Check that the alignify environment exists ===
if not exist "%CONDAPATH%\envs\alignify" (
    echo [ERROR] The 'alignify' environment was NOT found!
    echo.
    echo Please open Anaconda Prompt and run this command once:
    echo     conda env create -f environment.yml
    echo.
    pause
    exit /b 1
)

:: === Activate the environment ===
call "%CONDAPATH%\Scripts\activate.bat" "%CONDAPATH%\envs\alignify"
if errorlevel 1 (
    echo [ERROR] Failed to activate the alignify environment.
    pause
    exit /b 1
)

echo Environment ready. Launching Alignify...
echo.
python alignify.py

echo.
echo Program closed.
pause