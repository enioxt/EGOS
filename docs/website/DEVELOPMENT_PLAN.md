# EGOS Website Development Plan v1.0

**Status:** Initial Draft
**Source Analysis:** `research/EGOS design GROK.txt`, `research/Análise e Refinamento do Projeto EGOS_.txt`, `research/Criaçao de site com IA.txt`
**Core Dependencies:** `ROADMAP.md`, `docs/website/DESIGN_GUIDE.md`
**Date:** 2025-04-09

**Purpose:** This document outlines the detailed phases and tasks for developing the EGOS project website, based on the consolidated strategy and adopted design directives. It serves as a working plan, supplementing the main `ROADMAP.md`.

**Chosen Technical Approach:** Modern JavaScript Framework (Next.js or SvelteKit) with a Headless CMS (e.g., Sanity, Strapi, Decap CMS).

---

## Development Phases & Tasks

*(Note: Task IDs are prefixed with 'W' for Website. Priorities and ETAs are indicative).* 

**Phase WD: Website Design Definition (Status: DONE)**

*   **Goal:** Generate concrete, EGOS-aligned design directives.
*   `[DONE]` **Task WD-1:** Generate Core Design Directives (Internal analysis complete, see `research/EGOS design GROK.txt`).
*   `[DONE]` **Task WD-2:** Document Design Directives (Initial draft created in `docs/website/DESIGN_GUIDE.md`).

**Phase WIA: Website Information Architecture (Status: In Progress)**

*   **Goal:** Define the website's structure, navigation, and basic user flow.
*   **Depends On:** Task WD-2
*   `[In Progress]` **Task WIA-1:** Define Sitemap. List main pages/sections (Home, Philosophy, Principles, Subsystems, Community/$ETHIK, Roadmap, Genki Dama, Feedback, etc.). (`HIGH`)
*   `[Planned]` **Task WIA-2:** Define Navigation Structure. Plan top navigation, footer links, and key internal linking strategy. (`HIGH`)
*   `[Planned]` **Task WIA-3:** Outline Key User Flows. Map basic journeys for target personas (researcher, contributor, curious visitor) - *Requires UX Research (Phase WUX)*. (`MEDIUM`)

**Phase WUX: User Experience Research (Status: Planned - Parallel)** 

*   **Goal:** Deepen understanding of target audience needs and refine UX strategy.
*   `[Planned]` **Task WUX-1:** Conduct User Research (Surveys/Interviews) with target personas (e.g., "Contribuidor Técnico", "Pesquisador Ética em IA"). (`MEDIUM`)
*   `[Planned]` **Task WUX-2:** Develop Detailed Personas based on research. (`MEDIUM`)
*   `[Planned]` **Task WUX-3:** Refine User Journeys based on personas and research. (`MEDIUM`)

**Phase WP: Prototyping (Status: Planned)**

*   **Goal:** Create visual representations of the website structure and key interactions.
*   **Depends On:** Phase WIA, Phase WUX
*   `[Planned]` **Task WP-1:** Create Wireframes based on IA, User Flows & Design Guide. (`MEDIUM`)
*   `[Planned]` **Task WP-2:** Create High-Fidelity Mockups (e.g., Figma) based on Wireframes & Design Guide. (`HIGH`)
*   `[Planned]` **Task WP-3:** Prototype Key Interactions (Optional - e.g., Figma, Framer). (`LOW`)

**Phase WR: Technical Research (Status: Planned - Parallel)**

*   **Goal:** Investigate and define technical solutions for complex features.
*   `[Planned]` **Task WR-1:** Research/Prototype Visualization Techniques for ATLAS/MYCELIUM (e.g., D3.js, Three.js, Cytoscape.js, Sigma.js). Define chosen library/approach & assess performance/accessibility. (`MEDIUM`)
*   `[Planned]` **Task WR-2:** Define $ETHIK Integration Architecture & Security Plan (Frontend interaction [Web3.js/Ethers.js], Backend/API needs, Wallet/Contract interaction model, Security protocols). (`MEDIUM`)
*   `[Planned]` **Task WR-3:** Research WCAG Implementation for Custom Visualizations & Web3 Interactions (Focus on WCAG 2.1/2.2 AA). Document specific requirements and techniques. (`MEDIUM`)

**Phase WF: Frontend Development (Status: Planned)**

*   **Goal:** Build the user-facing website based on designs, IA, and technical research.
*   **Depends On:** Phase WP, Phase WR, Framework Choice (Next.js/SvelteKit), Headless CMS Choice
*   `[Planned]` **Task WF-1:** Setup Project (Next.js/SvelteKit) & Headless CMS Integration (e.g., Sanity/Strapi/Decap). (`HIGH`)
*   `[Planned]` **Task WF-2:** Implement Base Layout & Global Styles (CSS Modules/Tailwind/Styled Components, based on Design Guide). (`HIGH`)
*   `[Planned]` **Task WF-3:** Develop Reusable Components (Cards, Buttons, Nav, Footer, etc.). (`HIGH`)
*   `[Planned]` **Task WF-4:** Build Static Pages/Sections based on IA & Mockups (Utilizing SSR/SSG for performance). (`HIGH`)
*   `[Planned]` **Task WF-5:** Implement Core JS Interactivity (Hamburger, Toggles, Language Switcher Refinement using `i18next`). (`MEDIUM`)
*   `[Planned]` **Task WF-6:** Implement i18n Content Population via Headless CMS. (`MEDIUM`)
*   `[Planned]` **Task WF-7:** Implement ATLAS/MYCELIUM Visualizations (using chosen library from WR-1). (`HIGH`)
*   `[Planned]` **Task WF-8:** Implement $ETHIK Frontend Elements (Display, Interaction - based on Task WR-2). (`MEDIUM`)
*   `[Planned]` **Task WF-9:** Implement Living Roadmap Visualization (potentially sourcing data from CMS or API - GitHub/CMS). (`MEDIUM`)
*   `[Planned]` **Task WF-10:** Implement Community Section Frontend (Contribution info, $ETHIK explanation, Forum/Discussion links). (`MEDIUM`)
*   `[Planned]` **Task WF-11:** Implement Genki Dama Page. (`LOW`)
*   `[Planned]` **Task WF-12:** Implement Accessibility Features (ARIA, Keyboard Nav, Focus States - based on Task WR-3, check with WAVE/Axe). (`HIGH`)
*   `[Planned]` **Task WF-13:** Implement Responsive Design across all components/pages. (`HIGH`)

**Phase WB: Backend Development (Status: Planned)**

*   **Goal:** Develop necessary server-side logic, primarily for QPG, LLM Chat, and potential $ETHIK interactions.
*   **Depends On:** Phase WIA, Phase WR (specifically WR-2)
*   `[Planned]` **Task WB-1:** Design & Implement QPG Backend API. (`MEDIUM` - Part of QPG1)
*   `[Planned]` **Task WB-2:** Implement QPG LLM Integration (Free/Paid Tiers). (`MEDIUM` - Part of QPG1)
*   `[Planned]` **Task WB-3:** Design & Implement LLM Chat Backend Service (for website integration). (`HIGH` - Part of LLM Integration Phase 1)
*   `[Planned]` **Task WB-4:** Implement LLM Chat OpenRouter Integration + RAG. (`HIGH` - Part of LLM Integration Phase 2)
*   `[Planned]` **Task WB-5:** Implement Secure API Key Handling (Secrets Manager). (`CRITICAL`)
*   `[Planned]` **Task WB-6:** Implement Rate Limiting (IP/User). (`HIGH`)
*   `[Planned]` **Task WB-7:** Develop $ETHIK Backend Logic/API (if required by chosen architecture in WR-2 - Secure interactions). (`MEDIUM`)

**Phase WC: Content Population & Strategy (Status: Planned)** 

*   **Goal:** Populate the website with final, approved content aligned with the content strategy.
*   **Depends On:** Phase WIA, Headless CMS Setup (Part of WF-1)
*   `[Planned]` **Task WC-1:** Develop Content Strategy (Storytelling, Educational Resources - UNESCO ref, Blog/News plan, Tone of Voice). (`MEDIUM`)
*   `[Planned]` **Task WC-2:** Write/Adapt Final Website Copy (aligned with Tone, IA, Design, Content Strategy). (`HIGH`)
*   `[Planned]` **Task WC-3:** Populate Headless CMS (e.g., Sanity/Strapi/Decap) with structured content. (`HIGH`)
*   `[Planned]` **Task WC-4:** Source/Create Final Imagery & Assets (Illustrations, Icons, Photos - align with Design Guide). (`MEDIUM`)

**Phase WT: Testing & QA (Status: Planned - Ongoing Throughout)**

*   **Goal:** Ensure website quality, functionality, performance, security, and accessibility.
*   `[Planned]` **Task WT-1:** Unit/Integration Tests for Frontend (e.g., Jest/Vitest, Playwright/Cypress). (`HIGH`)
*   `[Planned]` **Task WT-2:** Unit/Integration Tests for Backend Services. (`HIGH`)
*   `[Planned]` **Task WT-3:** End-to-End Testing (e.g., Playwright/Cypress). (`MEDIUM`)
*   `[Planned]` **Task WT-4:** Accessibility Testing (Manual + Automated - Axe, WAVE, WCAG Check). (`CRITICAL`)
*   `[Planned]` **Task WT-5:** Cross-Browser/Device Testing. (`HIGH`)
*   `[Planned]` **Task WT-6:** Performance Testing (Lighthouse, k6, WebPageTest). (`MEDIUM`)
*   `[Planned]` **Task WT-7:** Security Testing/Audit (OWASP ZAP, Manual Review - especially for Backend & $ETHIK). (`HIGH`)
*   `[Planned]` **Task WT-8:** Usability Testing with target personas (based on WUX). (`MEDIUM`)

**Phase WDE: Deployment & Monitoring (Status: Planned)**

*   **Goal:** Launch the website and establish monitoring.
*   **Depends On:** Phase WT Completion
*   `[Planned]` **Task WDE-1:** Setup Hosting (e.g., Vercel, Netlify) & CI/CD Pipeline (GitHub Actions). (`HIGH`)
*   `[Planned]` **Task WDE-2:** Configure Domain & DNS. (`MEDIUM`)
*   `[Planned]` **Task WDE-3:** Implement Analytics (e.g., GA4). (`MEDIUM`)
*   `[Planned]` **Task WDE-4:** Setup Error Monitoring (e.g., Sentry). (`MEDIUM`)
*   `[Planned]` **Task WDE-5:** Launch Website (Initial Phase). (`HIGH`)
*   `[Planned]` **Task WDE-6:** Post-Launch Monitoring & Maintenance Plan (incl. user feedback loop via Tidio/form). (`MEDIUM`)

---
*This plan incorporates insights from multiple analyses and adopts a JS Framework approach. It will be refined as technical research (WR) and UX research (WUX) progress.* 
