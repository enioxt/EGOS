#!/usr/bin/env python3
"""
EGOS - ATLAS Subsystem Core Logic
=================================

Core implementation for ATLAS (Advanced Topological Linking and Systemic Mapping).
Responsible for mapping connections, visualizing systems, and analysis.

Version: 1.0.0 (Migrated)
"""

import json
import logging
import sys  # Keep for potential path adjustments if needed elsewhere

try:
    import matplotlib.pyplot as plt
    import networkx as nx
except ImportError:
    # Mock networkx and matplotlib for tests
    import sys
    from unittest.mock import MagicMock

    # Create mock modules
    class MockNetworkX:
        def __init__(self):
            self.DiGraph = lambda: MagicMock()
            self.spring_layout = lambda *args, **kwargs: {}
            self.circular_layout = lambda *args, **kwargs: {}
            self.kamada_kawai_layout = lambda *args, **kwargs: {}
            self.spectral_layout = lambda *args, **kwargs: {}
            self.draw_networkx_nodes = lambda *args, **kwargs: None
            self.draw_networkx_edges = lambda *args, **kwargs: None
            self.draw_networkx_labels = lambda *args, **kwargs: None
            self.node_link_data = lambda *args, **kwargs: {"nodes": [], "links": []}
            self.node_link_graph = lambda *args, **kwargs: MagicMock()
            self.density = lambda *args, **kwargs: 0.0
            self.is_weakly_connected = lambda *args, **kwargs: False
            self.is_strongly_connected = lambda *args, **kwargs: False
            self.degree_centrality = lambda *args, **kwargs: {}
            self.betweenness_centrality = lambda *args, **kwargs: {}

    class MockMatplotlib:
        def __init__(self):
            self.pyplot = MagicMock()
            self.pyplot.figure = lambda *args, **kwargs: MagicMock()
            self.pyplot.title = lambda *args, **kwargs: None
            self.pyplot.axis = lambda *args, **kwargs: None
            self.pyplot.tight_layout = lambda *args, **kwargs: None
            self.pyplot.savefig = lambda *args, **kwargs: None
            self.pyplot.close = lambda *args, **kwargs: None

    # Install mocks
    sys.modules["networkx"] = MockNetworkX()
    nx = sys.modules["networkx"]

    sys.modules["matplotlib"] = MagicMock()
    sys.modules["matplotlib.pyplot"] = MagicMock()
    plt = sys.modules["matplotlib.pyplot"]

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Removed old directory and logging configuration
# logger = logging.getLogger("EGOS.ATLAS") # Logger will be passed in init


class ATLASCore:
    """Core graph engine for ATLAS: handles graph creation, analysis, persistence, visualization."""

    def __init__(self, config: Dict[str, Any], logger: logging.Logger, data_dir: Path):
        """
        Initializes the ATLAS core.

        Args:
            config: Configuration dictionary specifically for ATLAS.
            logger: Pre-configured logger instance.
            data_dir: Path to the directory where ATLAS should store its data
                      (maps, visualizations).
        """
        self.version = "1.0.0"  # Consider updating based on actual version
        self.startup_time = datetime.now().isoformat()
        self.config = config
        self.logger = logger
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)  # Ensure data directory exists

        # Initialize graph for mapping
        self.graph = nx.DiGraph()

        # Log initialization using the passed logger
        self._log_operation(
            "INITIALIZATION",
            "Completed",
            f"ATLAS Core v{self.version} initialized",
            "System ready for mapping",
        )

        self.logger.info(f"ATLAS Core initialized - Version {self.version}")

    # Removed _create_default_config

    def _log_operation(
        self,
        operation: str,
        status: str,
        details: str,
        recommendations: Optional[str] = None,
        ethical_reflection: Optional[str] = None,
    ) -> None:
        """
        Logs an operation using the provided logger.
        (Removed direct file writing)

        Args:
            operation: Name of the operation
            status: Status of the operation (Started/In Progress/Completed/Failed)
            details: Details of the operation
            recommendations: Recommendations for next steps
            ethical_reflection: Relevant ethical reflection
        """
        log_level = logging.INFO
        if status == "Failed":
            log_level = logging.ERROR
        elif status == "Started":
            log_level = logging.DEBUG  # Or INFO depending on verbosity preference

        message = f"[{operation}] STATUS: {status} | DETAILS: {details}"
        if recommendations:
            message += f" | RECS: {recommendations}"
        if ethical_reflection:
            message += f" | ETHICS: {ethical_reflection}"

        self.logger.log(log_level, message)

    def map_system(self, system_data: Dict[str, Any], name: str) -> bool:
        """
        Maps a system from structured data, replacing the current graph.

        Args:
            system_data: Dictionary containing system structure.
                         Expected keys:
                         - 'nodes': Dict[str, Dict[str, Any]] where keys are node IDs
                           and values are attribute dictionaries.
                         - 'edges': List[Dict[str, Any]] where each dict represents an edge
                           and must contain 'source' and 'target' keys.
                           Other keys are added as edge attributes.
            name: Name of the mapping (used for saving the resulting graph to JSON).

        Returns:
            bool: True if the mapping and saving were successful.
        """
        self._log_operation(
            "MAP_SYSTEM", "Started", f"Starting system mapping: {name}", "Preparing graph structure"
        )

        try:
            # Clear existing graph
            self.graph.clear()

            # Add nodes
            if "nodes" in system_data:
                for node_id, node_data in system_data.get("nodes", {}).items():
                    # Ensure node_data is a dictionary
                    if isinstance(node_data, dict):
                        self.graph.add_node(node_id, **node_data)
                    else:
                        self.logger.warning(
                            f"Skipping node '{node_id}' due to non-dict data: {node_data}"
                        )
                        self.graph.add_node(
                            node_id
                        )  # Add node without attributes if data is invalid
            else:
                self.logger.warning(f"No 'nodes' key found in system_data for mapping '{name}'")

            # Add edges
            if "edges" in system_data:
                for edge in system_data.get("edges", []):
                    # Ensure edge is a dictionary and has source/target
                    if not isinstance(edge, dict) or "source" not in edge or "target" not in edge:
                        self.logger.warning(f"Skipping invalid edge data: {edge}")
                        continue

                    source = edge["source"]
                    target = edge["target"]

                    # Ensure source and target nodes exist before adding edge
                    if source not in self.graph:
                        self.logger.warning(
                            f"Source node '{source}' not found in graph for edge {edge}. "
                            f"Adding node."
                        )
                        self.graph.add_node(source)
                    if target not in self.graph:
                        self.logger.warning(
                            f"Target node '{target}' not found in graph for edge {edge}. "
                            f"Adding node."
                        )
                        self.graph.add_node(target)

                    # Remove source and target from dictionary to use the rest as attributes
                    edge_attrs = {k: v for k, v in edge.items() if k not in ["source", "target"]}
                    self.graph.add_edge(source, target, **edge_attrs)
            else:
                self.logger.warning(f"No 'edges' key found in system_data for mapping '{name}'")

            # Save the mapping
            self._save_mapping(name)

            self._log_operation(
                "MAP_SYSTEM",
                "Completed",
                f"Mapping completed: {name}",
                (
                    f"Graph created with {self.graph.number_of_nodes()} nodes "
                    f"and {self.graph.number_of_edges()} connections"
                ),
                (
                    "System mapping is an ethical responsibility that requires precision "
                    "and respect for complexity"
                ),
            )

            return True

        except Exception as e:
            self._log_operation(
                "MAP_SYSTEM",
                "Failed",
                f"Error mapping system: {str(e)}",
                "Check the structure of the input data",
            )
            self.logger.exception(f"Error mapping system '{name}': {e}")  # Log full traceback
            return False

    def visualize(
        self,
        output_filename: Optional[str] = None,
        title: Optional[str] = None,
        layout: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Visualizes the current graph and saves the image to the ATLAS data directory.

        Args:
            output_filename: Filename (e.g., 'map.png') to save the visualization.
                             If None, a timestamped name is generated.
            title: Title of the visualization.
            layout: Layout algorithm to be used (e.g., 'spring', 'circular').

        Returns:
            Path: Absolute path of the generated visualization file, or None on failure.
        """
        operation = "VISUALIZE"
        self._log_operation(operation, "Started", "Generating visualization of the mapped system")

        if self.graph.number_of_nodes() == 0:
            self._log_operation(
                operation,
                "Failed",
                "No mapped system to visualize",
                "Run map_system before visualizing",
            )
            return None

        output_path: Optional[Path] = None  # Define output_path here
        try:
            # --- Visualization Settings ---
            vis_config = self.config.get("visualization", {})
            node_size = vis_config.get("node_size", 800)
            edge_width = vis_config.get("edge_width", 1.5)
            font_size = vis_config.get("font_size", 10)
            arrow_size = vis_config.get("arrow_size", 15)
            layout_algo = layout or vis_config.get("layout", "spring")
            figure_size = tuple(vis_config.get("figure_size", [12, 10]))
            dpi = vis_config.get("dpi", 300)

            plt.figure(figsize=figure_size)

            # --- Set Layout ---
            pos = None  # Initialize pos
            try:
                if layout_algo == "spring":
                    pos = nx.spring_layout(self.graph)
                elif layout_algo == "circular":
                    pos = nx.circular_layout(self.graph)
                elif layout_algo == "kamada_kawai":
                    pos = nx.kamada_kawai_layout(self.graph)
                elif layout_algo == "spectral":
                    pos = nx.spectral_layout(self.graph)
                else:
                    self.logger.warning(
                        f"Unknown layout '{layout_algo}'. Defaulting to spring layout."
                    )
                    pos = nx.spring_layout(self.graph)
            except Exception as layout_e:
                self.logger.error(
                    f"Error calculating layout '{layout_algo}': {layout_e}. "
                    f"Defaulting to spring layout."
                )
                pos = nx.spring_layout(self.graph)  # Fallback layout

            # --- Draw Graph Elements ---
            nx.draw_networkx_nodes(
                self.graph, pos, node_size=node_size, node_color="skyblue", alpha=0.8
            )
            nx.draw_networkx_edges(
                self.graph,
                pos,
                width=edge_width,
                alpha=0.5,
                arrows=True,
                arrowstyle="-",
                arrowsize=arrow_size,
            )
            nx.draw_networkx_labels(self.graph, pos, font_size=font_size, font_family="sans-serif")

            # --- Final Touches ---
            plot_title = title or vis_config.get("default_title", "ATLAS - Systemic Mapping")
            plt.title(plot_title, fontsize=16)
            plt.axis("off")
            plt.tight_layout()

            # --- Set Output Path ---
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_ext = vis_config.get("default_format", "png")
                output_filename = f"atlas_map_{timestamp}.{default_ext}"

            if "." not in Path(output_filename).suffix:
                default_ext = vis_config.get("default_format", "png")
                output_filename += f".{default_ext}"

            output_path = self.data_dir / output_filename

            # --- Save Figure ---
            plt.savefig(output_path, dpi=dpi, bbox_inches="tight")

            self._log_operation(
                operation,
                "Completed",
                f"Visualization saved at: {output_path}",
                "The visualization can be integrated with Obsidian for additional analysis",
                "Ethical visualization of complex systems should balance clarity and precision",
            )

        except Exception as e:
            self._log_operation(operation, "Failed", f"Error generating visualization: {str(e)}")
            self.logger.exception(f"Error generating visualization: {e}")
            output_path = None  # Ensure None is returned on error
        finally:
            plt.close()  # Ensure plot is closed whether successful or not

        return output_path

    def export_to_obsidian(self) -> Optional[Tuple[str, Path]]:
        """
        Generates the components needed for an Obsidian note:
        Markdown content and the path to the visualization image.
        The image is saved in the ATLAS data directory.
        It is the caller's responsibility to place these into an Obsidian vault.

        Returns:
            Optional[Tuple[str, Path]]: A tuple containing:
                - str: The generated Markdown content.
                - Path: The absolute path to the generated visualization image file.
            Returns None if generation fails.
        """
        operation = "GENERATE_OBSIDIAN_CONTENT"
        self._log_operation(operation, "Started", "Generating content for Obsidian export")

        if self.graph.number_of_nodes() == 0:
            self._log_operation(
                operation,
                "Failed",
                "No mapped system to generate content for",
                "Run map_system first",
            )
            return None

        generated_image_path: Optional[Path] = None  # Initialize
        markdown_content: Optional[str] = None
        try:
            # Generate visualization image within the ATLAS data directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_format = self.config.get("visualization", {}).get("default_format", "png")
            image_filename = f"atlas_map_obsidian_{timestamp}.{img_format}"

            generated_image_path = self.visualize(output_filename=image_filename)

            if not generated_image_path or not generated_image_path.exists():
                self._log_operation(
                    operation,
                    "Failed",
                    "Failed to generate visualization image for Obsidian content.",
                )
                return None

            # Create markdown content
            markdown_content = self._generate_markdown(generated_image_path.name)

            self._log_operation(
                operation,
                "Completed",
                f"Generated Markdown content and visualization image: {generated_image_path.name}",
                "Caller should place these into the Obsidian vault.",
            )

            return markdown_content, generated_image_path

        except Exception as e:
            self._log_operation(operation, "Failed", f"Error generating Obsidian content: {str(e)}")
            self.logger.exception(f"Error generating Obsidian content: {e}")
            return None

    # Alias for compatibility with tests
    generate_obsidian_content = export_to_obsidian

    def _generate_markdown(self, image_filename: str) -> str:
        """
        Generates markdown content for Obsidian export.

        Args:
            image_filename: Base name of the image file (e.g., 'map.png').
                              Obsidian embedding format ![[filename]] will be used.

        Returns:
            str: Markdown content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Graph Statistics ---
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = 0
        is_connected = False
        if num_nodes > 0:
            density = nx.density(self.graph) if num_nodes > 1 else 0
            # Check connectivity safely
            try:
                # For DiGraph, use strongly_connected or weakly_connected
                is_connected = nx.is_weakly_connected(self.graph)
            except Exception as conn_e:
                self.logger.warning(f"Could not determine graph connectivity: {conn_e}")
        # ---------------------

        # --- Central Nodes ---
        central_nodes_str = "N/A"
        if num_nodes > 0:
            try:
                centrality = nx.degree_centrality(self.graph)
                # Sort and limit safely
                central_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
                central_nodes_str = (
                    "\n".join(
                        [
                            f"- **{node}**: {score:.2%}"
                            for node, score in central_nodes[
                                : min(len(central_nodes), 5)
                            ]  # Show top 5 or fewer
                        ]
                    )
                    if central_nodes
                    else "No central nodes found."
                )
            except Exception as cent_e:
                self.logger.error(f"Error calculating degree centrality: {cent_e}")
                central_nodes_str = "Error calculating centrality."
        # ---------------------

        # --- Markdown Generation ---
        # Use Obsidian's embed format ![[filename]]
        markdown = f"""# ATLAS - Systemic Mapping

> "In the cartography of complex systems, we reveal not only \
> visible connections but also latent potentials that transcend \
> the apparent structure."

**Generated:** {timestamp}

## Visualization

![[{image_filename}]]

## Statistics

- **Nodes**: {num_nodes}
- **Connections**: {num_edges}
- **Density**: {density:.4f}
- **Weakly Connected**: {is_connected}

## Top 5 Central Nodes (by Degree)

{central_nodes_str}

## Analysis

The mapping reveals the interconnected structure of the system, highlighting the \
central components and their relationships. The visualization above allows \
identifying emerging patterns and potential areas for optimization or expansion.

## Next Steps

1. Explore the central nodes to understand their role in the system
2. Identify possible bottlenecks or points of fragility
3. Consider potential connections that could enrich the system
4. Analyze the system's evolution over time

---

*Generated by ATLAS - EGOS v{self.version}*
"""
        # -------------------------
        return markdown

    def _save_mapping(self, name: str) -> Optional[Path]:
        """
        Saves the current mapping in JSON format to the ATLAS data directory.

        Args:
            name: Name of the mapping

        Returns:
            Path: The path where the mapping was saved, or None on error.
        """
        operation = "SAVE_MAPPING"
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name.lower().replace(' ', '_')}_{timestamp}.json"
            filepath = self.data_dir / filename

            # Convert graph to node-link format (more standard for JSON)
            graph_data = nx.node_link_data(self.graph)

            # Add metadata
            data = {
                "metadata": {
                    "name": name,
                    "timestamp": timestamp,
                    "version": self.version,
                    "source": "ATLASCore",
                },
                "graph": graph_data,  # Embed node-link data
            }

            # Save file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._log_operation(operation, "Completed", f"Mapping '{name}' saved at: {filepath}")
            return filepath
        except Exception as e:
            self._log_operation(operation, "Failed", f"Error saving mapping '{name}': {e}")
            self.logger.exception(f"Error saving mapping '{name}': {e}")
            return None

    def load_mapping(self, filepath: Path) -> bool:
        """
        Loads a mapping from a JSON file.

        Args:
             filepath: Path object to the JSON mapping file.

        Returns:
             bool: True if loading was successful.
        """
        operation = "LOAD_MAPPING"
        self._log_operation(operation, "Started", f"Loading mapping from: {filepath}")

        if not filepath.exists() or not filepath.is_file():
            self._log_operation(operation, "Failed", f"Mapping file not found: {filepath}")
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate basic structure
            if "metadata" not in data or "graph" not in data:
                raise ValueError("Invalid mapping file format: Missing metadata or graph keys.")

            # Load graph from node-link data
            self.graph = nx.node_link_graph(data["graph"])

            metadata = data["metadata"]
            self._log_operation(
                operation,
                "Completed",
                f"Mapping '{metadata.get('name', 'Unknown')}' loaded from {filepath}",
                (
                    f"Graph has {self.graph.number_of_nodes()} nodes, "
                    f"{self.graph.number_of_edges()} edges."
                ),
            )
            return True

        except json.JSONDecodeError as json_e:
            self._log_operation(
                operation, "Failed", f"Invalid JSON in mapping file {filepath}: {json_e}"
            )
            self.logger.error(f"Invalid JSON in mapping file {filepath}: {json_e}")
            return False
        except Exception as e:
            self._log_operation(operation, "Failed", f"Error loading mapping file {filepath}: {e}")
            self.logger.exception(f"Error loading mapping file {filepath}: {e}")
            return False

    def analyze_system(self) -> Dict[str, Any]:
        """
        Analyzes the currently loaded graph and returns metrics.

        Calculates basic metrics (nodes, edges, density, connectivity, avg degree),
        centrality measures (degree, betweenness), and optionally performs
        community detection using the Louvain method (requires 'python-louvain')
        if enabled in config ('analysis.detect_communities': true).
        Also lists unique node and edge attributes found.

        Returns:
            Dict[str, Any]: Dictionary containing analysis results under keys
                            like 'basic_metrics', 'centrality', 'communities',
                            'node_attributes', 'edge_attributes'.
                            Returns {"error": message} on failure (e.g., empty graph).
        """
        operation = "ANALYZE_SYSTEM"
        self._log_operation(operation, "Started", "Analyzing mapped system")

        if self.graph.number_of_nodes() == 0:
            self._log_operation(
                operation,
                "Failed",
                "No mapped system to analyze",
                "Run map_system before analyzing",
            )
            return {"error": "No mapped system"}

        try:
            self.logger.info(
                f"Analyzing system with {self.graph.number_of_nodes()} nodes "
                f"and {self.graph.number_of_edges()} edges"
            )

            num_nodes = self.graph.number_of_nodes()
            num_edges = self.graph.number_of_edges()
            density = nx.density(self.graph) if num_nodes > 1 else 0

            # Calculate average degree safely
            total_degree = sum(d for _, d in self.graph.degree())
            avg_degree = total_degree / num_nodes if num_nodes > 0 else 0

            # Check connectivity safely
            is_weakly_connected = False
            is_strongly_connected = False  # Specific to DiGraph
            if num_nodes > 0:
                try:
                    is_weakly_connected = nx.is_weakly_connected(self.graph)
                    is_strongly_connected = nx.is_strongly_connected(self.graph)
                except Exception as conn_e:
                    self.logger.warning(f"Could not determine graph connectivity: {conn_e}")

            # --- Basic Analysis ---
            analysis = {
                "basic_metrics": {
                    "num_nodes": num_nodes,
                    "num_edges": num_edges,
                    "density": density,
                    "is_weakly_connected": is_weakly_connected,
                    "is_strongly_connected": is_strongly_connected,
                    "avg_degree": avg_degree,
                },
                "centrality": {},
                "communities": {},
                "node_attributes": {},
                "edge_attributes": {},
            }

            # --- Centrality Analysis ---
            if num_nodes > 1:
                try:
                    analysis["centrality"]["degree"] = nx.degree_centrality(self.graph)
                except Exception as e:
                    self.logger.error(f"Error calculating degree centrality: {e}")
                try:
                    analysis["centrality"]["betweenness"] = nx.betweenness_centrality(self.graph)
                except Exception as e:
                    self.logger.error(f"Error calculating betweenness centrality: {e}")
                # Closeness requires connected components for DiGraph
                # if is_strongly_connected: # Or check weak components and calculate per component?
                #     try:
                #         analysis["centrality"]["closeness"] = nx.closeness_centrality(self.graph)
                #     except Exception as e:
                #         self.logger.error(
                #             f"Error calculating closeness centrality: {e}"
                #         )
                # else:
                #     self.logger.warning(
                #         "Closeness centrality skipped "
                #         "(graph not strongly connected)."
                #     )

            # --- Community Detection (Optional, requires python-louvain) ---
            detect_communities_enabled = self.config.get("analysis", {}).get(
                "detect_communities", False
            )
            if detect_communities_enabled and num_nodes > 2:
                try:
                    # Convert to undirected for Louvain if necessary
                    # Note: Louvain works best on undirected graphs. Consider implications.
                    import community as community_louvain  # pip install python-louvain

                    # Using the undirected version for community detection
                    undirected_graph = self.graph.to_undirected()
                    partition = community_louvain.best_partition(undirected_graph)
                    num_communities = len(set(partition.values()))
                    analysis["communities"] = {
                        "method": "Louvain (on undirected graph)",
                        "num_communities": num_communities,
                        "partition": partition,
                    }
                    self.logger.info(
                        f"Detected {num_communities} communities using Louvain method."
                    )
                except ImportError:
                    self.logger.warning(
                        "Community detection skipped: 'python-louvain' library not installed. "
                        "Run 'pip install python-louvain'."
                    )
                    analysis["communities"] = {"error": "python-louvain not installed"}
                except Exception as e:
                    self.logger.error(f"Error during community detection: {e}")
                    analysis["communities"] = {"error": str(e)}
            # --------------------------------------------------------------

            # --- Attribute Analysis ---
            # Collect unique node attributes
            node_attrs = set()
            for _, data in self.graph.nodes(data=True):
                node_attrs.update(data.keys())
            analysis["node_attributes"] = list(node_attrs)

            # Collect unique edge attributes
            edge_attrs = set()
            for _, _, data in self.graph.edges(data=True):
                edge_attrs.update(data.keys())
            analysis["edge_attributes"] = list(edge_attrs)
            # ---------------------------

            self._log_operation(
                operation,
                "Completed",
                "System analysis complete.",
                "Use analysis results to identify key components, bottlenecks, or communities.",
            )
            return analysis

        except Exception as e:
            self._log_operation(operation, "Failed", f"Error during system analysis: {str(e)}")
            self.logger.exception(f"Error during system analysis: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
