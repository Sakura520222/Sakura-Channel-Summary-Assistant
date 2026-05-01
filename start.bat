@echo off
chcp 65001 >nul
title Sakura Bot

:: Set virtual environment Python path
set "PYTHON_EXE=venv\Scripts\python.exe"
set "PIP_EXE=venv\Scripts\pip.exe"

if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
    echo.
)

:: Verify virtual environment Python exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Virtual environment Python not found at: %PYTHON_EXE%
    pause
    exit /b 1
)

echo [INFO] Using virtual environment Python: %PYTHON_EXE%

echo [INFO] Checking dependencies...
"%PYTHON_EXE%" -c "import telegram" 2>nul
if errorlevel 1 (
    echo [WARNING] Dependencies not installed, installing...
    "%PIP_EXE%" install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
    echo.
)

:: Build frontend
echo [INFO] Checking Node.js and npm...
where node >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js not found, skipping frontend build
    echo [INFO] Please install Node.js from https://nodejs.org/
) else (
    where npm >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] npm not found, skipping frontend build
    ) else (
        echo [SUCCESS] Node.js and npm found
        echo.
        
        if not exist "web\" (
            echo [WARNING] Frontend directory does not exist, skipping build
        ) else if not exist "web\package.json" (
            echo [WARNING] web/package.json not found, skipping build
        ) else (
            echo [INFO] Entering frontend directory...
            cd web
            
            echo [INFO] Installing frontend dependencies...
            call npm install
            if errorlevel 1 (
                echo [ERROR] Failed to install frontend dependencies!
                cd ..
                pause
                exit /b 1
            )
            
            echo [INFO] Building frontend...
            call npm run build
            if errorlevel 1 (
                echo [ERROR] Failed to build frontend!
                cd ..
                pause
                exit /b 1
            )
            
            echo [SUCCESS] Frontend build completed
            echo.
            
            cd ..
        )
    )
)

echo [INFO] Starting Sakura Bot...
echo.
"%PYTHON_EXE%" main.py

echo.
echo [INFO] Program exited
pause
