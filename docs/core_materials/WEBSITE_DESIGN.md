# EGOS Website Design Documentation

## Overview

This document summarizes the design, architecture, and implementation plan for the EGOS project website, aligned with the detailed design concept in `research/WebSite Enio Grok e Gemini.txt`.

---

## Design Concept Alignment

- **Minimalism:** Clean layout, whitespace, clear hierarchy.
- **Color Palette:** Deep Blue `#0A2342`, Warm Orange `#FF6600`, light backgrounds.
- **Typography:** Inter (body), Playfair Display (headings).
- **Subsystem-Centric:** Sections for ATLAS, NEXUS, CRONOS, ETHIK, HARMONY, KOIOS, CORUJA.
- **LLM Integration:** Chatbot placeholder, contextual help icons planned.
- **Interactivity:** Expandable cards, hamburger menu, planned animations.

---

## Modular CSS & JS

- **CSS:** Organized by components (`_navigation.css`, `_cards.css`, etc.) and pages (`_quantum_prompts.css`).
- **JS:** Handles hamburger toggle, expandable cards, Quantum Prompts placeholders.
- **Performance:** To be optimized with lazy loading, minification (TODO comments planned).

---

## Multilingual Architecture

- **Languages:** English, Portuguese, Spanish implemented; placeholders for French, German, Russian, Chinese.
- **Structure:** `.lang-content` divs with language-specific content, toggled via JS.
- **Next:** Full localization and translation.

---

## LLM Integration Plan

- **Chatbot:** Floating button placeholder, to be connected to OpenRouter 'quasar-alpha'.
- **Contextual Help:** Planned icons in subsystem sections to trigger LLM responses.
- **Quantum Prompts:** Dedicated page with input/output skeleton, future LLM backend integration.

---

## Current Gaps

- Missing content sections: `#about`, `#journey`, `#participate`.
- Detailed subsystem placeholders (diagrams, flowcharts, LLM help).
- Strict adherence to design concept colors/typography.
- Performance optimization comments.
- Advanced animations and LLM logic.

---

## Next Steps

- Implement missing content sections.
- Add detailed placeholders and contextual help icons.
- Refine CSS and add performance comments.
- Develop LLM integration logic.
- Continuously update documentation.

---

✧༺❀༻∞ EGOS ∞༺❀༻✧

# EGOS Website Development Standards

## 1. Language & Accessibility

- All content, comments, and code **must be in English** (except localized content placeholders).
- Follow accessibility best practices (semantic HTML5, ARIA labels, contrast).

## 2. Structure & Modularity

- Use **semantic HTML5** with clear sectioning (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`).
- Organize CSS modularly by components (`css/components/`), layout (`css/layout/`), base (`css/base/`), etc.
- Organize JS modularly, with clear event listeners and comments.

## 3. Multilingual Support

- Use `.lang-content` divs for each language.
- Toggle visibility via JS.
- Use placeholders for untranslated content.

## 4. Styling & Visual Design

- Follow the design concept in `research/WebSite Enio Grok e Gemini.txt`.
- Color palette: Deep Blue (`--primary-color`), Warm Orange (`--accent-color`), light backgrounds (`--background-color`), defined in `css/base/_variables.css`.
- Typography: Inter (body), Playfair Display (headings), defined in `css/base/_variables.css` and `css/base/_typography.css`.
- Emphasize minimalism: whitespace, clear hierarchy, limited color use.
- Responsive design: mobile-first approach, using media queries.
- **Golden Ratio:** Apply principles of the Golden Ratio (approx. 1:1.618) for spacing, layout proportions (widths, heights), and element sizing where appropriate to enhance visual harmony.

## 5. Interactivity

- Implement hamburger menu toggle for mobile.
- Implement expandable subsystem cards.
- Add placeholders for future LLM chatbot and contextual help icons.
- Add comments for future animations, LLM integration, and advanced interactivity.

## 6. Performance

- Add TODO comments for:
  - Lazy loading images.
  - Minifying CSS/JS.
  - Async/defer script loading.
- Optimize images for web use.
- Aim for fast load times (e.g., good Lighthouse scores).

## 7. Documentation

- Document website features, design decisions, and changes in `docs/project_documentation/WEBSITE_DESIGN.md`.
- Update `ROADMAP.md` with all website-related tasks and progress.

## 8. Consistency & Compliance

- Follow KOIOS standards for code quality, documentation, and commit messages.
- Align with ETHIK principles (privacy, accessibility, clarity).
- **Visual Consistency:** Ensure related user interfaces (e.g., the Streamlit dashboard) visually align with the main website's color palette, typography, and overall style to maintain a cohesive brand identity.
