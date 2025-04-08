#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EVA & GUARANI - ATLAS Service
=============================

Orchestrates the ATLAS subsystem for systemic cartography and visualization.
Acts as the primary Mycelium interface for ATLAS, receiving requests and
publishing responses. Initializes and manages the lifecycle of AtlasCartographer
and ATLASCore components.

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
from .core.atlas_core import ATLASCore

# --- Import Cartographer --- #
from .core.cartographer import AtlasCartographer

# -------------------------

# Configure logging for the service - Use Koios Logger
# logger = logging.getLogger("atlas_service")
# handler = logging.StreamHandler()
# formatter = logging.Formatter('🗺️ %(asctime)s - [ATLAS Service] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)


class AtlasService:
    """Manages the ATLAS subsystem's operations, acting as the Mycelium gateway."""

    def __init__(
        self, config: Dict[str, Any], mycelium_interface: MyceliumInterface, project_root: Path
    ):
        """Initialize the ATLAS Service.

        Initializes Koios loggers, determines the data directory, and instantiates
        both AtlasCartographer and ATLASCore, passing necessary configurations
        and dependencies.

        Args:
            config: Configuration dictionary for the ATLAS subsystem.
                    Should contain sections like 'logging', 'core_config',
                    'cartographer_config'.
            mycelium_interface: An instance of the MyceliumInterface.
            project_root: The absolute path to the project's root directory.
        """
        self.config = config
        self.interface = mycelium_interface
        self.project_root = project_root
        self.node_id = "ATLAS_SERVICE"
        self.running = False

        # --- Setup Loggers using Koios --- #
        log_config = self.config.get("logging", {})
        self.logger = get_koios_logger(f"EGOS.{self.node_id}", config=log_config)
        atlas_core_logger = get_koios_logger("EGOS.ATLAS.Core", config=log_config)
        # Pass a logger instance down to the core
        # self.atlas_core_logger = logging.getLogger("EGOS.ATLAS")
        # # Match name used in core - Now using Koios
        atlas_cartographer_logger = get_koios_logger("EGOS.ATLAS.Cartographer", config=log_config)
        # Ensure logger level is appropriate (can be configured)
        # log_level_str = self.config.get("log_level", "INFO").upper()
        # self.atlas_core_logger.setLevel(getattr(logging, log_level_str, logging.INFO))
        # Add handlers if not configured globally (basic console handler for now)
        # if not self.atlas_core_logger.handlers:
        #      core_handler = logging.StreamHandler()
        #      core_formatter = logging.Formatter('🗺️ %(asctime)s - [ATLAS Core] %(message)s')
        #      core_handler.setFormatter(core_formatter)
        #      self.atlas_core_logger.addHandler(core_handler)
        #      self.atlas_core_logger.propagate = False
        #      # Avoid double logging if root logger has handlers
        # ---------------------------------

        # --- Determine Data Directory ---
        # Use config value or default relative to project root
        data_dir_rel_path = self.config.get("data_directory", "data/atlas")
        self.atlas_data_dir = (self.project_root / data_dir_rel_path).resolve()
        self.atlas_data_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"ATLAS data directory set to: {self.atlas_data_dir}")
        # ---------------------------------

        # --- Setup Logger for ATLASCore ---
        # Pass a logger instance down to the core
        # self.atlas_core_logger = logging.getLogger("EGOS.ATLAS")
        # # Match name used in core - Now using Koios
        # Ensure logger level is appropriate (can be configured)
        # log_level_str = self.config.get("log_level", "INFO").upper()
        # self.atlas_core_logger.setLevel(getattr(logging, log_level_str, logging.INFO))
        # Add handlers if not configured globally (basic console handler for now)
        # if not self.atlas_core_logger.handlers:
        #      core_handler = logging.StreamHandler()
        #      core_formatter = logging.Formatter('🗺️ %(asctime)s - [ATLAS Core] %(message)s')
        #      core_handler.setFormatter(core_formatter)
        #      self.atlas_core_logger.addHandler(core_handler)
        #      self.atlas_core_logger.propagate = False
        #      # Avoid double logging if root logger has handlers
        # ---------------------------------

        # --- Instantiate ATLASCore ---
        atlas_core_config = self.config.get("core_config", {})  # Pass specific core config
        self.atlas_core = ATLASCore(
            config=atlas_core_config,
            logger=atlas_core_logger,  # Pass the Koios logger
            data_dir=self.atlas_data_dir,
        )
        # -----------------------------

        # --- Instantiate AtlasCartographer --- #
        cartographer_config = self.config.get(
            "cartographer_config", self.config
        )  # Use main config if specific not found
        self.atlas_cartographer = AtlasCartographer(
            config=cartographer_config,  # Pass specific or main config
            logger=atlas_cartographer_logger,  # Pass the Koios logger
            mycelium_client=self.interface,  # Pass the Mycelium interface
        )
        # ---------------------------------- #

        self.logger.info("ATLAS Service initialized with KoiosLogger.")

    async def start(self):
        """Start the ATLAS service and subscribe to Mycelium request topics."""
        if self.running:
            self.logger.warning("ATLAS Service is already running.")  # Use self.logger
            return

        self.logger.info("Starting ATLAS Service...")  # Use self.logger
        # Subscribe to relevant Mycelium topics
        try:
            # Example: Listen for requests to map a project
            await self.interface.subscribe(
                f"request.{self.node_id}.map_system", self.handle_map_system_request
            )
            # Example: Listen for requests to generate Obsidian content
            await self.interface.subscribe(
                f"request.{self.node_id}.generate_obsidian", self.handle_generate_obsidian_request
            )
            # Example: Listen for requests to analyze the current map
            await self.interface.subscribe(
                f"request.{self.node_id}.analyze_system", self.handle_analyze_system_request
            )
            # Add other subscriptions as needed
            self.logger.info("Subscribed to Mycelium request topics.")  # Use self.logger
        except Exception as e:
            self.logger.error(
                f"Failed to subscribe to Mycelium topics: {e}", exc_info=True
            )  # Use self.logger
            # Should we prevent starting if subscription fails?
            return

        self.running = True
        self.logger.info("ATLAS Service started successfully.")  # Use self.logger

    async def stop(self):
        """Stop the ATLAS service.

        (Currently does not explicitly unsubscribe from Mycelium topics).
        """
        if not self.running:
            self.logger.warning("ATLAS Service is not running.")  # Use self.logger
            return

        self.logger.info("Stopping ATLAS Service...")  # Use self.logger
        # Unsubscribe from topics if necessary
        # await self.interface.unsubscribe(...)

        self.running = False
        self.logger.info("ATLAS Service stopped.")  # Use self.logger

    # --- Mycelium Request Handlers --- #

    async def handle_map_system_request(self, message: Dict[str, Any]):
        """Handles 'request.ATLAS_SERVICE.map_system' Mycelium requests.

        Delegates to ATLASCore.map_system to generate and save a map from
        provided system data.

        Expected payload keys:
            - system_data (Dict): Dictionary with 'nodes' and 'edges' keys.
            - map_name (str): Name to use when saving the map.

        Publishes response to: f'response.{self.node_id}.{request_id}'
        """
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received map_system request: {request_id}")  # Use self.logger
        response_topic = f"response.{self.node_id}.{request_id}"

        try:
            payload = message.get("payload", {})
            system_data = payload.get("system_data")
            map_name = payload.get("map_name", f"map_{request_id}")  # Default name

            if not system_data or not isinstance(system_data, dict):
                raise ValueError("Missing or invalid 'system_data' in payload.")

            # Execute the mapping
            success = self.atlas_core.map_system(system_data, map_name)

            response_payload = {
                "success": success,
                "map_name": map_name,
                "nodes_count": self.atlas_core.graph.number_of_nodes(),
                "edges_count": self.atlas_core.graph.number_of_edges(),
                # Optionally include path to saved JSON map?
                # "map_file": str(saved_path) if success and saved_path else None
            }

            await self.interface.publish(
                response_topic, {"type": "map_system_response", "payload": response_payload}
            )
            self.logger.info(
                f"Processed map_system request {request_id}. Success: {success}"
            )  # Use self.logger

        except Exception as e:
            self.logger.error(
                f"Error handling map_system request {request_id}: {e}", exc_info=True
            )  # Use self.logger
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )

    async def handle_generate_obsidian_request(self, message: Dict[str, Any]):
        """Handles 'request.ATLAS_SERVICE.generate_obsidian' Mycelium requests.

        Delegates to ATLASCore.export_to_obsidian (alias generate_obsidian_content)
        to generate Markdown content and a visualization image for the current map.

        Expected payload: {}

        Publishes response to: f'response.{self.node_id}.{request_id}'
        """
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received generate_obsidian request: {request_id}")  # Use self.logger
        response_topic = f"response.{self.node_id}.{request_id}"

        try:
            # Generate the markdown and image path
            result = self.atlas_core.generate_obsidian_content()

            if result:
                markdown_content, image_path = result
                response_payload = {
                    "success": True,
                    "markdown_content": markdown_content,
                    "image_path": str(image_path),  # Send the path to the generated image
                }
                self.logger.info(
                    f"Generated Obsidian content successfully for {request_id}. Image: {image_path}"
                )  # Use self.logger
            else:
                response_payload = {
                    "success": False,
                    "message": "Failed to generate Obsidian content.",
                }
                self.logger.warning(
                    f"Failed to generate Obsidian content for {request_id}."
                )  # Use self.logger

            await self.interface.publish(
                response_topic, {"type": "generate_obsidian_response", "payload": response_payload}
            )

        except Exception as e:
            self.logger.error(
                f"Error handling generate_obsidian request {request_id}: {e}", exc_info=True
            )  # Use self.logger
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )

    async def handle_analyze_system_request(self, message: Dict[str, Any]):
        """Handles 'request.ATLAS_SERVICE.analyze_system' Mycelium requests.

        Delegates to ATLASCore.analyze_system to perform analysis on the current map.

        Expected payload: {}

        Publishes response to: f'response.{self.node_id}.{request_id}'
        """
        request_id = message.get("id", "unknown")
        self.logger.info(f"Received analyze_system request: {request_id}")  # Use self.logger
        response_topic = f"response.{self.node_id}.{request_id}"

        try:
            analysis_results = self.atlas_core.analyze_system()
            response_payload = {
                "success": "error" not in analysis_results,
                "analysis": analysis_results,
            }
            await self.interface.publish(
                response_topic, {"type": "analyze_system_response", "payload": response_payload}
            )
            self.logger.info(
                f"Processed analyze_system request {request_id}. "
                f"Success: {response_payload['success']}"
            )

        except Exception as e:
            self.logger.error(
                f"Error handling analyze_system request {request_id}: {e}", exc_info=True
            )  # Use self.logger
            await self.interface.publish(
                response_topic, {"type": "error", "payload": {"message": str(e)}}
            )


# Example run block (similar to EthikService)
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
    # Should load a main config and extract the 'atlas' section
    config = {
        "data_directory": "data/atlas_output",  # Example override
        "log_level": "DEBUG",  # For service logger
        "logging": {"level": "DEBUG"},  # For KoiosLogger config
        "core_config": {  # Config specific to ATLASCore
            "visualization": {"default_format": "png", "node_size": 1000, "layout": "kamada_kawai"},
            "analysis": {"detect_communities": False},  # Example: disable community detection
        },
    }
    # ---------------------------

    # --- Initialize Mycelium ---
    mycelium_interface = MyceliumInterface(node_id="ATLAS_Main")  # Example
    # await mycelium_interface.connect(...)
    # -------------------------

    atlas_service = AtlasService(config, mycelium_interface, project_root)

    try:
        await atlas_service.start()
        print("ATLAS Service running. Send requests via Mycelium...")
        # Keep running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logging.info("Shutdown signal received.")
    finally:
        await atlas_service.stop()
        # await mycelium_interface.disconnect()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO) # Basic config if run directly - Handled in main now
    print("Running ATLAS Service example...")
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"ATLAS Service example failed: {e}", exc_info=True)
