@echo off
REM Tectonic LaTeX Compiler Installer for Windows
REM This script helps you install Tectonic easily

echo ==========================================
echo Tectonic LaTeX Compiler Installer
echo ==========================================
echo.

REM Check if Tectonic is already installed
where tectonic >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Tectonic is already installed!
    tectonic --version
    echo.
    echo You're all set. Run compile_presentation.bat to compile your LaTeX files.
    pause
    exit /b 0
)

echo Tectonic not found. Let's install it...
echo.

REM Check for Scoop
where scoop >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Scoop package manager.
    echo Installing Tectonic via Scoop...
    echo.
    scoop install tectonic
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ==========================================
        echo Success! Tectonic installed successfully!
        echo ==========================================
        tectonic --version
        pause
        exit /b 0
    ) else (
        echo.
        echo Failed to install via Scoop. Trying alternative methods...
        echo.
    )
)

REM Check for Chocolatey
where choco >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found Chocolatey package manager.
    echo Installing Tectonic via Chocolatey...
    echo.
    choco install tectonic -y
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ==========================================
        echo Success! Tectonic installed successfully!
        echo ==========================================
        tectonic --version
        pause
        exit /b 0
    ) else (
        echo.
        echo Failed to install via Chocolatey.
        echo.
    )
)

REM No package manager found - provide manual instructions
echo ==========================================
echo Manual Installation Required
echo ==========================================
echo.
echo No package manager (Scoop/Chocolatey) found.
echo.
echo Please choose one of these options:
echo.
echo OPTION 1: Install Scoop (Recommended - easiest)
echo   1. Open PowerShell as Administrator
echo   2. Run: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
echo   3. Run: irm get.scoop.sh ^| iex
echo   4. Run this script again
echo.
echo OPTION 2: Install Chocolatey
echo   1. Open PowerShell as Administrator
echo   2. Run: Set-ExecutionPolicy Bypass -Scope Process -Force
echo   3. Run: [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
echo   4. Run: iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
echo   5. Run this script again
echo.
echo OPTION 3: Download Tectonic directly
echo   1. Visit: https://github.com/tectonic-typesetting/tectonic/releases
echo   2. Download the Windows installer
echo   3. Run the installer
echo   4. Add Tectonic to your PATH environment variable
echo.
echo OPTION 4: Install MiKTeX (traditional, large download)
echo   Visit: https://miktex.org/download
echo.
pause
exit /b 1
