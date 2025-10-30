@echo off
REM Modern LaTeX Beamer Presentation Compiler for Windows using Tectonic
REM Tectonic is a modern, self-contained LaTeX compiler that auto-downloads packages
REM Usage: compile_presentation.bat <latex_file_name>
REM Example: compile_presentation.bat presentation.tex

REM Check if parameter is provided
if "%~1"=="" (
    echo Error: No LaTeX file specified
    echo Usage: compile_presentation.bat ^<latex_file_name^>
    echo Example: compile_presentation.bat presentation.tex
    exit /b 1
)

REM Get the filename and remove .tex extension if present
set "LATEX_FILE=%~1"
set "BASENAME=%~n1"

REM Check if file exists
if not exist "%BASENAME%.tex" (
    echo Error: File '%BASENAME%.tex' not found!
    exit /b 1
)

echo ==========================================
echo Compiling LaTeX Presentation: %BASENAME%.tex
echo ==========================================
echo.

REM Check if Tectonic is installed
where tectonic >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Tectonic not found. Checking for installation options...
    echo.

    REM Check if scoop is installed
    where scoop >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Found Scoop package manager. Installing Tectonic...
        scoop install tectonic
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install Tectonic via Scoop.
            goto :manual_install
        )
    ) else (
        goto :manual_install
    )
) else (
    echo Found Tectonic - proceeding with compilation...
    echo.
)

REM Compile with Tectonic (runs multiple passes automatically)
echo Compiling with Tectonic...
tectonic "%BASENAME%.tex"

REM Check if PDF was created
if not exist "%BASENAME%.pdf" (
    echo.
    echo ==========================================
    echo X Compilation failed - no PDF created!
    echo ==========================================
    echo.
    echo Check the output above for errors.
    echo.
    echo Tectonic usually provides clear error messages.
    echo Common issues:
    echo   - Missing or malformed LaTeX syntax
    echo   - Missing image files
    echo   - Incompatible package usage
    exit /b 1
)

echo.
echo ==========================================
echo Compilation complete!
echo Output: %BASENAME%.pdf
echo ==========================================

REM Open the PDF
echo.
echo Opening PDF...
start "" "%BASENAME%.pdf"

exit /b 0

:manual_install
echo.
echo ==========================================
echo Tectonic Installation Required
echo ==========================================
echo.
echo Tectonic is a modern LaTeX compiler that's much easier to use than MiKTeX/TeX Live.
echo.
echo Installation options:
echo.
echo 1. Install via Scoop (Recommended - easiest):
echo    First install Scoop from https://scoop.sh
echo    Run: scoop install tectonic
echo.
echo 2. Install via Chocolatey:
echo    Run: choco install tectonic
echo.
echo 3. Download installer from:
echo    https://github.com/tectonic-typesetting/tectonic/releases
echo.
echo 4. Alternative - Install MiKTeX (traditional, large):
echo    https://miktex.org/download
echo.
echo After installing Tectonic, run this script again.
echo.
exit /b 1
