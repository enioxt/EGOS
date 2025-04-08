#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - NEXUS Service
=============================

Orchestrates the NEXUS subsystem for modular code analysis.
Handles configuration, manages NEXUSCore, and integrates with Mycelium.

Version: 1.0.0
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

# Import Koios Logger utility
from subsystems.KOIOS.core.logging import get_koios_logger

# Import Mycelium Interface
from subsystems.MYCELIUM.core.interface import MyceliumInterface

# Import core component
from .core.nexus_core import NEXUSCore

# Configure logging for the service - Use Koios Logger
# logger = logging.getLogger("nexus_service")
# handler = logging.StreamHandler()
# formatter = logging.Formatter('🧩 %(asctime)s - [NEXUS Service] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)


class NexusService:
    """Manages the NEXUS subsystem's operations."""

    def __init__(
        self, config: Dict[str, Any], mycelium_interface: MyceliumInterface, project_root: Path
    ):
        """Initialize the NEXUS Service.

        Args:
            config: Configuration dictionary for the NEXUS subsystem.
            mycelium_interface: An instance of the MyceliumInterface.
            project_root: The absolute path to the project's root directory.
        """
        self.config = config
        self.interface = mycelium_interface
        self.project_root = project_root
        self.node_id = "NEXUS_SERVICE"
        self.running = False

        # --- Setup Loggers using Koios --- #
        log_config = self.config.get("logging", {})
        self.logger = get_koios_logger(f"EGOS.{self.node_id}", config=log_config)
        # Store the core logger as an instance attribute
        self.nexus_core_logger = get_koios_logger("EGOS.NEXUS.Core", config=log_config)
        # ---------------------------------

        # --- Setup Logger for NEXUSCore ---
        # self.nexus_core_logger = logging.getLogger("NEXUS") # Match name used in core
        # log_level_str = self.config.get("log_level", "INFO").upper()
        # self.nexus_core_logger.setLevel(getattr(logging, log_level_str, logging.INFO))
        # if not self.nexus_core_logger.handlers:
        #      core_handler = logging.StreamHandler()
        #      core_formatter = logging.Formatter('🧩 %(asctime)s - [NEXUS Core] %(message)s')
        #      core_handler.setFormatter(core_formatter)
        #      self.nexus_core_logger.addHandler(core_handler)
        #      self.nexus_core_logger.propagate = False
        # ---------------------------------

        # --- Instantiate NEXUSCore ---
        nexus_core_config = self.config.get("core_config", {})  # Pass specific core config
        self.nexus_core = NEXUSCore(
            config=nexus_core_config,
            logger=self.nexus_core_logger,  # Pass the instance attribute logger
            project_root=self.project_root,  # Pass project root to core
        )
        # -----------------------------

        self.logger.info("NEXUS Service initialized with KoiosLogger.")

    async def start(self):
        """Start the NEXUS service and any necessary listeners."""
        if self.running:
            self.logger.warning("NEXUS Service is already running.")  # Use self.logger
            return

        self.logger.info("Starting NEXUS Service...")  # Use self.logger
        # Subscribe to relevant Mycelium topics
        try:
            await self.interface.subscribe(
                f"request.{self.node_id}.analyze_file", self.handle_analyze_file_request
            )
            await self.interface.subscribe(
                f"request.{self.node_id}.analyze_workspace", self.handle_analyze_workspace_request
            )
            await self.interface.subscribe(
                f"request.{self.node_id}.suggest_improvements",
                self.handle_suggest_improvements_request,
            )
            # Add other subscriptions as needed
            self.logger.info("Subscribed to Mycelium request topics.")  # Use self.logger
        except Exception as e:
            self.logger.error(
                f"Failed to subscribe to Mycelium topics: {e}", exc_info=True
            )  # Use self.logger
            return

        self.running = True
        self.logger.info("NEXUS Service started successfully.")  # Use self.logger

    async def stop(self):
        """Stop the NEXUS service."""
        if not self.running:
            self.logger.warning("NEXUS Service is not running.")  # Use self.logger
            return

        self.logger.info("Stopping NEXUS Service...")  # Use self.logger
        # Unsubscribe from topics if necessary
        # await self.interface.unsubscribe(...)

        self.running = False
        self.logger.info("NEXUS Service stopped.")  # Use self.logger

    # --- Mycelium Request Handlers --- #

    async def handle_analyze_file_request(self, message: Dict[str, Any]):
        """Handles requests to analyze a specific file."""
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received analyze_file request: {request_id}")  # Use self.logger
        response_topic = f"response.{self.node_id}.{request_id}"

        try:
            payload = message.get("payload", {})
            file_path_str = payload.get("file_path")

            if not file_path_str:
                raise ValueError("Missing 'file_path' in payload.")

            # Potentially resolve relative path against project root if needed
            # For now, assume absolute or resolvable path is provided
            # file_path = (self.project_root / file_path_str).resolve()

            # Execute the analysis
            analysis_result = self.nexus_core.analyze_code(file_path_str)

            response_payload = {
                "success": analysis_result is not None and "error" not in analysis_result,
                "file_path": file_path_str,
                "analysis": analysis_result or {},
            }

            await self.interface.publish(
                response_topic, {"type": "analyze_file_response", "payload": response_payload}
            )
            self.logger.info(
                f"Processed analyze_file request {request_id} "
                f"for '{file_path_str}'. Success: {response_payload['success']}"
            )

        except Exception as e:
            self.logger.error(
                f"Error handling analyze_file request {request_id}: {e}", exc_info=True
            )  # Use self.logger
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )

    async def handle_analyze_workspace_request(self, message: Dict[str, Any]):
        """Handles requests to analyze the entire workspace."""
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received analyze_workspace request: {request_id}")  # Use self.logger
        response_topic = f"response.{self.node_id}.{request_id}"

        try:
            # Execute the analysis
            analysis_result = self.nexus_core.analyze_workspace()

            response_payload = {
                "success": analysis_result is not None and "error" not in analysis_result,
                "analysis": analysis_result or {},
            }

            await self.interface.publish(
                response_topic, {"type": "analyze_workspace_response", "payload": response_payload}
            )
            self.logger.info(
                f"Processed analyze_workspace request {request_id}. "
                f"Success: {response_payload['success']}"
            )

        except Exception as e:
            self.logger.error(
                f"Error handling analyze_workspace request {request_id}: {e}", exc_info=True
            )  # Use self.logger
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )

    async def handle_suggest_improvements_request(self, message: Dict[str, Any]):
        """Handles requests to suggest improvements based on analysis data."""
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received suggest_improvements request: {request_id}")  # Use self.logger
        response_topic = f"response.{self.node_id}.{request_id}"

        try:
            payload = message.get("payload", {})
            analysis_data = payload.get("analysis_data")

            if not analysis_data or not isinstance(analysis_data, dict):
                raise ValueError("Missing or invalid 'analysis_data' in payload.")

            # Execute the suggestion generation
            suggestions = self.nexus_core.suggest_improvements(analysis_data)

            response_payload = {"success": True, "suggestions": suggestions}

            await self.interface.publish(
                response_topic,
                {"type": "suggest_improvements_response", "payload": response_payload},
            )
            self.logger.info(
                f"Processed suggest_improvements request {request_id}. "
                f"Found {len(suggestions)} suggestions."
            )

        except Exception as e:
            self.logger.error(
                f"Error handling suggest_improvements request {request_id}: {e}", exc_info=True
            )  # Use self.logger
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )


# Example run block (similar to other services)
# Needs update to reflect KoiosLogger usage
async def main():
    # --- Determine Project Root (Needs reliable method) ---
    try:
        project_root = Path(__file__).parent.parent.parent.resolve()
        print(f"Determined project root: {project_root}")
    except Exception as e:
        print(f"Could not determine project root: {e}")
        return
    # -----------------------------------------------------

    # --- Setup Basic Logging for Example --- #
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    # --------------------------------------- #

    # --- Load Config (Example) ---
    config = {
        "log_level": "DEBUG",  # For service logger
        "logging": {"level": "DEBUG"},  # For KoiosLogger config
        "core_config": {  # Config specific to NEXUSCore
            "analysis": {
                "suggestions": {
                    "cognitive_load_threshold_high": 60,  # Example override
                    "imports_threshold": 20,
                }
            }
        },
    }
    # ---------------------------

    # --- Initialize Mycelium ---
    mycelium_interface = MyceliumInterface(node_id="NEXUS_Main")  # Example
    # await mycelium_interface.connect(...)
    # -------------------------

    nexus_service = NexusService(config, mycelium_interface, project_root)

    try:
        await nexus_service.start()
        print("NEXUS Service running. Send requests via Mycelium...")
        # Keep running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logging.info("Shutdown signal received.")
    finally:
        await nexus_service.stop()
        # await mycelium_interface.disconnect()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO) # Basic config if run directly - Handled in main
    print("Running NEXUS Service example...")
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"NEXUS Service example failed: {e}", exc_info=True)
