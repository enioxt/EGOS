---
metadata:
  api_endpoints: []
  author: EVA & GUARANI
  backup_required: true
  category: tools
  changelog: []
  dependencies:
  - QUANTUM_PROMPTS
  - BIOS-Q
  description: Component of the EVA & GUARANI Quantum Unified System
  documentation_quality: 0.95
  encoding: utf-8
  ethical_validation: true
  last_updated: '2025-03-29'
  related_files: []
  required: true
  review_status: approved
  security_level: 0.95
  simulation_capable: false
  status: active
  subsystem: MASTER
  test_coverage: 0.9
  translation_status: completed
  type: script
  version: '8.0'
  windows_compatibility: true
---
REM
REM METADATA:
REM   type: utility
REM   category: module
REM   subsystem: MASTER
REM   status: active
REM   required: false
REM   simulation_capable: true
REM   dependencies: []
REM   description: Component of the  subsystem
REM   author: EVA & GUARANI
REM   version: 1.0.0
REM   last_updated: '2025-03-29'
REM   principles: []
REM   security_level: standard
REM   test_coverage: 0.0
REM   documentation_quality: 0.0
REM   ethical_validation: true
REM   windows_compatibility: true
REM   encoding: utf-8
REM   backup_required: false
REM   translation_status: pending
REM   api_endpoints: []
REM   related_files: []
REM   changelog: ''
REM   review_status: pending
REM REM

REM
REM METADATA:
REM   type: utility
REM   category: module
REM   subsystem: MASTER
REM   status: active
REM   required: false
REM   simulation_capable: true
REM   dependencies: []
REM   description: Component of the  subsystem
REM   author: EVA & GUARANI
REM   version: 1.0.0
REM   last_updated: '2025-03-29'
REM REM


# ==================================================================
# COMBINED FILE FROM MULTIPLE SIMILAR FILES
# Date: 2025-03-22 08:37:43
# Combined files:
# - tools\utilities\install_dependencies.bat (kept)
# - tools\utilities\install_dependencies.bat.backup (moved to quarantine)
# ==================================================================

batch
@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================================
echo            EVA ^& GUARANI - DEPENDENCY INSTALLER
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    echo You can download Python at: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if pip is installed
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip not found. Please install pip.
    echo You can install pip by running: python -m ensurepip --upgrade
    pause
    exit /b 1
)

echo Installing dependencies...
echo.

REM Install mandatory dependencies
echo Installing mandatory dependencies...
python -m pip install python-telegram-bot>=13.0 psutil>=5.8.0 colorama>=0.4.4 requests>=2.25.1 pillow>=8.0.0 numpy>=1.19.0 openai>=0.27.0 tenacity>=8.0.0

echo.
echo Do you want to install optional dependencies? (y/n)
set /p install_optional=

if /i "%install_optional%"=="y" (
    echo.
    echo Installing optional dependencies...
    python -m pip install matplotlib>=3.4.0 pandas>=1.3.0 scikit-learn>=0.24.0 transformers>=4.5.0
)

echo.
echo Verifying installation...
echo.

REM Check if the script check_dependencies.py exists
if exist "check_dependencies.py" (
    python "check_dependencies.py"
) else (
    echo WARNING: The file check_dependencies.py was not found.
    echo Unable to verify the installation of dependencies.
    echo.
    echo Installation completed. You can start the bot with start_bot.bat
)

echo.
pause
