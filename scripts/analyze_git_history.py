import subprocess
import csv
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

REPO_PATH = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_PATH / 'analysis_results'
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / 'egos_git_analysis.csv'

def get_tracked_files(repo_path):
    try:
        result = subprocess.run(['git', 'ls-files'], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        files = result.stdout.strip().split('\n')
        return [f for f in files if f]
    except Exception as e:
        logging.error(f"Failed to get tracked files: {e}")
        return []

def analyze_file_history(repo_path, files):
    file_data = []
    for idx, file in enumerate(files):
        try:
            result = subprocess.run(
                ['git', 'log', '--follow', '--format=%cI', '--', file],
                cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            commit_dates = [d for d in result.stdout.strip().split('\n') if d]
            if commit_dates:
                first_commit = min(commit_dates)
                last_commit = max(commit_dates)
                dt_first = datetime.fromisoformat(first_commit)
                dt_last = datetime.fromisoformat(last_commit)
                lifespan_days = (dt_last - dt_first).total_seconds() / 86400
            else:
                first_commit = last_commit = ''
                lifespan_days = ''
            file_data.append([file, first_commit, last_commit, lifespan_days])
        except Exception as e:
            logging.warning(f"Failed to analyze {file}: {e}")
            file_data.append([file, '', '', ''])
        if (idx + 1) % 100 == 0:
            logging.info(f"Processed {idx+1}/{len(files)} files...")
    return file_data

def main():
    logging.info("Starting Git history analysis...")
    logging.info(f"Output will be saved to: {OUTPUT_CSV}")
    files = get_tracked_files(REPO_PATH)
    logging.info(f"Found {len(files)} tracked files.")
    logging.info("Analyzing commit history for each file (this may take a while)...")
    file_data = analyze_file_history(REPO_PATH, files)
    logging.info(f"Finished analyzing {len(files)} files.")
    logging.info(f"Writing results to {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filepath', 'FirstCommitDate', 'LastCommitDate', 'LifespanDays'])
        writer.writerows(file_data)
    logging.info("Successfully wrote results to CSV.")
    logging.info("Git history analysis complete.")

if __name__ == '__main__':
    main()
