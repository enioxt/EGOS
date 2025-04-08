# Git Bash Command Reference

This reference document provides the correct command syntax for Git Bash, to ensure all operations work properly in the EVA & GUARANI EGOS project.

## Navigation Commands

```bash
# Change directory - use Unix-style paths with forward slashes
cd /c/Eva\ Guarani\ EGOS

# Navigate to subdirectory
cd QUANTUM_PROMPTS/MASTER

# Go up one directory
cd ..

# List directory contents
ls
# or with details
ls -la

# List directory contents with hidden files
ls -a
```

## File and Directory Operations

```bash
# Create directory
mkdir new_directory

# Create nested directories (equivalent to mkdir -p)
mkdir -p path/to/nested/directories

# Create a file
touch filename.txt

# Copy a file
cp source.txt destination.txt

# Move or rename a file
mv source.txt destination.txt

# Delete a file
rm filename.txt

# Delete an empty directory
rmdir directory_name

# Delete a directory and its contents
rm -rf directory_name

# Check if file exists
[ -f filename.txt ] && echo "Exists" || echo "Does not exist"
```

## Command Chaining

```bash
# Use semicolon to chain commands
cd /c/Eva\ Guarani\ EGOS; ls -la

# AND operator (run second command only if first succeeds)
cd /c/Eva\ Guarani\ EGOS && ls -la

# OR operator (run second command only if first fails)
cd /c/Eva\ Guarani\ EGOS || echo "Failed to change directory"

# Pipe output of one command to another
ls -la | grep "README"
```

## Running Python and Other Commands

```bash
# Run Python script
python script.py

# Run Python module
python -m http.server 3000

# Install Python package
pip install -r requirements.txt

# Run tests with pytest
pytest tests/
```

## Git Commands

```bash
# Check status of repository
git status

# Add files to staging
git add filename.txt
# Add all files
git add .

# Commit changes
git commit -m "Commit message"

# Push to remote
git push origin main

# Pull from remote
git pull origin main

# Create a new branch
git checkout -b new-branch-name

# Switch to an existing branch
git checkout branch-name

# View commit history
git log
```

## Environment Variables

```bash
# Set environment variable for current session
export VARIABLE_NAME="value"

# Read environment variable
echo $VARIABLE_NAME

# List all environment variables
env
```

## Important Notes

1. Git Bash uses Unix-style paths with forward slashes (`/`), not backslashes (`\`)
2. Use backslashes (`\`) to escape spaces in paths: `/c/Eva\ Guarani\ EGOS`
3. Windows drives are referenced as `/c/`, `/d/`, etc. instead of `C:\`, `D:\`
4. Git Bash is case-sensitive, unlike Windows PowerShell
5. Some Windows-specific commands may not work in Git Bash
6. Use `-p` flag with mkdir to create nested directories
7. The working directory persists between commands in a single session

## Conversion between Windows and Git Bash Paths

| Windows Path | Git Bash Path |
|--------------|--------------|
| `C:\Users\Username` | `/c/Users/Username` |
| `C:\Program Files\Git` | `/c/Program\ Files/Git` |
| `D:\Projects\Eva Guarani EGOS` | `/d/Projects/Eva\ Guarani\ EGOS` |

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
