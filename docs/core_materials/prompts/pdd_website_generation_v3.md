\
---
metadata:
  author: Enio Pro (via EVA & GUARANI)
  backup_required: true
  category: PROMPT_DESIGN_DOCUMENT
  description: PDD for generating the initial EGOS project website (HTML, CSS, JS) based on the detailed design concept v3.
  documentation_quality: 0.8 # Based on provided prompt detail
  encoding: utf-8
  ethical_validation: true # Ensures visual design reflects ethics
  last_updated: '2025-04-09' # Current Date
  owner: CORUJA / KOIOS
  related_files:
    - docs/research/WebSite Enio Grok e Gemini.txt
    - docs/website/index.html # Target output
    - docs/website/css/style.css # Target output
    - docs/website/js/script.js # Target output
    - .cursor/rules/quantum_prompt_core.mdc
  required: true # Core website generation
  review_status: final # Based on user-provided prompt
  security_level: 0.5 # Public website generation instructions
  subsystem: KOIOS # Prompt definition standard
  type: documentation
  version: '1.0' # PDD version
  windows_compatibility: true
---

# Prompt Design Document: EGOS Website Initial Code Generation (v3)

**PDD Version:** 1.0
**Date:** 2025-04-09
**Prompt Goal ID:** `WEBSITE-GEN-001`

## 1. Goal & Objective

*   **Goal:** Generate the initial front-end codebase (HTML, CSS, basic JS) for the public-facing EGOS project website.
*   **Objective:** Create a functional, well-structured, and visually aligned starting point for the website that adheres strictly to the provided detailed design concept (v3) and EGOS principles (minimalism, modularity, ethics).

## 2. Target AI Model(s)

*   **Primary:** Models suited for complex instruction following and code generation (e.g., Claude Sonnet, GPT-4o).
*   **Secondary:** Models potentially used for specific sub-tasks if needed (e.g., Gemini Pro for analysis/planning, although the prompt is highly prescriptive).

## 3. Prompt Text

```plaintext
# Instruction for Website Code Generation – EGOS Project (v3 – Based on Detailed Design Concept)

**Your Role:** You are an expert front-end developer with a strong aesthetic sense, a focus on usability, and experience implementing modern and interactive designs. Your task is to generate the initial code (HTML, CSS, basic JS) for the EGOS project website, strictly following the specifications from the detailed design concept provided as reference.

**EGOS Project Context:**
* **Name:** EGOS (Evolutionary Gnostic Operating System) – AI Ecosystem.
* **Main Repository:** `https://github.com/enioxt/egos`
* **Design Concept Reference:** Based on the report "Website Design Concept for the EGOS Project Integrated with LLMs" (The LLM should assume implicit access to the details of this concept, including 2025 trends, examples, tables, etc.).
* **Philosophy:** Deep ethics, modularity, consciousness, love, compassion, privacy.
* **Confirmed Subsystems:** ATLAS, NEXUS, CRONOS, ETHIK, HARMONY, KOIOS, CORUJA.
* **Technology Stack:** Python, Asyncio, LLMs (Gemini, Claude), integration via OpenRouter with 'quasar-alpha'.
* **Desired Tone:** Human, accessible, inspiring, clear—reflecting depth without excessive jargon.

**Website Goals:**
* Create a unique, modern, minimalist, intuitive, and high-performance online platform that effectively communicates EGOS's complex vision.
* Visually reflect the core values: ethics, modularity, and consciousness.
* Functionally and visually integrate the 'quasar-alpha' LLM for user assistance.
* Be fully responsive (mobile, tablet, desktop) and performance-optimized.

**Detailed Implementation Requirements (Based on Design Concept v2):**

1. **General Structure (HTML - `index.html`):**
    * Semantic HTML5. Single-page application (SPA) with anchor-based navigation.
    * **Main Sections (`<main>`):**
        * `#hero`: Initial visual impact, concise title, mission subtitle, CTA "Discover Our Vision". Use a subtle gradient background or abstract illustration placeholder.
        * `#about`: Detailed presentation of EGOS (base placeholder on README content but written in an accessible tone like "AI that feels...").
        * `#principles`: Clear highlight of ethical/philosophical principles. Use placeholders for minimalist representative icons.
        * **Subsystems (Create a main section `#subsystems-overview` and/or individual sections):** `#atlas`, `#nexus`, `#cronos`, `#ethik`, `#harmony`, `#koios`, `#coruja`. Follow specific design guidelines for each (see section 4 below).
        * `#journey` (Optional but recommended): Placeholder for a visual timeline of the project's evolution.
        * `#participate`: Strong CTA ("Join the Future"), contact info (email placeholder), collaboration links (placeholders).
    * **Header (`<header>`):** Fixed at the top. Placeholder for EGOS logo. Main navigation (`<nav>`).
    * **Navigation (`<nav>`):** Clear links to `#hero`, `#about`, `#principles`, `#subsystems-overview` (or individual links for each subsystem), `#participate`, and potentially `#journey` and `#documentation` (if applicable). Implement hamburger menu for mobile view.
    * **Footer (`<footer>`):** Copyright (current year), placeholders for social media links (Facebook, X, LinkedIn), and link to GitHub.

2. **Styling (CSS - `style.css` - Based on Concept v2):**
    * **Minimalism:** Strictly applied: generous whitespace, clean layout, content-focused, clear visual hierarchy.
    * **Responsiveness:** Mobile-first. Well-defined media queries for tablet/desktop. Use Grid/Flexbox for flexible layouts.
    * **Color Palette:** Primary: Deep Blue (`#0A2342` approx.) for trust/stability. Accent: Warm Orange (`#FF6600` approx.) for CTAs/key elements. Background: White/very light gray. Ensure high contrast and accessibility.
    * **Typography:** `Inter` for body text (maximum readability). `Playfair Display` for headings (elegance). Define font sizes and weights for clear hierarchy (h1, h2, h3, p).
    * **Visual Elements:** Include commented placeholders for:
        * Custom abstract illustrations (hero, sections).
        * Minimalist icons (principles, subsystems).
        * Potential AI-generated art backgrounds (commented as optional).
    * **CSS Interactivity:**
        * Smooth transitions on link/button hover.
        * Styles for interactive subsystem cards (normal and hover/expanded states).
        * Styles for hamburger menu (open/closed).
        * Comment where more complex animations (subsystem connections, parallax or fade-in scroll effects) should occur (JS may be required).

3. **Content (Placeholders):**
    * Use placeholder text simulating the human/accessible tone.
    * For `#about`, use text inspired by the README.
    * For each subsystem section (`#atlas` to `#coruja`), include placeholders briefly describing their purpose as detailed in Table 2 of the "Design Concept", and indicate where diagrams, flowcharts, or specific interactive elements should be inserted.

4. **Subsystem-Specific Requirements (HTML/CSS/Placeholders):**
    * **`#atlas`:** Placeholder for high-level diagram/interactive model. Placeholder for contextual LLM definitions.
    * **`#nexus`:** Placeholder for interactive flowchart/data visualization. Placeholder for contextual LLM explaining data flow.
    * **`#cronos`:** Placeholder for interactive timeline/calendar. Placeholder for contextual LLM (dates/milestones).
    * **`#ethik`:** Clear display of principles. Placeholder for icons. Placeholder for contextual LLM (principles explanation). Structure for expandable sections.
    * **`#harmony`:** Placeholder for network diagram/interconnection visualization. Placeholder for contextual LLM (interaction explanation). Comment where flow animations between subsystems would go.
    * **`#koios`:** Placeholder for search functionality (potentially with LLM input). Placeholder for interactive knowledge map. Placeholder for contextual LLM (documentation search).
    * **`#coruja`:** Placeholder for interactive data visualizations/dashboards. Placeholder for contextual LLM (metrics explanation). Comment where animated charts would be added.
    * **Interactive Cards (General for subsystems):** Implement HTML/CSS structure for cards that expand on hover/click to show more details and GitHub link (placeholder).

5. **LLM 'quasar-alpha' Integration (Placeholders):**
    * **Chatbot:** Include a floating icon (placeholder, e.g., bottom-right corner) that would eventually open the chatbot interface. Style the icon placeholder.
    * **Contextual Help:** In each subsystem section, include a subtle icon (placeholder, e.g., '?') that would eventually trigger the LLM to provide context-specific explanations.

6. **JavaScript (Basic Initial - `script.js`):**
    * Implement toggle functionality for the mobile hamburger menu.
    * Implement basic expand/collapse functionality for subsystem interactive cards (on hover or click).
    * Add clear comments indicating where more advanced JS logic will be needed (scroll animations, diagram interactions, chatbot/contextual help logic).

7. **Performance (Code Comments):**
    * Include reminder comments in HTML/CSS/JS on where to apply optimizations:
        ```html
        <!-- TODO: Lazy load images -->
        ```
        ```css
        /* TODO: Minify CSS (CSSNano) */
        ```
        ```js
        // TODO: Minify JS (UglifyJS) & use async/defer loading
        ```

**Output Format:**
* Separate files: `index.html`, `style.css`, `script.js`.
* Well-commented code, explaining structure, placeholders, and where real content or more complex logic is needed.
```

## 4. Context Requirements

*   **Implicit Context:**
    *   Access to the details within the "Website Design Concept for the EGOS Project Integrated with LLMs" report (`docs/research/WebSite Enio Grok e Gemini.txt`), including trends, examples, tables (especially Table 2 for subsystem content).
    *   Understanding of EGOS subsystems (ATLAS, NEXUS, CRONOS, ETHIK, HARMONY, KOIOS, CORUJA).
    *   Understanding of EGOS philosophy (ethics, modularity, consciousness, etc.).
    *   Knowledge of modern front-end development best practices (HTML5, CSS3, JS, Responsiveness, SPA).
*   **Explicit Context (Provided):**
    *   EGOS Project Name, Repo URL.
    *   Technology Stack (Python, Asyncio, LLMs, OpenRouter/quasar-alpha - relevant for integration placeholders).
    *   Desired Tone.
    *   Specific color codes (`#0A2342`, `#FF6600`), fonts (`Inter`, `Playfair Display`).
    *   Detailed structure for HTML sections, header, nav, footer.
    *   Specific CSS requirements (minimalism, responsiveness, colors, typography, placeholders, interactivity).
    *   Placeholder content guidelines.
    *   Subsystem-specific visual/interactive element placeholders.
    *   LLM integration placeholders (chatbot icon, contextual help icon).
    *   Basic JS functionality requirements (menu toggle, card interaction).
    *   Performance comment requirements.
    *   Required output file names (`index.html`, `style.css`, `script.js`).

## 5. Expected Output Format & Structure

*   **Files:** Three distinct files: `index.html`, `style.css`, `script.js`.
*   **Content:** Code adhering to all specified requirements.
*   **Placeholders:** Liberal use of comments and placeholder text/elements as specified (e.g., `<!-- Placeholder for ATLAS diagram -->`, `// TODO: Implement chatbot UI logic`).
*   **Comments:** Well-commented code explaining structure, choices (where not obvious), and indicating where further development is needed.
*   **Language:** All code, comments, and text must be in **English**.

## 6. Evaluation Criteria

*   **Completeness:** Does the output include all requested HTML sections, CSS rules (or placeholders), and basic JS functions?
*   **Accuracy:** Does the generated code accurately reflect the specified requirements (colors, fonts, structure, responsiveness approach, etc.)?
*   **Adherence to Design Concept:** Does the output align with the principles and details described in the referenced design concept (minimalism, modularity)?
*   **Code Quality:** Is the code well-structured, readable, and use semantic HTML? Are comments clear and helpful?
*   **Placeholder Usage:** Are placeholders used correctly to indicate where real content, complex JS, or visual assets are needed?

## 7. Potential Challenges & Mitigation

*   **Ambiguity in Design Concept:** Although the prompt assumes implicit access, the AI might misinterpret subtle aspects of the design document.
    *   **Mitigation:** The prompt is highly specific, reducing ambiguity. If issues arise, provide specific clarifications or snippets from the design doc.
*   **CSS Complexity:** Implementing all CSS details perfectly (especially responsiveness and subsystem card interactions) might require iteration.
    *   **Mitigation:** Focus on generating the correct structure and basic styles first. Refine complex CSS or JS interactions in subsequent steps. The prompt already requests comments for complex parts.
*   **LLM Integration Nuances:** Representing LLM integration points purely with placeholders might be abstract.
    *   **Mitigation:** The prompt clearly asks for icon placeholders and comments, which is sufficient for the initial structure. Actual implementation is a separate, later task.

## 8. Ethical Considerations (ETHIK Review)

*   **Accessibility:** The prompt requires ensuring high contrast and clear visual hierarchy, aligning with accessibility principles. Code generation should follow semantic HTML practices.
*   **Transparency:** The use of placeholders and comments ensures clarity about the current state and future work.
*   **Tone:** The requirement for a human, accessible tone aligns with EGOS's communication principles.
*   **Visual Representation:** The design choices (minimalism, colors) aim to visually reflect EGOS's ethical and philosophical pillars.

## 9. Iteration & Improvement Log

*   **v1.0 (2025-04-09):** Initial PDD created based on the user-provided v3 prompt.

---
✧༺❀༻∞ EGOS ∞༺❀༻✧ 
