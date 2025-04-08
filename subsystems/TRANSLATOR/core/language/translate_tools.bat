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
setlocal enabledelayedexpansion

REM EVA & GUARANI Translation Tools - Batch Interface
REM This script provides a user-friendly interface for the translation tools

REM Set up paths
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\..\"
set "SCANNER_SCRIPT=%SCRIPT_DIR%translate_to_english.py"
set "TRANSLATOR_SCRIPT=%SCRIPT_DIR%ai_translate_file.py"

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if required scripts exist
if not exist "%SCANNER_SCRIPT%" (
    echo ERROR: Scanner script not found at %SCANNER_SCRIPT%
    pause
    exit /b 1
)

if not exist "%TRANSLATOR_SCRIPT%" (
    echo ERROR: Translator script not found at %TRANSLATOR_SCRIPT%
    pause
    exit /b 1
)

REM Set default paths
set "DEFAULT_ROOT_DIR=%PROJECT_ROOT%"
set "DEFAULT_OUTPUT_DIR=%SCRIPT_DIR%reports\"

REM Create reports directory if it doesn't exist
if not exist "%DEFAULT_OUTPUT_DIR%" mkdir "%DEFAULT_OUTPUT_DIR%"

REM Main menu
:menu
cls
echo =====================================================
echo   EVA ^& GUARANI Translation Tools - Batch Interface
echo =====================================================
echo.
echo These tools help you translate files from Portuguese to English
echo and identify files containing Portuguese text.
echo.
echo LOCATION: %SCRIPT_DIR%
echo.
echo Available Tools:
echo 1. Scan for Portuguese files
echo 2. Translate a specific file
echo 3. Batch translate files
echo 4. Configure API Key
echo 5. Help
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto scan_project
if "%choice%"=="2" goto translate_file
if "%choice%"=="3" goto batch_translate
if "%choice%"=="4" goto configure_api
if "%choice%"=="5" goto show_help
if "%choice%"=="6" goto exit_script

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:: Scan project
:scan_project
echo.
echo Scanning project for Portuguese files...
echo.

set "defaultRootDir=C:\Eva & Guarani - EGOS"

if not exist "%defaultRootDir%" (
    set "defaultRootDir=..\..\"
)

echo This will scan the entire EVA ^& GUARANI system for Portuguese content.
echo The scan will focus on project files and exclude system directories.
echo This may take a few minutes depending on the size of your project.
echo.

set /p rootDir="Enter root directory to scan (default: %defaultRootDir%): "

if "!rootDir!"=="" (
    set "rootDir=%defaultRootDir%"
)

echo.
echo Running scanner...
echo.

set "report_file=%SCRIPT_DIR%translation_report.md"
python translate_to_english.py --root-dir "!rootDir!" --output "!report_file!"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Scan complete. Results saved to: !report_file!
    echo.

    :: Check if any files were found
    findstr /i /c:"| File |" "!report_file!" > nul
    if %ERRORLEVEL% EQU 0 (
        echo Portuguese files were detected in your project.
        echo.
        echo Options:
        echo 1. Translate all detected files now
        echo 2. View the report first
        echo 3. Return to main menu
        echo.
        set /p translate_option="What would you like to do? (1-3): "

        if "!translate_option!"=="1" (
            echo.
            echo Starting batch translation of all detected files...
            echo.
            set "translate_all=true"
            goto start_batch_translation
        ) else if "!translate_option!"=="2" (
            echo.
            echo Displaying report contents:
            echo.
            type "!report_file!"
            echo.
            echo After reviewing the report:
            echo 1. Translate all detected files
            echo 2. Return to main menu
            echo.
            set /p post_review="What would you like to do? (1-2): "

            if "!post_review!"=="1" (
                echo.
                echo Starting batch translation...
                echo.
                set "translate_all=true"
                goto start_batch_translation
            )
        )
    ) else (
        echo No Portuguese files were detected in your project.
    )
) else (
    echo.
    echo Scan failed with error code %ERRORLEVEL%
    echo.
)

pause
cls
goto menu

:: Translate a file
:translate_file
echo.
echo Translate a specific file using AI
echo.
set /p file_path="Enter the path to the file you want to translate: "

if not exist "!file_path!" (
    echo File does not exist: !file_path!
    pause
    cls
    goto menu
)

REM Set default API key (remove hardcoded value)
set "default_api_key="
REM User should set the OPENAI_API_KEY environment variable instead.
REM Example: setx OPENAI_API_KEY "your_key_here"

echo.
echo Enter the path to the file or folder to translate.
set /p custom_api_key="Enter your OpenAI API key (or press Enter to use OPENAI_API_KEY environment variable): "
set "api_key_param="
if not "!custom_api_key!"=="" (
    set "api_key_param=--api-key !custom_api_key!"
) else (
    REM No custom key, rely on environment variable (already set or needs to be set by user)
    REM Removed: set "OPENAI_API_KEY=!default_api_key!"
    set "api_key_param="
)

set /p output_path="Enter output file path (leave empty to replace original): "
set "output_param="
if not "!output_path!"=="" (
    set "output_param=--output !output_path!"
)

set /p dry_run="Do you want to perform a dry run (no changes will be made)? (y/N): "
set "dry_run_param="
if /i "!dry_run!"=="y" (
    set "dry_run_param=--dry-run"
)

echo.
echo Translating file...
echo.

python ai_translate_file.py --file "!file_path!" !api_key_param! !output_param! !dry_run_param!

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Translation complete. Check the output file.
    echo.
) else (
    echo.
    echo Translation failed with error code %ERRORLEVEL%
    echo.
)

pause
cls
goto menu

:: Batch translate
:batch_translate
cls
call :display_header
echo BATCH TRANSLATE MODE
echo =====================
echo This mode allows you to translate multiple files listed in a translation report.
echo.

set "report_file=%SCRIPT_DIR%translation_report.md"
set /p report_file="Enter path to translation report file (or press Enter for default: %report_file%): "

if not exist "%report_file%" (
    echo Report file not found: %report_file%
    echo Please run the scanner first to generate a report.
    pause
    cls
    goto menu
)

set "translate_all=false"

:start_batch_translation
echo.
echo Will process files listed in: "%report_file%"
echo.

if "%translate_all%"=="false" (
    set /p confirm="Proceed with batch translation? (Y/N): "
    if /i not "%confirm%"=="Y" goto menu
)

echo.
echo Starting batch translation...
echo This may take some time depending on the number of files.
echo.

:: Set default API key for batch translation
set "OPENAI_API_KEY=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"

echo Processing files from report: "%report_file%"
echo.

:: Extract file paths using a more reliable method
set "temp_file=%TEMP%\files_to_translate.txt"
:: Create a temporary Python script to extract file paths
set "extract_script=%TEMP%\extract_paths.py"

echo import re > "%extract_script%"
echo import sys >> "%extract_script%"
echo import os >> "%extract_script%"
echo with open(r"%report_file%", "r", encoding="utf-8") as f: >> "%extract_script%"
echo     content = f.read() >> "%extract_script%"
echo pattern = r"\|\s*([^|]+\.(?:py|md|txt|json|js|html|css|bat|ps1))\s*\|" >> "%extract_script%"
echo matches = re.findall(pattern, content) >> "%extract_script%"
echo # Use forward slashes which work on Windows too >> "%extract_script%"
echo project_root = "C:/Eva & Guarani - EGOS" >> "%extract_script%"
echo with open(r"%temp_file%", "w", encoding="utf-8") as out: >> "%extract_script%"
echo     for match in matches: >> "%extract_script%"
echo         path = match.strip() >> "%extract_script%"
echo         if path and not path.startswith("Size") and not path.startswith("Type"): >> "%extract_script%"
echo             # Create absolute path relative to project root >> "%extract_script%"
echo             abs_path = os.path.join(project_root, path) >> "%extract_script%"
echo             if os.path.exists(abs_path): >> "%extract_script%"
echo                 out.write(abs_path + "\n") >> "%extract_script%"
echo             else: >> "%extract_script%"
echo                 print(f"Warning: File not found: {abs_path}") >> "%extract_script%"

:: Run the extraction script
python "%extract_script%"

:: Count how many files to translate
set /a count=0
for /F "tokens=*" %%a in ('type "%temp_file%"') do (
    set /a count+=1
)

if %count% EQU 0 (
    echo No valid files found in the report to translate.
    pause
    goto menu
)

echo Found %count% files to translate.
echo.

:: Process each file
set /a current=0
set /a success=0
set /a failed=0

for /F "usebackq tokens=*" %%a in ("%temp_file%") do (
    set "file_path=%%a"
    setlocal enabledelayedexpansion

    set /a current+=1
    echo [!current!/%count%] Translating: "!file_path!"

    :: Check if file exists
    if exist "!file_path!" (
        :: Translate the file
        python ai_translate_file.py --file "!file_path!"

        if !ERRORLEVEL! EQU 0 (
            set /a success+=1
            echo Translation successful.
        ) else (
            set /a failed+=1
            echo Translation failed.
        )
    ) else (
        echo File not found: "!file_path!"
        set /a failed+=1
    )
    echo.
    endlocal & set /a success=%success% & set /a failed=%failed% & set /a current=%current%
)

:: Clean up
del "%temp_file%" 2>nul
del "%extract_script%" 2>nul

echo.
echo Batch translation completed.
echo Successfully translated: %success% files
echo Failed to translate: %failed% files
echo.
pause
cls
goto menu

:: Configure API key
:configure_api
cls
call :display_header
echo API KEY CONFIGURATION
echo ====================
echo.
echo Current API Key:
python "%TRANSLATOR_SCRIPT%" --show-key
echo.
echo Options:
echo 1. Enter a custom API key
echo 2. Use environment variable (set OPENAI_API_KEY)
echo 3. Use default project key
echo 4. Back to main menu
echo.
set /p key_option="Enter your choice (1-4): "

if "%key_option%"=="1" (
    echo.
    set /p api_key="Enter your OpenAI API key: "
    python "%TRANSLATOR_SCRIPT%" --set-key "%api_key%"
    echo.
    echo API key configured.
    pause
) else if "%key_option%"=="2" (
    echo.
    echo Please set the OPENAI_API_KEY environment variable.
    echo Example: setx OPENAI_API_KEY "your-key-here"
    echo.
    echo After setting the environment variable, you may need to restart this script.
    pause
) else if "%key_option%"=="3" (
    echo.
    python "%TRANSLATOR_SCRIPT%" --use-default-key
    echo.
    echo Using default project key.
    pause
)

cls
goto menu

:: Show help
:show_help
cls
call :display_header
echo HELP & DOCUMENTATION
echo ====================
echo.
echo These tools help you identify and translate Portuguese content to English.
echo.
echo SCAN MODE:
echo - Scans the entire project for files containing Portuguese content
echo - Generates a report with files prioritized by importance
echo - Use this first to identify which files need translation
echo.
echo TRANSLATE MODE:
echo - Translates a single file from Portuguese to English
echo - Creates a backup of the original file before translation
echo - Supports various file formats including code and documentation
echo.
echo BATCH MODE:
echo - Translates multiple files listed in a translation report
echo - Useful for bulk translation after scanning
echo.
echo For more details, see the TRANSLATE_README.md file in:
echo %SCRIPT_DIR%
echo.
pause
cls
goto menu

:: Display header (used by multiple functions)
:display_header
echo =====================================================
echo   EVA ^& GUARANI Translation Tools - Batch Interface
echo =====================================================
echo.
goto :eof

:exit_script
echo.
echo Thank you for using EVA ^& GUARANI Translation Tools.
echo ✧༺❀༻∞ EVA ^& GUARANI ∞༺❀༻✧
echo.
endlocal
exit /b 0
