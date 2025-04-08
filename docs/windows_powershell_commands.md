# Windows PowerShell Command Reference

This reference document provides the correct command syntax for Windows PowerShell, to ensure all operations work properly in the EVA & GUARANI EGOS project.

## Navigation Commands

```powershell
# Change directory - use Windows path format
cd "C:\Eva Guarani EGOS"

# Navigate to subdirectory
cd ".\QUANTUM_PROMPTS\MASTER"

# Go up one directory
cd ..

# List directory contents
dir
# or
Get-ChildItem

# List directory with details
dir -Force
# or
Get-ChildItem -Force
```

## File and Directory Operations

```powershell
# Create directory
mkdir "new_directory"
# or
New-Item -ItemType Directory -Path "new_directory"

# Create nested directories (similar to mkdir -p)
New-Item -ItemType Directory -Path "path\to\nested\directories" -Force

# Create a file
New-Item -ItemType File -Path "filename.txt"

# Copy a file
Copy-Item "source.txt" "destination.txt"

# Move a file
Move-Item "source.txt" "destination.txt"

# Delete a file
Remove-Item "filename.txt"

# Check if file exists
Test-Path "filename.txt"
```

## Command Chaining

```powershell
# Use semicolon to chain commands
cd "C:\Eva Guarani EGOS"; dir

# AND operator (run second command only if first succeeds)
cd "C:\Eva Guarani EGOS" -and (dir)

# OR operator (run second command only if first fails)
cd "C:\Eva Guarani EGOS" -or (Write-Error "Failed to change directory")
```

## Running Python and Other Commands

```powershell
# Run Python script
python script.py

# Run Python module
python -m http.server 3000

# Install Python package
pip install -r requirements.txt

# Run tests with pytest
pytest .\tests\
```

## Environment Variables

```powershell
# Set environment variable for current session
$env:VARIABLE_NAME = "value"

# Read environment variable
$env:VARIABLE_NAME

# List all environment variables
Get-ChildItem Env:
```

## Important Notes

1. Use double quotes (`"`) for paths with spaces
2. Use backslashes (`\`) for path separators in Windows, not forward slashes (`/`)
3. Use `.` to reference current directory, not `/`
4. PowerShell has tab completion for paths and commands
5. Commands are case-insensitive in PowerShell
6. Use `-Force` parameter to override confirmations or create nested directories

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
