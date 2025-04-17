# CRONOS Refactoring Example: Retention Policy

This document provides a concrete example of how to refactor the complex `_apply_retention_policy` method in the CRONOS service to improve readability, maintainability, and testability.

## Original Method

```python
def _apply_retention_policy(
    self,
    sorted_backups: List[SystemBackupInfo],
    retention_days: Dict[str, int],
    now: datetime
) -> Dict[str, SystemBackupInfo]:
    """Applies retention policy to sorted backups and returns map of backups to keep."""
    kept_backups_map: Dict[str, SystemBackupInfo] = {}
    kept_counts = {"daily": 0, "weekly": 0, "monthly": 0}
    last_kept_week = -1
    last_kept_month = -1

    for backup in sorted_backups:
        age_days = (now - backup.timestamp).days
        backup_week = backup.timestamp.isocalendar()[1]
        backup_month = backup.timestamp.month

        keep_reason = None

        # Keep daily backups
        if retention_days.get("daily", 0) > 0 and age_days < retention_days["daily"]:
            if backup.id not in kept_backups_map:
                keep_reason = "daily"
                kept_counts["daily"] += 1

        # Keep weekly backups (first of the week within retention period)
        elif retention_days.get("weekly", 0) > 0 and age_days < retention_days["weekly"]:
            if backup_week != last_kept_week:
                if backup.id not in kept_backups_map:
                    keep_reason = "weekly"
                    kept_counts["weekly"] += 1
                    last_kept_week = backup_week

        # Keep monthly backups (first of the month within retention period)
        elif retention_days.get("monthly", 0) > 0 and age_days < retention_days["monthly"]:
            if backup_month != last_kept_month:
                if backup.id not in kept_backups_map:
                    keep_reason = "monthly"
                    kept_counts["monthly"] += 1
                    last_kept_month = backup_month

        if keep_reason:
            kept_backups_map[backup.id] = backup
            backup.retention_category = keep_reason # Tag the backup info

    self.logger.info(f"Retention Policy Applied: Kept Daily={kept_counts['daily']}, Weekly={kept_counts['weekly']}, Monthly={kept_counts['monthly']}")
    return kept_backups_map
```

## Refactored Solution

```python
def _apply_retention_policy(
    self,
    sorted_backups: List[SystemBackupInfo],
    retention_days: Dict[str, int],
    now: datetime
) -> Dict[str, SystemBackupInfo]:
    """Applies retention policy to sorted backups and returns map of backups to keep.

    Args:
        sorted_backups: List of backups sorted by timestamp (newest first)
        retention_days: Dictionary with retention periods for different categories
        now: Current datetime for age calculation

    Returns:
        Dictionary mapping backup IDs to backup objects that should be kept
    """
    policy_tracker = RetentionPolicyTracker()
    kept_backups_map: Dict[str, SystemBackupInfo] = {}

    for backup in sorted_backups:
        retention_category = self._determine_retention_category(
            backup, retention_days, now, policy_tracker
        )

        if retention_category:
            kept_backups_map[backup.id] = backup
            backup.retention_category = retention_category

    self._log_retention_results(policy_tracker.kept_counts)
    return kept_backups_map

def _determine_retention_category(
    self,
    backup: SystemBackupInfo,
    retention_days: Dict[str, int],
    now: datetime,
    policy_tracker: 'RetentionPolicyTracker'
) -> Optional[str]:
    """Determines which retention category (if any) a backup falls into.

    Args:
        backup: The backup to evaluate
        retention_days: Dictionary with retention periods for different categories
        now: Current datetime for age calculation
        policy_tracker: Tracker object to maintain state across evaluations

    Returns:
        The retention category if the backup should be kept, None otherwise
    """
    age_days = (now - backup.timestamp).days

    # Check if backup should be kept for daily retention
    if self._should_keep_daily(backup, age_days, retention_days, policy_tracker):
        return "daily"

    # Check if backup should be kept for weekly retention
    if self._should_keep_weekly(backup, age_days, retention_days, policy_tracker):
        return "weekly"

    # Check if backup should be kept for monthly retention
    if self._should_keep_monthly(backup, age_days, retention_days, policy_tracker):
        return "monthly"

    return None

def _should_keep_daily(
    self,
    backup: SystemBackupInfo,
    age_days: int,
    retention_days: Dict[str, int],
    policy_tracker: 'RetentionPolicyTracker'
) -> bool:
    """Determines if a backup should be kept based on daily retention policy.

    Args:
        backup: The backup to evaluate
        age_days: Age of the backup in days
        retention_days: Dictionary with retention periods for different categories
        policy_tracker: Tracker object to maintain state across evaluations

    Returns:
        True if the backup should be kept for daily retention, False otherwise
    """
    if retention_days.get("daily", 0) <= 0 or age_days >= retention_days["daily"]:
        return False

    if backup.id in policy_tracker.kept_backup_ids:
        return False

    policy_tracker.kept_counts["daily"] += 1
    policy_tracker.kept_backup_ids.add(backup.id)
    return True

def _should_keep_weekly(
    self,
    backup: SystemBackupInfo,
    age_days: int,
    retention_days: Dict[str, int],
    policy_tracker: 'RetentionPolicyTracker'
) -> bool:
    """Determines if a backup should be kept based on weekly retention policy.

    Args:
        backup: The backup to evaluate
        age_days: Age of the backup in days
        retention_days: Dictionary with retention periods for different categories
        policy_tracker: Tracker object to maintain state across evaluations

    Returns:
        True if the backup should be kept for weekly retention, False otherwise
    """
    if retention_days.get("weekly", 0) <= 0 or age_days >= retention_days["weekly"]:
        return False

    backup_week = backup.timestamp.isocalendar()[1]
    if backup_week == policy_tracker.last_kept_week:
        return False

    if backup.id in policy_tracker.kept_backup_ids:
        return False

    policy_tracker.last_kept_week = backup_week
    policy_tracker.kept_counts["weekly"] += 1
    policy_tracker.kept_backup_ids.add(backup.id)
    return True

def _should_keep_monthly(
    self,
    backup: SystemBackupInfo,
    age_days: int,
    retention_days: Dict[str, int],
    policy_tracker: 'RetentionPolicyTracker'
) -> bool:
    """Determines if a backup should be kept based on monthly retention policy.

    Args:
        backup: The backup to evaluate
        age_days: Age of the backup in days
        retention_days: Dictionary with retention periods for different categories
        policy_tracker: Tracker object to maintain state across evaluations

    Returns:
        True if the backup should be kept for monthly retention, False otherwise
    """
    if retention_days.get("monthly", 0) <= 0 or age_days >= retention_days["monthly"]:
        return False

    backup_month = backup.timestamp.month
    if backup_month == policy_tracker.last_kept_month:
        return False

    if backup.id in policy_tracker.kept_backup_ids:
        return False

    policy_tracker.last_kept_month = backup_month
    policy_tracker.kept_counts["monthly"] += 1
    policy_tracker.kept_backup_ids.add(backup.id)
    return True

def _log_retention_results(self, kept_counts: Dict[str, int]) -> None:
    """Logs the results of applying the retention policy.

    Args:
        kept_counts: Dictionary with counts of backups kept by category
    """
    self.logger.info(
        f"Retention Policy Applied: "
        f"Kept Daily={kept_counts['daily']}, "
        f"Weekly={kept_counts['weekly']}, "
        f"Monthly={kept_counts['monthly']}"
    )

class RetentionPolicyTracker:
    """Helper class to track state during retention policy application."""

    def __init__(self):
        """Initialize the retention policy tracker."""
        self.kept_counts = {"daily": 0, "weekly": 0, "monthly": 0}
        self.last_kept_week = -1
        self.last_kept_month = -1
        self.kept_backup_ids = set()
```

## Benefits of the Refactored Solution

1. **Single Responsibility Principle**
   - Each method has a clear, focused purpose
   - Logic for each retention type is isolated

2. **Improved Readability**
   - Shorter methods with descriptive names
   - Clear control flow

3. **Enhanced Testability**
   - Each helper method can be unit tested independently
   - Mock objects can be used for the tracker

4. **Better Documentation**
   - Comprehensive docstrings for all methods
   - Clear explanation of parameters and return values

5. **Maintainability**
   - Easier to modify or extend specific retention rules
   - State tracking is encapsulated in a dedicated class

6. **Reduced Cyclomatic Complexity**
   - Main method has linear flow with fewer branches
   - Helper methods encapsulate individual decision logic

## Testing Strategy

```python
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

class TestRetentionPolicy(unittest.TestCase):
    def setUp(self):
        self.service = CronosService(config={}, mycelium_interface=MagicMock(), project_root=Path("."))
        self.now = datetime(2023, 5, 15)
        self.tracker = RetentionPolicyTracker()

    def test_should_keep_daily(self):
        # Create a backup from yesterday
        backup = SystemBackupInfo(
            id="backup_20230514",
            name="Daily Backup",
            timestamp=self.now - timedelta(days=1),
            location=Path(".")
        )

        # Test with valid retention period
        retention_days = {"daily": 7, "weekly": 30, "monthly": 90}
        age_days = 1

        result = self.service._should_keep_daily(
            backup, age_days, retention_days, self.tracker
        )

        self.assertTrue(result)
        self.assertEqual(1, self.tracker.kept_counts["daily"])
        self.assertIn(backup.id, self.tracker.kept_backup_ids)

    def test_should_not_keep_daily_too_old(self):
        # Create a backup from 10 days ago
        backup = SystemBackupInfo(
            id="backup_20230505",
            name="Old Backup",
            timestamp=self.now - timedelta(days=10),
            location=Path(".")
        )

        # Test with valid retention period
        retention_days = {"daily": 7, "weekly": 30, "monthly": 90}
        age_days = 10

        result = self.service._should_keep_daily(
            backup, age_days, retention_days, self.tracker
        )

        self.assertFalse(result)
        self.assertEqual(0, self.tracker.kept_counts["daily"])

    # Similar tests for weekly and monthly retention
    # ...
```

## Implementation Notes

1. The `RetentionPolicyTracker` class encapsulates the state that was previously tracked through local variables.
2. Each retention category has a dedicated method with clear logic.
3. The main method is now a high-level orchestrator that delegates specific decisions to helper methods.
4. Exception handling would be added to the main and helper methods following the specific exception patterns outlined in the recommendations document.
