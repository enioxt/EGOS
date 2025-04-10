# EGOS Website Design Guide v1.0

**Status:** Initial Draft
**Source Analysis:** `research/EGOS design GROK.txt`, `research/Análise e Refinamento do Projeto EGOS_.txt`
**Date:** 2025-04-09

**Purpose:** This document outlines the core design directives and visual identity for the EGOS project website, aiming to reflect its unique philosophy of ethical, conscious, modular AI combined with art, beauty, and unconditional love.

---

## 1. Core Philosophy & Tone

* **Tone:** Human, artistic, fluid, democratic, economical, beautiful, loving, transparent, clear, trustworthy, innovative, profound but accessible.
* **Avoid:** Corporate jargon, clichés, hype, fake promises, purely technical or cold language.
* **Goal:** Convey the *spirit* and *soul* of EGOS, fostering connection and understanding, not just function.
* **Transparency:** Clearly label under-development features. The site itself acts as a living roadmap.

## 2. Visual Themes & Metaphors

* **Primary Metaphor (Interconnection):** Mycelium network. Visualize connections between subsystems and concepts organically.
* **Modularity:** Represent subsystems as distinct yet connected modules/blocks/nodes.
* **Ethics:** Use subtle symbols like balanced scales or shields (integrated, not just overlaid).
* **Consciousness:** Explore visual representations like evolving light patterns, brain-like networks, or mandalas.
* **Love/Humanity:** Integrate warmth through color, imagery (abstract or potentially community photos later), and inviting interactions.
* **Overall:** Blend futuristic/technological elements with organic/natural forms.

## 3. Mood Board Concepts (To be developed visually)

* Combine clean, modern tech interfaces with textures/patterns inspired by nature (wood grain, leaf veins, mycelium).
* Mix cool, trustworthy blues/greens with accents of warm, inviting pinks/oranges/purples.
* Focus on generative or abstract art that evokes connection, growth, and complexity.

## 4. Color Palette

* **Primary:** Deep blue (e.g., `#003366`) - Trust, professionalism, depth.
* **Secondary:** Emerald green (e.g., `#4CAF50`) - Growth, ethics, nature, harmony.
* **Accents:**
  * Soft pink (e.g., `#FFB6C1`) - Love, warmth, humanity.
  * Lavender/Purple (e.g., `#E6E6FA`) - Creativity, spirituality, innovation.
* **Neutrals:** White (`#FFFFFF`), Light Grays (e.g., `#F5F5F5`, `#EAEAEA`) - Clarity, background, readability.
* **Usage:** Use neutrals predominantly for background/text. Use primary/secondary for key sections/elements. Use accents purposefully for calls-to-action, highlights, or specific conceptual links.

## 5. Typography

* **Headings (h1-h3):** Playfair Display (Serif) - Provides artistry, depth, philosophical feel. Ensure sufficient weight for readability.
* **Body Text / UI Elements:** Inter (Sans-serif) - Modern, highly readable, accessible, excellent range of weights.
* **Hierarchy:** Establish clear typographic scale for headings, subheadings, body text, captions, buttons.
* **Accessibility:** Ensure sufficient contrast ratios for all text against backgrounds.

## 6. Layout Principles

* **Foundation:** Use a flexible grid system (e.g., 12-column) for underlying structure and alignment.
* **Flow:** Allow for organic flow and asymmetry where appropriate to reflect natural/mycelial themes. Avoid rigid boxes exclusively.
* **Whitespace:** Use generously to create a clean, uncluttered, thoughtful feel. Enhances readability and focus.
* **Visual Hierarchy:** Guide the user's eye using size, weight, color, and placement. Key messages (Mission, Vision) should be prominent.
* **Modularity:** Design components (cards, buttons, etc.) that can be reused consistently.

## 7. Visual Representations of Abstract Concepts

* **Mycelium Network:** Background textures, subtle animated connecting lines, node-link diagrams (potentially interactive via JS library like D3.js, Cytoscape.js - Requires research `RESEARCH-VISUALIZATION`).
* **Subsystems/Modularity:** Distinct cards or interactive 3D nodes/blocks with unique icons/colors, visually connected.
* **ATLAS (Cartography):** Interactive map/graph visualization (Requires research `RESEARCH-VISUALIZATION`).
* **ETHIK (Ethics):** Subtle integration of scale/shield motifs, perhaps color-coding or icons in relevant UI sections, transparency in presenting ethical checks/balances.
* **$ETHIK Token:** Needs specific design based on technical implementation (`RESEARCH-ETHIK-ARCH`). Could be a numerical display with an icon, a visual progress bar for rewards, or integrated into community profiles.

## 8. Community & Living Roadmap Integration

* **Living Roadmap:** Interactive timeline visualization (e.g., horizontal scroll, vertical list with status indicators). Link milestones to GitHub issues/PRs/discussions. Clearly show past, present, future.
* **Community Section ("Join the Journey"):**
  * Clear calls-to-action for contribution (code, docs, feedback).
  * Explanation of the $ETHIK token system (purpose, earning, utility - Requires clarification).
  * Direct links to GitHub repository, discussions, other community channels.
  * Potentially feature contributor spotlights or recent activity.

## 9. Interactivity & Animation

* **Subtlety:** Animations should be purposeful, enhance understanding, and guide the user, not distract.
* **Examples:**
  * Fade-in/subtle transitions on scroll.
  * Meaningful hover states on cards, links, buttons (e.g., slight scale, color change, revealing info).
  * Interactive diagrams (subsystems, roadmap) responding to user input.
  * Loading indicators for dynamic content.
* **Feedback:** Implement clear visual feedback for user actions (e.g., button clicks, form submissions).
* **Consider:** JS libraries like GSAP for complex animations if needed, but prioritize CSS transitions/animations for performance where possible.

## 10. Accessibility (WCAG AA Target)

* Ensure all design choices (color, typography, layout, interaction) meet WCAG AA guidelines.
* Provide text alternatives for non-text content.
* Ensure keyboard navigability and visible focus states.
* Design interactive elements and custom visualizations accessibly (Requires research `RESEARCH-WCAG`).

---
*This guide provides the initial direction. Visual design prototypes (Figma) and technical research will further refine these concepts.*
