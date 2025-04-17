import re
import argparse
from pathlib import Path
import logging

# Basic Logging Setup
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# KOIOS Task Format Regex (Expanded to capture groups for reconstruction)
# *   [Status] [SubSystem(s)][TaskID] Description (`Priority`) Optional_Status Optional_Depends
# Making TaskID optional initially to catch lines missing it.
TASK_REGEX_STRICT = re.compile(
    r"^(\*\s+\[(DONE|In Progress|Planned|Blocked)\]\s+\[([A-Z/]+)\]\[([A-Z0-9-]+)\]\s+)(.*?)\s+\(`(CRITICAL|HIGH|MEDIUM|LOW)`\)((?:\s+Status:\s+\w+)?(?:\s+depends_on:\s+\[[A-Z0-9,\s-]+\])?)$"
)

# Regex to catch lines that *look* like tasks but might be missing components
TASK_REGEX_LOOSE = re.compile(
    r"^(\*\s+\[(DONE|In Progress|Planned|Blocked)\]\s+)(.*?)\s+\(`(CRITICAL|HIGH|MEDIUM|LOW)`\)(.*)$"
)

# Regex to find just the Task ID part if present
TASK_ID_PART_REGEX = re.compile(r"\[([A-Z/]+)\]\[([A-Z0-9-]+)\]")


def attempt_fix_task_format(line: str, line_num: int) -> str:
    """Tries to heuristically correct a task line to match KOIOS format."""
    original_line = line
    line = line.strip()

    # If it already matches strictly, return as is
    if TASK_REGEX_STRICT.match(line):
        return original_line.strip() # Return stripped original if it was already compliant

    match_loose = TASK_REGEX_LOOSE.match(line)
    if match_loose:
        prefix = match_loose.group(1) # e.g., '*   [DONE] '
        status = match_loose.group(2)
        middle = match_loose.group(3).strip()
        priority_part = f"(`{match_loose.group(4)}`)"
        suffix = match_loose.group(5).strip() # Optional Status, Depends

        # Check if middle part already contains Task ID
        id_match = TASK_ID_PART_REGEX.search(middle)
        if id_match:
            # Already has ID, maybe just spacing or structure is off
            # Reconstruct carefully
            subsystem = id_match.group(1)
            task_id = id_match.group(2)
            # Extract description *after* the ID part
            desc_start_index = middle.find(f"[{task_id}]") + len(f"[{task_id}]")
            description = middle[desc_start_index:].strip()
            reconstructed = f"{prefix}[{subsystem}][{task_id}] {description} {priority_part}{suffix}"
            logging.info(f"Reformatted Line {line_num}: '{line}' -> '{reconstructed}'")
            return reconstructed
        else:
            # Missing Task ID - Assign placeholder
            subsystem = "UNKNOWN"
            task_id = f"TASK-TODO-{line_num}"
            description = middle # Use the whole middle part as description
            fixed_line = f"{prefix}[{subsystem}][{task_id}] {description} {priority_part}{suffix}"
            logging.warning(f"Assigned Placeholder ID Line {line_num}: '{line}' -> '{fixed_line}'")
            return fixed_line
    else:
        # Doesn't even match loosely, likely not a standard task format
        logging.error(f"Cannot parse Line {line_num}: {line}")
        return original_line # Return original, maybe add a comment?
        # return f"{original_line.strip()} # <<< KOIOS FORMAT ERROR?"

    return original_line # Fallback


def process_roadmap_file(roadmap_file: Path, output_file: Path):
    """Reads roadmap, attempts format correction, writes to new file."""
    if not roadmap_file.is_file():
        logging.error(f"Roadmap file not found at {roadmap_file}")
        return

    corrected_lines = []
    corrections_made = 0
    errors_found = 0

    try:
        with open(roadmap_file, 'r', encoding='utf-8') as f_in:
            for line_num, line in enumerate(f_in, 1):
                stripped_line = line.strip()
                # Only process lines that look like potential tasks
                if stripped_line.startswith("*") and "[`" in stripped_line:
                    corrected_line = attempt_fix_task_format(stripped_line, line_num)
                    if corrected_line != stripped_line:
                        corrections_made += 1
                    if "# <<< KOIOS FORMAT ERROR?" in corrected_line:
                        errors_found += 1
                    corrected_lines.append(corrected_line)
                else:
                    # Keep non-task lines (headers, blank lines, comments) as is
                    corrected_lines.append(line.rstrip()) # Use rstrip to preserve indentation if any

    except Exception as e:
        logging.error(f"Error reading roadmap file: {e}")
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(corrected_lines))
        logging.info(f"Processed roadmap written to: {output_file}")
        logging.info(f"Attempted corrections on {corrections_made} lines.")
        if errors_found:
            logging.warning(f"Found {errors_found} lines that could not be parsed/corrected.")

    except Exception as e:
        logging.error(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate and attempt to auto-correct KOIOS task format in ROADMAP.md.")
    parser.add_argument(
        "roadmap_path",
        type=Path,
        nargs='?',
        default=Path("ROADMAP.md"),
        help="Path to the source ROADMAP.md file (default: ./ROADMAP.md)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("ROADMAP_standardized.md"),
        help="Path for the output standardized roadmap file (default: ./ROADMAP_standardized.md)"
    )
    args = parser.parse_args()

    # Adjust relative paths based on script location
    script_dir = Path(__file__).parent.parent.parent # Go up from scripts/validation

    if args.roadmap_path.name == "ROADMAP.md" and not args.roadmap_path.is_absolute():
        roadmap_file_path = (script_dir / args.roadmap_path).resolve()
    else:
        roadmap_file_path = args.roadmap_path.resolve()

    if args.output.name == "ROADMAP_standardized.md" and not args.output.is_absolute():
         output_file_path = (script_dir / args.output).resolve()
    else:
         output_file_path = args.output.resolve()

    logging.info(f"Reading from: {roadmap_file_path}")
    logging.info(f"Writing to: {output_file_path}")

    process_roadmap_file(roadmap_file_path, output_file_path)
