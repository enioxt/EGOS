# 🗺️ ATLAS Subsystem Roadmap

**Last Update:** April 5, 2025

This document outlines the detailed tasks and milestones specifically for the **ATLAS** subsystem (Systemic Cartography & Visualization), complementing the high-level overview in the main project `../../ROADMAP.md`.

---

## 🎯 Phase 2 Focus: Initial Structure Definition

### Initial Setup (Completed Tasks - Ref Main Roadmap Phase 2a)

*   Conceptual definition within MQP [DONE]

### Foundational Capabilities (Planned - Ref Main Roadmap Phase 2)

*   **Task ATL-STR-01: Define Core Data Models**
    *   **Relates to:** Main Roadmap Task `ATL-STR-01`
    *   **Goal:** Establish the basic schemas for representing knowledge graph nodes and edges within the ATLAS system.
    *   **Sub-Tasks:**
        *   [ ] Define core node types (e.g., `Concept`, `Document`, `CodeModule`, `Person`, `Event`, `Subsystem`).
        *   [ ] Define core edge types/relationships (e.g., `RELATES_TO`, `DEPENDS_ON`, `DEFINES`, `CONTAINS`, `AUTHOR_OF`, `REFERENCES`).
        *   [ ] Specify standard metadata properties for nodes and edges (e.g., `id`, `type`, `name`, `description`, `source`, `timestamp`, `subsystem_tag`).
        *   [ ] Choose a preliminary representation format (e.g., Pydantic models, JSON Schema).
        *   [ ] Document these initial schemas in `subsystems/ATLAS/docs/schema.md`.
    *   **Status:** Planned
    *   **Priority:** MEDIUM

*   **Task ATL-STO-01: Research Storage Options**
    *   **Relates to:** Enabling future implementation.
    *   **Goal:** Evaluate potential storage solutions for the ATLAS knowledge graph.
    *   **Sub-Tasks:**
        *   [ ] Research graph database options (e.g., Neo4j, ArangoDB, AWS Neptune, potentially using Supabase Postgres with graph extensions like AGE).
        *   [ ] Evaluate based on query capabilities, performance, scalability, cost, ease of integration, and Windows compatibility.
        *   [ ] Make a preliminary technology selection for graph storage.
    *   **Status:** Planned
    *   **Priority:** LOW (for Phase 2, higher later)

---

## Future Phases (Placeholder)

*   Implement graph storage solution.
*   Develop APIs/services for creating, querying, and updating graph data.
*   Integrate with other subsystems (e.g., NEXUS analysis results, CRONOS events, KOIOS documentation metadata).
*   Develop visualization components.

---

✧༺❀༻∞ EGOS ∞༺❀༻✧
