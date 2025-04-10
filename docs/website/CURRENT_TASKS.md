# EGOS Website - Current Development Tasks (Temporary)

**Purpose:** Tracks immediate, active tasks for website development based on `DEVELOPMENT_PLAN.md`. Progress here should be reflected back into `ROADMAP.md` upon completion of phases/major milestones.

**Date:** 2025-04-09

---

## Phase WIA: Website Information Architecture (Status: In Progress)

* **Goal:** Define the website's structure, navigation, and basic user flow based on core content and the adopted design directives (`docs/website/DESIGN_GUIDE.md`).
* **Depends On:** `WEBSITE-DESIGN-DIRECTIVES` (Task WD-2 in `ROADMAP.md` - Status: DONE)

**Completed Tasks (Phase WIA):**

* [X] **Task WIA-1:** Define Sitemap. List main pages/sections (Home, Philosophy, Principles, Subsystems, Community/$ETHIK, Roadmap, Genki Dama, Feedback, etc.). (`HIGH`)
* [X] **Task WIA-2:** Define Navigation Structure. Plan top navigation, footer links, and key internal linking strategy. (`HIGH`, `depends_on: [WIA-1]`)

**Pending Tasks (Phase WIA):**

* [ ] **Task WIA-3:** Outline Key User Flows. Map basic journeys for target personas (researcher, contributor, curious visitor). (`MEDIUM`, `depends_on: [WIA-1, WUX]`)

**Upcoming Tasks (Phase WIA):**

---

## Phase WUX: User Experience Research (Status: In Progress)

* **Goal:** Deepen understanding of target audience needs and refine UX strategy.

**Active Task:**

* [ ] **Task WUX-1a (Sub-task):** Conduct Analogous Site Analysis. Analyze 3-5 relevant sites (e.g., Hugging Face, Kubernetes.io, Center for Humane Tech, ENS) through persona lenses to inform research goals. Document findings in `research/website_ux_analysis.md`. (`MEDIUM`)

**Upcoming Tasks (Phase WUX):**

* [ ] **Task WUX-1b (Sub-task):** Plan & Execute Targeted Community Questions/Survey based on analysis findings. (`MEDIUM`, `depends_on: [WUX-1a]`)
* [ ] **Task WUX-1c (Sub-task):** Review Internal Documentation (MQP, Strategy) for intended user needs. (`LOW`, `depends_on: [WUX-1a]`)
* [ ] **Task WUX-2:** Develop Detailed Personas based on research. (`MEDIUM`, `depends_on: [WUX-1b, WUX-1c]`)
* [ ] **Task WUX-3:** Refine User Journeys based on personas and research. (`MEDIUM`, `depends_on: [WUX-2]`)

---

*(This file will be updated as tasks progress. Subsequent phases like WP (Prototyping), WR (Research), WF (Frontend Dev), etc., will be added here as they become active.)*
