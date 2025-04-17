import subprocess
import csv
from datetime import datetime, timezone
from pathlib import Path
import logging
from typing import List, Tuple, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPO_PATH: Path = Path(__file__).resolve().parent.parent
OUTPUT_DIR: Path = REPO_PATH / 'analysis_results'
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_CSV: Path = OUTPUT_DIR / 'egos_git_analysis.csv'

def get_tracked_files(repo_path: Path) -> List[str]:
    """Retrieves a list of all files currently tracked by Git in the repo.

    Args:
        repo_path: The path to the Git repository.

    Returns:
        A list of tracked file paths relative to the repo root, or empty list on error.
    """
    try:
        # Use git ls-files which is generally reliable for tracked files
        result = subprocess.run(
            ['git', 'ls-files'],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True, # Raises CalledProcessError on non-zero exit
            encoding='utf-8' # Explicitly set encoding
        )
        files = result.stdout.strip().split('\n')
        # Filter out potential empty strings if the output ends with a newline
        return [f for f in files if f]
    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed while getting tracked files: {e}")
        logging.error(f"Stderr: {e.stderr}")
        return []
    except FileNotFoundError:
        logging.error(f"'git' command not found. Is Git installed and in PATH?")
        return []
    except Exception as e:
        # Catch other potential errors like permission issues
        logging.error(f"An unexpected error occurred while getting tracked files: {e}")
        return []

def analyze_file_history(repo_path: Path, files: List[str]) -> List[List[Optional[str]]]:
    """Analyzes the Git commit history for a list of files.

    Args:
        repo_path: The path to the Git repository.
        files: A list of file paths (relative to repo root) to analyze.

    Returns:
        A list of lists, where each inner list contains:
        [filepath, first_commit_iso_date, last_commit_iso_date, lifespan_days_str].
        Returns empty strings for dates/lifespan on error for a specific file.
    """
    file_data: List[List[Optional[str]]] = []
    total_files = len(files)
    logging.info(f"Analyzing commit history for {total_files} files...")

    for idx, file in enumerate(files):
        try:
            # Use --follow to track file history across renames/moves
            # Use %cI for ISO 8601 commit date (strict ISO format)
            result = subprocess.run(
                ['git', 'log', '--follow', '--format=%cI', '--', file],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True, # Raise error on failure
                encoding='utf-8'
            )
            commit_dates_iso = [d for d in result.stdout.strip().split('\n') if d]

            if commit_dates_iso:
                # Parse ISO dates, which include timezone info
                commit_datetimes = [datetime.fromisoformat(d) for d in commit_dates_iso]
                dt_first: datetime = min(commit_datetimes)
                dt_last: datetime = max(commit_datetimes)

                # Ensure consistent timezone handling (convert to UTC for lifespan calculation)
                lifespan_seconds = (dt_last.astimezone(timezone.utc) - dt_first.astimezone(timezone.utc)).total_seconds()
                lifespan_days = lifespan_seconds / 86400
                lifespan_days_str = f"{lifespan_days:.2f}" # Format to 2 decimal places
                first_commit_str = dt_first.isoformat()
                last_commit_str = dt_last.isoformat()
            else:
                # Should not happen if ls-files returned it, but handle defensively
                first_commit_str = None
                last_commit_str = None
                lifespan_days_str = None
                logging.warning(f"No commit dates found for tracked file: {file}")

            file_data.append([file, first_commit_str, last_commit_str, lifespan_days_str])

        except subprocess.CalledProcessError as e:
            logging.warning(f"Git command failed for file '{file}': {e}. Stderr: {e.stderr}")
            file_data.append([file, None, None, None])
        except ValueError as e:
            # Handle potential date parsing errors
            logging.warning(f"Could not parse commit dates for file '{file}': {e}")
            file_data.append([file, None, None, None])
        except Exception as e:
            # Catch-all for other unexpected errors during analysis of a single file
            logging.warning(f"An unexpected error occurred analyzing file '{file}': {e}")
            file_data.append([file, None, None, None])

        # Log progress periodically
        if (idx + 1) % 100 == 0 or (idx + 1) == total_files:
            logging.info(f"Processed {idx+1}/{total_files} files...")

    return file_data

def main():
    """Main function to execute the Git history analysis."""
    logging.info("Starting Git history analysis...")
    logging.info(f"Repository path: {REPO_PATH}")
    logging.info(f"Output will be saved to: {OUTPUT_CSV}")

    files = get_tracked_files(REPO_PATH)
    if not files:
        logging.error("No tracked files found or error retrieving them. Exiting.")
        return

    logging.info(f"Found {len(files)} tracked files.")

    file_data = analyze_file_history(REPO_PATH, files)

    logging.info(f"Finished analyzing files.")
    logging.info(f"Writing results to {OUTPUT_CSV}...")

    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Filepath', 'FirstCommitDateISO', 'LastCommitDateISO', 'LifespanDays'])
            writer.writerows(file_data)
        logging.info(f"Successfully wrote results to {OUTPUT_CSV}.")
    except IOError as e:
        logging.error(f"Failed to write results to CSV file {OUTPUT_CSV}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while writing the CSV: {e}")

    logging.info("Git history analysis complete.")

if __name__ == '__main__':
    main()
