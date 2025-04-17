# EGOS Website Roadmap

This document outlines the development roadmap for the EGOS website.

## Legend

-   **Status:** To Do | In Progress | Done | Blocked
-   **Subsystem[s]:** Frontend | Backend | UI/UX | Infra | Docs | Core | etc.
-   **Task ID:** Unique identifier (e.g., WEB-001)
-   **Priority:** Critical | High | Medium | Low
-   **Description:** Clear description of the task.
-   **Dependencies:** Any blocking tasks (Task IDs).
-   **Principles:** Relevant EGOS principles (e.g., Modularity, Accessibility).

---

## Phase 1: Foundation & Landing Page

| Status | Subsystem[s] | Task ID | Priority | Description                                                                                                | Dependencies | Principles                |
| :----- | :----------- | :------ | :------- | :--------------------------------------------------------------------------------------------------------- | :----------- | :------------------------ |
| Done   | Frontend, UI/UX | WEB-001 | Critical | Migrate core landing page components (Header, Hero, Principles, Subsystems, CTA, Footer) from `lovable` project. | -            | Modularity, Preservation |
| Done   | Frontend, UI/UX | WEB-002 | High     | Set up Shadcn/UI and Tailwind CSS configuration.                                                        | -            | Modularity                |
| Done   | Frontend, UI/UX | WEB-003 | High     | Integrate migrated components into the main landing page (`src/app/page.tsx`).                             | WEB-001      | Modularity                |
| Done   | Frontend, UI/UX | WEB-005 | High     | Fix SVG components and animations for visual elements.                                                   | WEB-002      | Universal Accessibility  |
| Done   | Frontend, UI/UX | WEB-004 | Medium   | Test and verify the appearance and functionality of the landing page components.                           | WEB-003      | Integrated Ethics        |
| To Do  | Frontend, I18n | WEB-006 | Low      | Implementar suporte a internacionalização (i18n) para português e inglês.                                  | WEB-004      | Universal Accessibility  |
