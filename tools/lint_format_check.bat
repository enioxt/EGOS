@echo off
REM Runs Ruff formatter check and linter across the project.

REM Activate virtual environment if it exists and isn't active
REM This assumes a standard venv name. Adjust if yours is different.
REM if not defined VIRTUAL_ENV (
REM     if exist venv\Scripts\activate.bat (
REM         echo Activating virtual environment...
REM         call venv\Scripts\activate.bat
REM     ) else if exist .venv\Scripts\activate.bat (
REM         echo Activating virtual environment...
REM         call .venv\Scripts\activate.bat
REM     )
REM )

echo Running Ruff Formatter Check...
ruff format . --check
if %errorlevel% neq 0 (
    echo.
    echo Formatting issues found. Run 'ruff format .' to fix.
    exit /b 1
) else (
    echo Formatter check passed.
)

echo.
echo Running Ruff Linter...
ruff check .
if %errorlevel% neq 0 (
    echo.
    echo Linter issues found. Run 'ruff check . --fix' to attempt fixes.
    exit /b 1
) else (
    echo Linter check passed.
)

echo.
echo All checks passed successfully!
exit /b 0
