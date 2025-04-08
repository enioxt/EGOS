#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ETHIK Service
=============================

Orchestrates the ETHIK subsystem components (Validator, Sanitizer).
Manages initialization, Mycelium communication setup, and lifecycle.

Version: 8.0.0
Ethical Awareness: 0.999
Love: 0.999
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

# Import Koios Logger utility
from subsystems.KOIOS.core.logging import get_koios_logger

# Import Mycelium Interface
from subsystems.MYCELIUM.core.interface import MyceliumInterface

from .core.sanitizer import EthikSanitizer

# Import core components
from .core.validator import EthikValidator

# Configure logging - Use Koios Logger instead of basicConfig
# logger = logging.getLogger("ethik_service")
# handler = logging.StreamHandler()
# formatter = logging.Formatter('💖 %(asctime)s - [ETHIK Service] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)


class EthikService:
    """Manages the ETHIK subsystem's operations and components."""

    def __init__(
        self, config: Dict[str, Any], mycelium_interface: MyceliumInterface, project_root: Path
    ):
        """Initialize the ETHIK Service.

        Args:
            config: Configuration dictionary for the ETHIK subsystem.
            mycelium_interface: An instance of the MyceliumInterface.
            project_root: The absolute path to the project's root directory.
        """
        self.config = config
        self.interface = mycelium_interface
        self.node_id = "ETHIK_SERVICE"
        self.running = False
        self.project_root = project_root

        # --- Setup Loggers using Koios --- #
        log_config = self.config.get("logging", {})
        self.logger = get_koios_logger(f"EGOS.{self.node_id}", config=log_config)
        validator_logger = get_koios_logger("EGOS.ETHIK.Validator", config=log_config)
        sanitizer_logger = get_koios_logger("EGOS.ETHIK.Sanitizer", config=log_config)
        # --------------------------------- #

        # Extract specific configs if needed, or pass the whole dict
        validator_config = self.config.get("validator_config", {})
        sanitizer_config = self.config.get("sanitizer_config", {})

        # --- Resolve Absolute Paths for Rule Files ---
        # Get relative paths from config
        validation_rules_rel_path = validator_config.get("rules_file") or self.config.get(
            "validation_rules_file", "config/validation_rules.json"
        )
        sanitization_rules_rel_path = sanitizer_config.get("rules_file") or self.config.get(
            "sanitization_rules_file", "config/sanitization_rules.json"
        )

        # Create absolute paths using project_root
        validator_rules_abs_path = (self.project_root / validation_rules_rel_path).resolve()
        sanitizer_rules_abs_path = (self.project_root / sanitization_rules_rel_path).resolve()

        # Update the component-specific configs with absolute paths
        validator_config["rules_file"] = str(validator_rules_abs_path)
        sanitizer_config["rules_file"] = str(sanitizer_rules_abs_path)
        # ---------------------------------------------

        # Add main config sections needed by components
        validator_config["history_retention_days"] = self.config.get("history_retention_days", 30)
        sanitizer_config["history_retention_days"] = self.config.get("history_retention_days", 30)
        sanitizer_config["performance"] = self.config.get("performance", {})

        # Instantiate core components with updated config and dedicated loggers
        self.validator = EthikValidator(validator_config, self.interface, validator_logger)
        self.sanitizer = EthikSanitizer(sanitizer_config, self.interface, sanitizer_logger)

        self.logger.info("ETHIK Service initialized with KoiosLogger.")

    async def start(self):
        """Start the ETHIK service and its components."""
        if self.running:
            self.logger.warning("ETHIK Service is already running.")
            return

        self.logger.info("Starting ETHIK Service...")
        # Ensure Mycelium connection is active (responsibility might be higher up)
        # if not self.interface.is_connected():
        #     await self.interface.connect()

        # Start components
        await self.validator.start_monitoring()
        await self.sanitizer.start_monitoring()

        self.running = True
        self.logger.info("ETHIK Service started successfully.")

    async def stop(self):
        """Stop the ETHIK service and its components."""
        if not self.running:
            self.logger.warning("ETHIK Service is not running.")
            return

        self.logger.info("Stopping ETHIK Service...")
        # Stop components
        await self.validator.stop_monitoring()
        await self.sanitizer.stop_monitoring()

        # Disconnect Mycelium (responsibility might be higher up)
        # await self.interface.disconnect()

        self.running = False
        self.logger.info("ETHIK Service stopped.")


# Example of how this service might be run (e.g., from a main script)
# Needs update to reflect KoiosLogger usage if run standalone
async def main():
    # --- Determine Project Root (Needs reliable method) ---
    try:
        project_root = Path(__file__).parent.parent.parent.resolve()
        print(f"Determined project root: {project_root}")  # Use print for basic example
    except Exception as e:
        print(f"Could not determine project root: {e}")
        return
    # -----------------------------

    # --- Setup Basic Logging for Example --- #
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    # --------------------------------------- #

    # Load configuration (replace with actual config loading, perhaps relative to root)
    config_path = project_root / "config" / "ethik_config.json"  # Example path
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            logging.info(f"Loaded ETHIK config from {config_path}")
        except Exception as e:
            logging.error(f"Failed to load ETHIK config from {config_path}: {e}. Using defaults.")
    else:
        logging.warning(f"ETHIK config not found at {config_path}. Using defaults.")

    # Apply defaults if needed (example)
    config.setdefault("validation_rules_file", "config/validation_rules.json")
    config.setdefault("sanitization_rules_file", "config/sanitization_rules.json")
    config.setdefault("history_retention_days", 7)
    config.setdefault("validator_config", {}).setdefault("ethical_threshold", 0.7)
    config.setdefault("sanitizer_config", {})
    config.setdefault("performance", {}).setdefault("caching", {"max_size": 100})
    # Add logging config section for Koios example
    config["logging"] = {"level": "INFO"}

    # Initialize Mycelium (replace with actual interface init)
    mycelium_interface = MyceliumInterface(node_id="ETHIK_Main")  # Example
    # Assume connect happens elsewhere or here:
    # await mycelium_interface.connect(...)

    # Pass resolved project_root to the service
    ethik_service = EthikService(config, mycelium_interface, project_root)

    try:
        await ethik_service.start()
        # Keep the service running (e.g., wait indefinitely or handle termination)
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logging.info("Shutdown signal received.")  # Use standard logging here
    finally:
        await ethik_service.stop()
        # Ensure Mycelium disconnects if managed here
        # await mycelium_interface.disconnect()


if __name__ == "__main__":
    # Added json import for example main
    import json

    # Basic logging setup moved inside main() for the example run
    print("Running ETHIK Service example...")
    try:
        asyncio.run(main())
    except Exception as e:
        # Use root logger for critical failure before service logger is set up
        logging.critical(f"ETHIK Service example failed: {e}", exc_info=True)
