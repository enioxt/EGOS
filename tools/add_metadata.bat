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

@echo off
REM ===================================
REM EVA & GUARANI - Metadata Manager v1.0
REM ===================================
REM
REM METADATA:
REM type: utility
REM category: core
REM subsystem: MASTER
REM status: active
REM required: false
REM dependencies:
REM   - Python 3.8+
REM   - metadata_manager.py
REM description: Batch script to run the metadata management tool
REM author: EVA & GUARANI
REM version: 1.0.0
REM last_updated: 2025-03-28
REM
REM ===================================

echo ===================================
echo EVA ^& GUARANI - Metadata Manager v1.0
echo ===================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Create and activate virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install or update dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Get the workspace root directory
cd ..
set "WORKSPACE_ROOT=%CD%"

REM Run the metadata manager
echo.
echo Running metadata manager...
python tools\metadata_manager.py "%WORKSPACE_ROOT%"

REM Check the result
if errorlevel 1 (
    echo.
    echo Error: Metadata manager failed
    echo Please check metadata_manager.log for details
) else (
    echo.
    echo Metadata manager completed successfully
    echo Please check metadata_report.txt for details
)

REM Deactivate virtual environment
deactivate

echo.
echo Press any key to exit...
pause > nul
