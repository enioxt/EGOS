#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manages the Process ID (PID) file for CRONOS service to prevent multiple instances."""

import logging
import os
from pathlib import Path
import platform
import subprocess


class PidManager:
    """Handles creation, checking, and removal of the CRONOS PID file."""

    def __init__(self, pid_file_path: Path, logger: logging.Logger):
        """Initializes the PID Manager.

        Args:
            pid_file_path: The absolute path to the PID file.
            logger: The logger instance to use.
        """
        self.pid_file_path = pid_file_path
        self.logger = logger

    def check_and_create_pid(self):
        """Checks for an existing PID file and creates one if none is found
        or if the existing one is stale."""
        if self.pid_file_path.exists():
            try:
                self._check_pid_file()  # Raises RuntimeError if PID is active
            except (ValueError, OSError, ProcessLookupError):
                # Includes invalid PID int(), file read errors,
                # permission errors checking process
                self.logger.warning(
                    f"Stale or invalid PID file found: {self.pid_file_path}. Overwriting."
                )
            except Exception as e:  # Catch other potential errors reading/checking PID
                self.logger.error(
                    f"Error checking existing PID file {self.pid_file_path}: {e}", exc_info=True
                )
                raise  # Re-raise unexpected errors during PID check
        else:
            self._create_pid_file()

    def _check_pid_file(self):
        """Checks if a PID file exists and if the process it points to is running."""
        if self.pid_file_path.exists():
            try:
                pid_str = self.pid_file_path.read_text().strip()
                pid = int(pid_str)
                self.logger.info(f"Found existing PID file: {self.pid_file_path} with PID {pid}")

                # Check if process is running
                if platform.system() == "Windows":
                    # On Windows, os.kill doesn't exist. Use tasklist.
                    try:
                        # Check tasklist output, suppressing stderr
                        # to avoid messages if PID not found
                        subprocess.check_output(
                            f'tasklist /FI "PID eq {pid}"', shell=True, stderr=subprocess.STDOUT
                        )
                        # If the command succeeds and finds the task, the process is likely running.
                        error_msg = (
                            f"Another CRONOS instance may be running (PID: {pid}). "
                            f"PID file: {self.pid_file_path}. Aborting."
                        )
                        self.logger.critical(error_msg)
                        raise RuntimeError(
                            f"PID file {self.pid_file_path} exists and process {pid} is running."
                        )
                    except subprocess.CalledProcessError as e:
                        # Command fails if process not found - this is expected for a stale PID
                        output_str = e.output.decode(errors="ignore") if e.output else ""
                        if "No tasks found" in output_str:
                            stale_msg = (
                                f"PID {pid} from stale file {self.pid_file_path} not found. "
                                f"Assuming stale."
                            )
                            self.logger.warning(stale_msg)
                        else:
                            tasklist_error = (
                                f"Error checking process {pid} with tasklist: {output_str}"
                            )
                            self.logger.error(tasklist_error)
                            # Re-raise as OSError for consistent handling
                            raise OSError(f"Error checking process status for PID {pid}") from e
                else:  # Assume POSIX-like (Linux, macOS)
                    try:
                        os.kill(pid, 0)  # Check if process exists (sends null signal)
                        # If os.kill doesn't raise an error, the process exists
                        error_msg = (
                            f"Another CRONOS instance may be running (PID: {pid}). "
                            f"PID file: {self.pid_file_path}. Aborting."
                        )
                        self.logger.critical(error_msg)
                        raise RuntimeError(
                            f"PID file {self.pid_file_path} exists and process {pid} is running."
                        )
                    except ProcessLookupError:
                        # Process does not exist - PID file is stale
                        stale_msg = (
                            f"Stale PID file found: {self.pid_file_path}. "
                            f"Process {pid} not running. Overwriting."
                        )
                        self.logger.warning(stale_msg)
                    except PermissionError as pe:
                        # Cannot signal the process (maybe running as different user)
                        # Treat as potentially running for safety
                        self.logger.error(
                            f"Permission error checking process {pid}. "
                            f"Assuming it might be running. Aborting."
                        )
                        raise RuntimeError(
                            f"Permission error checking PID {pid} from file "
                            f"{self.pid_file_path}. Cannot guarantee single instance."
                        ) from pe
                    except (ValueError, OSError):  # Removed duplicate ProcessLookupError
                        # Includes invalid PID int(), file read errors,
                        # permission errors checking process
                        invalid_msg = (
                            f"Stale or invalid PID file found: {self.pid_file_path}. "
                            f"Containing PID {pid} which is not running or inaccessible."
                        )
                        self.logger.warning(invalid_msg)
                    except Exception as e:  # Catch other potential errors reading/checking PID
                        error_msg = f"Error checking existing PID file {self.pid_file_path}: {e}"
                        self.logger.error(error_msg, exc_info=True)
                        raise  # Re-raise unexpected errors during PID check

            except (ValueError, OSError, ProcessLookupError):
                # Includes invalid PID int(), file read errors, permission errors checking process
                self.logger.warning(
                    f"Stale or invalid PID file found: {self.pid_file_path}. Overwriting."
                )
            except Exception as e:  # Catch other potential errors reading/checking PID
                self.logger.error(
                    f"Error checking existing PID file {self.pid_file_path}: {e}", exc_info=True
                )
                raise  # Re-raise unexpected errors during PID check

    def _create_pid_file(self):
        """Creates the PID file with the current process ID."""
        try:
            self.pid_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pid_file_path, "w") as f:
                f.write(str(os.getpid()))
            self.logger.info(f"Created PID file: {self.pid_file_path} with PID {os.getpid()}")
        except (IOError, OSError) as e:
            self.logger.critical(
                f"Could not create PID file {self.pid_file_path}: {e}", exc_info=True
            )
            raise  # Cannot continue without PID file

    def remove_pid_file(self):
        """Removes the PID file if it belongs to the current process."""
        try:
            if self.pid_file_path.exists():
                try:
                    stored_pid = int(self.pid_file_path.read_text().strip())
                except (ValueError, IOError) as e:
                    self.logger.warning(
                        f"Could not read PID from {self.pid_file_path} "
                        f"during removal: {e}. Removing anyway."
                    )
                    stored_pid = -1  # Ensure it doesn't match current PID

                current_pid = os.getpid()
                if stored_pid == current_pid:
                    self.pid_file_path.unlink()
                    self.logger.info(f"Removed PID file: {self.pid_file_path}")
                else:
                    self.logger.warning(
                        f"PID file {self.pid_file_path} does not contain current "
                        f"PID ({current_pid}). Not removing."
                    )
        except (OSError, PermissionError) as e:
            self.logger.error(f"Error removing PID file {self.pid_file_path}: {e}", exc_info=True)
