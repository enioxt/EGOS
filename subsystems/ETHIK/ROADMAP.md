# ⚖️ ETHIK Subsystem Roadmap

**Last Update:** April 5, 2025

This document outlines the detailed tasks and milestones specifically for the **ETHIK** subsystem, complementing the high-level overview in the main project `../../ROADMAP.md`.

---

## 🎯 Phase 2 Focus: Foundational Checks

### Initial Setup (Completed Tasks - Ref Main Roadmap Phase 2a)

*   Define `EthikException` hierarchy [DONE]
*   Define `EthikCheckerInterface` [DONE]
*   Implement `DummyEthikChecker` [DONE]
*   Integrate `EthikCheckerInterface` into `BasicOrchestrator` [DONE]

### Foundational Capabilities (Planned - Ref Main Roadmap Phase 2)

*   **Task ETH-CHK-01: Implement Concrete Checks**
    *   **Relates to:** Main Roadmap Task `ETH-CHK-01`
    *   **Goal:** Move beyond the `DummyEthikChecker` by implementing a concrete checker with initial, basic filtering capabilities.
    *   **Sub-Tasks:**
        *   [x] Create `subsystems/ETHIK/core/basic_ethik_checker.py`. *(File created)*
        *   [x] Implement basic PII detection logic (e.g., regex for email, phone - needs refinement based on actual requirements). *(Implemented in BasicEthikChecker)*
        *   [x] Implement basic keyword blocklist filtering. *(Implemented in BasicEthikChecker)*
        *   [x] Add unit tests for the new checker's logic. *(Created tests/core/test_basic_ethik_checker.py)*
        *   [ ] Update relevant configurations or injection points to use `BasicEthikChecker` instead of `DummyEthikChecker`.
    *   **Status:** In Progress
    *   **Priority:** HIGH

---

## Future Phases (Placeholder)

*   Implement advanced content analysis (bias detection, toxicity).
*   Develop logic for handling complex PDD `ethik_guidelines`.
*   Integrate with Mycelium for shared blocklists or ethical event reporting.
*   Develop mechanisms for the "fair exchange" validation concept.

---

✧༺❀༻∞ EGOS ∞༺❀༻✧
