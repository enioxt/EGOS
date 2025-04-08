# File Size Analysis Tool

## Overview

This document provides tools and commands for analyzing file sizes within the EGOS codebase to enforce the [file modularity standard](../../.cursor/rules/file_modularity.mdc), which recommends keeping files under 300-500 lines for improved readability, maintainability, and AI processing.

## PowerShell Command for Finding Largest Files

The following PowerShell command quickly identifies the largest files in a codebase, helping pinpoint candidates for refactoring according to our file modularity rules:

```powershell
# Replace 'C:\\Eva Guarani EGOS' with the actual path to your project root
Get-ChildItem -Path 'C:\\Eva Guarani EGOS' -Recurse -Filter *.py | Sort-Object Length -Descending | Select-Object -First 10 | Format-Table Name, @{Name='Size (MB)';Expression={[math]::Round($_.Length / 1MB, 2)}}, Length -AutoSize
```

### Command Explanation

1. `Get-ChildItem -Path 'C:\\Eva Guarani EGOS' -Recurse -Filter *.py`: Finds all Python files recursively within the specified path.
2. `Sort-Object Length -Descending`: Sorts files by size (in bytes) in descending order.
3. `Select-Object -First 10`: Takes only the top 10 largest files.
4. `Format-Table`: Formats the output as a table with:
   - Filename
   - Size in MB (calculated and rounded to 2 decimal places)
   - Length in bytes

## Linux/Unix Command Alternative

For developers working on Linux, macOS, or other Unix-like systems, use this equivalent command:

```bash
# Replace /path/to/egos with the actual path to your project root
find /path/to/egos -name "*.py" -type f -exec ls -la {} \\; | sort -nrk 5 | head -n 10 | awk '{printf "%-50s %8.2f MB %12d bytes\\n", $9, $5/(1024*1024), $5}'
```

### Command Explanation

1. `find /path/to/egos -name "*.py" -type f`: Finds all Python files recursively
2. `-exec ls -la {} \\;`: Executes `ls -la` on each file to get detailed listing including size
3. `sort -nrk 5`: Sorts numerically in reverse order by the 5th column (file size)
4. `head -n 10`: Takes only the top 10 results
5. `awk '{printf...}'`: Formats the output nicely showing filename, size in MB, and size in bytes

### Benefits Over Line-Counting Methods

This approach focuses on file size rather than line count, which offers several advantages:

- **Performance**: Dramatically faster as it only reads file metadata, not content
- **Resource Efficiency**: Consumes minimal memory and CPU even on large codebases
- **Correlation with Complexity**: File size often correlates with complexity and is a reasonable proxy for identifying refactoring candidates

### Sample Output

```
Name             Size (MB)  Length
----             ---------  ------
core.py               1,48 1554066
core.py               1,48 1554066
channels.py           1,12 1177684
channels.py           1,12 1177684
_figurewidget.py      1,05 1096038
_figurewidget.py      1,05 1096038
_figure.py            1,04 1094857
_figure.py            1,04 1094857
generic.py            0,45  474370
generic.py            0,45  474370
```

## Git-Based Alternatives

When working with Git repositories, you might also need to identify large files in Git history (not just current working files). For these scenarios, consider these alternatives:

```bash
# Find largest blobs in the Git repository (includes ALL tracked files, even deleted ones)
git rev-list --objects --all \
| git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
| sed -n 's/^blob //p' \
| sort --numeric-sort --key=2 \
| tail -n 10 \
| cut -c 1-12,41- \
| $(command -v gnumfmt || echo numfmt) --field=2 --to=iec-i --suffix=B --padding=7 --round=nearest
```

However, the PowerShell command is preferred for day-to-day development as it's faster and focuses on current files.

## Usage in Development Workflow

1. **Regular Audits**: Run this command periodically (quarterly or after major feature additions) to identify refactoring candidates.
2. **Pre-Release Checks**: Include as part of release preparation to ensure codebase maintainability.
3. **New Contributor Onboarding**: Share this tool with new team members to help them understand our modularity standards.

## Integration with CI/CD (Future Enhancement)

Future work could include integrating this analysis into CI/CD pipelines to:

- Flag files exceeding size thresholds in pull requests
- Generate periodic reports on file size trends
- Automatically create issues for files exceeding thresholds

## Related KOIOS Standards

- [File Modularity](../../.cursor/rules/file_modularity.mdc)
- [Python Coding Standards](../../.cursor/rules/python_coding_standards.mdc)

## Contributions

This tool was developed and documented as part of EGOS's KOIOS standards evolution. Future improvements could include:

- Adding language-specific adaptations
- Creating a reusable PowerShell module
- Building visual reports of file size distribution

---

**Last Updated**: 2025-04-08  
**Author**: EGOS Team  
**Subsystem**: KOIOS
