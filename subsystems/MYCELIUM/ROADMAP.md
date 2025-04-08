# 🍄 MYCELIUM Subsystem Roadmap

**Last Update:** April 5, 2025

This document outlines the detailed tasks and milestones specifically for the **MYCELIUM** subsystem (Inter-Subsystem Communication Network), complementing the high-level overview in the main project `../../ROADMAP.md`.

---

## 🎯 Phase 2 Focus: Core Messaging Definition

### Initial Setup (Completed Tasks - Ref Main Roadmap Phase 2a)

*   Conceptual definition within MQP [DONE]

### Foundational Capabilities (Planned - Ref Main Roadmap Phase 2)

*   **Task MYC-MSG-01: Define Core Topics & Formats**
    *   **Relates to:** Main Roadmap Task `MYC-MSG-01`
    *   **Goal:** Establish the initial communication patterns needed for Phase 2 functionality, focusing on topics and message schemas.
    *   **Sub-Tasks:**
        *   [ ] Define initial topic structure conventions (e.g., `request.<target_subsystem>.<action>`, `event.<source_subsystem>.<event_name>`).
        *   [ ] Specify topics needed for potential ETHIK validation requests/responses (if decided to use Mycelium instead of direct calls).
        *   [ ] Specify topics needed for potential KOIOS log event broadcasting (see Task `KOI-LOG-03`).
        *   [ ] Define standard message envelope (e.g., including message ID, timestamp, source, trace ID).
        *   [ ] Define specific message payloads (schemas) for the initial topics.
        *   [ ] Document these initial topics and schemas in `subsystems/MYCELIUM/docs/topics.md` (or similar).
    *   **Status:** Planned
    *   **Priority:** MEDIUM

*   **Task MYC-INF-01: Research/Select Technology**
    *   **Relates to:** Enabling future implementation.
    *   **Goal:** Evaluate and select the underlying technology for the Mycelium message bus.
    *   **Sub-Tasks:**
        *   [ ] Research options (e.g., Redis Pub/Sub, RabbitMQ, NATS, ZeroMQ, potentially built on Supabase Realtime if suitable).
        *   [ ] Evaluate based on performance, reliability, ease of use, scalability, and alignment with EGOS principles (Windows compatibility).
        *   [ ] Make a preliminary technology selection.
    *   **Status:** Planned
    *   **Priority:** LOW (for Phase 2, higher later)

---

## Future Phases (Placeholder)

*   Implement chosen message bus technology.
*   Create client libraries/interfaces for subsystems to easily publish/subscribe.
*   Implement message persistence and replay capabilities.
*   Develop monitoring and management tools for the Mycelium network.

---

✧༺❀༻∞ EGOS ∞༺❀༻✧
