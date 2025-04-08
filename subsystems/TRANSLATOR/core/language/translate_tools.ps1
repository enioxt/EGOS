# EVA & GUARANI - Translation Tools PowerShell Runner
# This script helps run the translation tools to convert Portuguese content to English
# For the entire EVA & GUARANI system, not just the sandbox
# Usage: .\translate_tools.ps1

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Get directory paths using helper functions
function GetProjectRoot {
    # Get the current directory of the script
    $scriptPath = $MyInvocation.MyCommand.Path
    $scriptDirectory = Split-Path -Parent $scriptPath

    # Get the project root (2 levels up from the tools/language directory)
    $projectRoot = (Get-Item $scriptDirectory).Parent.Parent.FullName
    return $projectRoot
}

function GetToolsDirectory {
    # Get the current directory of the script
    $scriptPath = $MyInvocation.MyCommand.Path
    $scriptDirectory = Split-Path -Parent $scriptPath
    return $scriptDirectory
}

# Initialize paths
$projectRoot = GetProjectRoot
$toolsDir = GetToolsDirectory
$scannerScript = Join-Path $toolsDir "translate_to_english.py"
$translatorScript = Join-Path $toolsDir "ai_translate_file.py"

function Show-Header {
    Write-Host "`n========================================================================" -ForegroundColor Cyan
    Write-Host "                EVA & GUARANI - Translation Tools Runner                " -ForegroundColor Cyan
    Write-Host "             (For the entire EVA & GUARANI system, not just sandbox)    " -ForegroundColor Cyan
    Write-Host "========================================================================`n" -ForegroundColor Cyan
}

function Check-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow

    # Check if Python is installed
    try {
        $pythonVersion = python --version
        Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "  Please install Python 3.8 or later from https://python.org" -ForegroundColor Red
        exit 1
    }

    # Check for required packages
    try {
        $openaiInstalled = python -c "import openai" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ OpenAI package is installed" -ForegroundColor Green
        }
        else {
            Write-Host "Installing OpenAI package..." -ForegroundColor Yellow
            python -m pip install openai
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ OpenAI package installed successfully" -ForegroundColor Green
            }
            else {
                Write-Host "✗ Failed to install OpenAI package" -ForegroundColor Red
                exit 1
            }
        }
    }
    catch {
        Write-Host "✗ Error checking for OpenAI package: $_" -ForegroundColor Red
        exit 1
    }

    Write-Host "All prerequisites met`n" -ForegroundColor Green
}

function Show-Menu {
    Clear-Host
    $helpText = @"
=====================================================
  EVA & GUARANI Translation Tools - PowerShell
=====================================================

These tools help you translate files from Portuguese to English
and identify files containing Portuguese text.

LOCATION: $toolsDir

Available Tools:
1. Scan for Portuguese files
2. Translate a specific file
3. Batch translate files
4. Configure API key
5. Help
6. Exit

"@
    Write-Host $helpText

    $choice = Read-Host "Enter your choice (1-6)"
    return $choice
}

function Scan-Project {
    Write-Host "`nScanning project for Portuguese files...`n" -ForegroundColor Yellow

    # Default to the main EVA & GUARANI system root directory
    $defaultRootDir = Resolve-Path -Path "C:\Eva & Guarani - EGOS"

    if (-not (Test-Path $defaultRootDir)) {
        $defaultRootDir = Resolve-Path -Path "..\.."
    }

    Write-Host "This will scan the entire EVA & GUARANI system for Portuguese content." -ForegroundColor Yellow
    Write-Host "The scan will focus on project files and exclude system directories." -ForegroundColor Yellow
    Write-Host "This may take a few minutes depending on the size of your project." -ForegroundColor Yellow

    $rootDir = Read-Host "Enter root directory to scan (default: $defaultRootDir)"

    if ([string]::IsNullOrWhiteSpace($rootDir)) {
        $rootDir = $defaultRootDir
    }

    # Set default report file path
    $reportFile = Join-Path $toolsDir "translation_report.md"

    Write-Host "`nRunning scanner...`n" -ForegroundColor Yellow
    python translate_to_english.py --root-dir "$rootDir" --output "$reportFile"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nScan complete. Results saved to: $reportFile`n" -ForegroundColor Green

        # Check if any files were found
        $reportContent = Get-Content -Path $reportFile -Raw
        if ($reportContent -match "\| File \|") {
            Write-Host "Portuguese files were detected in your project." -ForegroundColor Yellow
            Write-Host "`nOptions:"
            Write-Host "1. Translate all detected files now"
            Write-Host "2. View the report first"
            Write-Host "3. Return to main menu"

            $translateOption = Read-Host "`nWhat would you like to do? (1-3)"

            if ($translateOption -eq "1") {
                Write-Host "`nStarting batch translation of all detected files...`n" -ForegroundColor Yellow
                Batch-Translate -reportFile $reportFile -autoConfirm $true
            }
            elseif ($translateOption -eq "2") {
                Write-Host "`nOpening report file...`n" -ForegroundColor Yellow
                Start-Process $reportFile

                Write-Host "After reviewing the report:"
                Write-Host "1. Translate all detected files"
                Write-Host "2. Return to main menu"

                $postReview = Read-Host "`nWhat would you like to do? (1-2)"

                if ($postReview -eq "1") {
                    Write-Host "`nStarting batch translation...`n" -ForegroundColor Yellow
                    Batch-Translate -reportFile $reportFile -autoConfirm $true
                }
            }
        }
        else {
            Write-Host "No Portuguese files were detected in your project." -ForegroundColor Green
        }
    }
    else {
        Write-Host "`nScan failed with error code $LASTEXITCODE`n" -ForegroundColor Red
    }

    Write-Host "Press any key to continue..."
    [void][System.Console]::ReadKey($true)
}

function Translate-File {
    Write-Host "`nTranslate a specific file using AI`n" -ForegroundColor Yellow

    $filePath = Read-Host "Enter the path to the file you want to translate"

    if (-not (Test-Path $filePath)) {
        Write-Host "`nFile does not exist: $filePath`n" -ForegroundColor Red
        Write-Host "Press any key to continue..."
        [void][System.Console]::ReadKey($true)
        return
    }

    # Priority: 1. Explicit API key parameter, 2. Environment variable OPENAI_API_KEY
    $apiKey = $APIKeyParameter # Use the parameter if provided
    if (-not $apiKey) {
        $apiKey = $env:OPENAI_API_KEY # Fallback to environment variable
    }

    if (-not $apiKey) {
        Write-Host "Error: No OpenAI API key provided via parameter or environment variable (OPENAI_API_KEY)." -ForegroundColor Red
        exit 1
    }

    $outputPath = Read-Host "Enter output file path (leave empty to replace original)"

    $outputParam = ""
    if ($outputPath) {
        $outputParam = "--output `"$outputPath`""
    }

    $dryRun = Read-Host "Do you want to perform a dry run (no changes will be made)? (y/N)"
    $dryRunParam = ""
    if ($dryRun -eq "y" -or $dryRun -eq "Y") {
        $dryRunParam = "--dry-run"
    }

    Write-Host "`nTranslating file..." -ForegroundColor Yellow

    $command = "python ai_translate_file.py --file `"$filePath`" $apiKeyParam $outputParam $dryRunParam"

    try {
        Invoke-Expression $command

        Write-Host "`nTranslation complete.`n" -ForegroundColor Green
    }
    catch {
        Write-Host "`nError during translation: $_`n" -ForegroundColor Red
    }

    Write-Host "Press any key to continue..."
    [void][System.Console]::ReadKey($true)
}

function Batch-Translate {
    param (
        [string]$reportFile = "",
        [bool]$autoConfirm = $false
    )

    if ([string]::IsNullOrEmpty($reportFile)) {
        Write-Host "`nBatch translate files from a translation report`n" -ForegroundColor Yellow

        $defaultReportFile = Join-Path $toolsDir "translation_report.md"
        $reportFile = Read-Host "Enter path to translation report (default: $defaultReportFile)"
        if ([string]::IsNullOrWhiteSpace($reportFile)) {
            $reportFile = $defaultReportFile
        }
    }

    if (-not (Test-Path $reportFile)) {
        Write-Host "Report file not found: $reportFile`n" -ForegroundColor Red
        Write-Host "Press any key to continue..."
        [void][System.Console]::ReadKey($true)
        return
    }

    if (-not $autoConfirm) {
        Write-Host "`nWill process files listed in: $reportFile" -ForegroundColor Yellow
        $confirm = Read-Host "Proceed with batch translation? (y/n)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            return
        }
    }

    Write-Host "`nIMPORTANT: This requires an OpenAI API key." -ForegroundColor Magenta

    # Priority: 1. Explicit API key parameter, 2. Environment variable OPENAI_API_KEY
    $apiKey = $APIKeyParameter # Use the parameter if provided
    if (-not $apiKey) {
        $apiKey = $env:OPENAI_API_KEY # Fallback to environment variable
    }

    if (-not $apiKey) {
        Write-Host "Error: No OpenAI API key provided via parameter or environment variable (OPENAI_API_KEY)." -ForegroundColor Red
        exit 1
    }

    if ($autoConfirm) {
        $apiKeyParam = ""
        $priority = "high"
        $dryRunParam = ""
    }
    else {
        $apiKey = Read-Host "Enter your OpenAI API key (or press Enter to use default key)"

        $apiKeyParam = ""
        if (-not [string]::IsNullOrWhiteSpace($apiKey)) {
            $apiKeyParam = "--api-key `"$apiKey`""
        }

        $priority = Read-Host "Process which priority files? (high/medium/low/all) (default: high)"
        if ([string]::IsNullOrWhiteSpace($priority)) {
            $priority = "high"
        }

        $dryRun = Read-Host "Run in dry-run mode (no changes will be made)? (y/n)"
        $dryRunParam = ""
        if ($dryRun -eq "y" -or $dryRun -eq "Y") {
            $dryRunParam = "--dry-run"
        }
    }

    Write-Host "`nStarting batch translation...`n" -ForegroundColor Yellow
    Write-Host "This may take some time depending on the number of files." -ForegroundColor Yellow

    # Use batch mode directly with the report file
    & python "$translatorScript" --batch "$reportFile" $apiKeyParam $dryRunParam --priority $priority

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nBatch translation completed successfully.`n" -ForegroundColor Green
    }
    else {
        Write-Host "`nBatch translation completed with some issues. Check the logs for details.`n" -ForegroundColor Yellow
    }

    Write-Host "Press any key to continue..."
    [void][System.Console]::ReadKey($true)
}

function Show-Help {
    Write-Host "`nEVA & GUARANI Translation Tools Help`n" -ForegroundColor Cyan
    Write-Host "These tools help you standardize the EVA & GUARANI codebase to English."
    Write-Host ""
    Write-Host "Available Tools:" -ForegroundColor Yellow
    Write-Host "1. Portuguese File Scanner (translate_to_english.py)"
    Write-Host "   - Identifies files containing Portuguese content"
    Write-Host "   - Generates a report listing files that need translation"
    Write-Host ""
    Write-Host "2. AI-Assisted Translator (ai_translate_file.py)"
    Write-Host "   - Uses OpenAI API to translate files from Portuguese to English"
    Write-Host "   - Preserves code structure and functionality"
    Write-Host ""
    Write-Host "3. Batch Translation"
    Write-Host "   - Processes multiple files from a translation report"
    Write-Host "   - Prioritizes files based on importance"
    Write-Host ""
    Write-Host "Documentation:" -ForegroundColor Yellow
    Write-Host "For detailed instructions, see:"
    Write-Host "- Translation Guide: ../docs/TRANSLATION_GUIDE.md"
    Write-Host "- System Analysis: ../docs/SYSTEM_ANALYSIS.md"
    Write-Host "- Implementation Roadmap: ../docs/IMPLEMENTATION_ROADMAP.md"
    Write-Host ""
    Write-Host "Press any key to continue..."
    [void][System.Console]::ReadKey($true)
}

# Main script execution
try {
    # Set working directory to the script's directory
    Set-Location -Path $PSScriptRoot

    Show-Header
    Check-Prerequisites

    $exit = $false
    while (-not $exit) {
        Show-Header
        $choice = Show-Menu

        switch ($choice) {
            "1" { Scan-Project }
            "2" { Translate-File }
            "3" { Batch-Translate }
            "4" { Show-Help }
            "5" { $exit = $true }
            default {
                Write-Host "`nInvalid choice. Please try again.`n" -ForegroundColor Red
                Start-Sleep -Seconds 1
            }
        }
    }

    Write-Host "`nThank you for using EVA & GUARANI Translation Tools!`n" -ForegroundColor Cyan
}
catch {
    Write-Host "An error occurred: $_" -ForegroundColor Red
    exit 1
}
