from pathlib import Path
import sys

# Determine the project root directory using .parents attribute (attempt 3)
conftest_path = Path(__file__).resolve()
# parents[0]=tests, parents[1]=NEXUS, parents[2]=subsystems, parents[3]=Project Root
try:
    project_root = conftest_path.parents[3]
except IndexError:
    # Fallback if structure is different than expected
    print("Error: Could not determine project root using parents[3]. Falling back.")
    # Attempt previous logic as fallback
    project_root = Path(__file__).parent.parent.parent.resolve()

# Add the project root to the Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print(f"Attempting to add project root via .parents[3]: {project_root}")  # For verification

# You can also define fixtures here if needed later
