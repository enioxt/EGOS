// NOTE: Assuming Task interface is exported from Roadmap.tsx or moved later
export interface Task {
  id: string;
  title: string;
  status: 'Planned' | 'In Progress' | 'Completed' | 'Blocked' | 'DONE';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  subsystem?: string;
  phase?: string;
  description?: string;
  details: string;
  link?: string; // GitHub URL for code or issue
}

export const roadmapTasks: Task[] = [
  // --- Phase 2a: Initial Framework & Standards --- (KOIOS Lead)
  { id: 'KOIOS-STD-STRUCT', title: 'Standardize Project Structure & Basic READMEs', status: 'DONE', priority: 'CRITICAL', subsystem: 'KOIOS', phase: '2a', details: '[DONE] Standardize Project Structure & Basic READMEs (`CRITICAL`)' },
  { id: 'KOIOS-STD-COMMIT', title: 'Implement Conventional Commit Standards', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', details: '[DONE] Implement Conventional Commit Standards (`HIGH`)' },
  { id: 'KOIOS-STD-PYTHON', title: 'Define Core Python Coding Standards (PEP8, Typing)', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', details: '[DONE] Define Core Python Coding Standards (PEP8, Typing) (`HIGH`)' },
  { id: 'KOIOS-STD-LOGGING', title: 'Implement Logging Standards', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', details: '[DONE] Implement Logging Standards (`HIGH`)' },
  { id: 'KOIOS-STD-DOCSTRINGS', title: 'Establish Basic Documentation Standards (Docstrings)', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', details: '[DONE] Establish Basic Documentation Standards (Docstrings) (`HIGH`)' },
  { id: 'KOIOS-PRECOMMIT', title: 'Set up Pre-Commit Hooks (ruff, black)', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', details: '[DONE] Set up Pre-Commit Hooks (ruff, black) (`HIGH`)' },
  { id: 'KOIOS-META-SCHEMA', title: 'Define Metadata Schema for MDC Rules', status: 'DONE', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', details: '[DONE] Define Metadata Schema for MDC Rules (`MEDIUM`)' },
  { id: 'KOIOS-CURSOR-AGENT', title: 'Activate Cursor Agent Mode', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS/AI', phase: '2a', details: '[DONE] **Activate Cursor Agent Mode:** Transitioned from Chat to Agent, enabling direct file/terminal interaction. (`HIGH` - See `docs/ai_integration/cursor_agent_mode.md`)' },
  { id: 'KOIOS-RULES-CONSOLIDATE', title: 'Consolidate `.cursor/rules`', status: 'DONE', priority: 'HIGH', subsystem: 'KOIOS', phase: '2a', details: '[DONE] **Consolidate `.cursor/rules`:** Reviewed all `.cursor/rules/*.mdc` files, consolidating or linking them into `global_rules.mdc` as the central source of truth for project standards. (`HIGH`)' },
  { id: 'KOIOS-REFACTOR-META', title: 'Refactor Subsystems for Metadata Compliance', status: 'In Progress', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', details: '[In Progress] Refactor Subsystems for Metadata Compliance (`MEDIUM`)' },
  // --- Phase 2a: Documentation Tasks (Continued) ---
  { id: 'KOIOS-DOC-RU-01', title: 'Document Rationale for File Handling Rules', status: 'Planned', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', details: '[Planned] [KOIOS][DOC-RU-01] Document Rationale for File Handling Rules (`Existence Check`, `Comprehensive Search`) in KOIOS standards (`MEDIUM`)' },
  { id: 'KOIOS-DOC-BP-FS-01', title: 'Add "Best Practices for File Search/Creation" to Docs', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', details: '[Planned] [KOIOS][DOC-BP-FS-01] Add "Best Practices for File Search/Creation" section to relevant documentation (`LOW`)' },
  { id: 'KOIOS-LESSONS-01', title: 'Create/Maintain "Lessons Learned" Log', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', details: '[Planned] [KOIOS][KOIOS-LESSONS-01] Create/Maintain "Lessons Learned" log for AI Collaboration & Onboarding (`LOW`)' },
  { id: 'DOC-HTA-USAGE-01', title: 'Document `analyze_git_history.py` Usage', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS/NEXUS', phase: '2a', details: '[Planned] [KOIOS/NEXUS][DOC-HTA-USAGE-01] Document `analyze_git_history.py` script usage and examples (`LOW`)' },
  { id: 'DOC-README-HTA-01', title: 'Update README with Historical Analysis Link', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', details: '[Planned] [KOIOS][DOC-README-HTA-01] Update main `README.md` to mention historical analysis capability and link report (`LOW`)' },
  { id: 'DOC-CONTRIB-AI-01', title: 'Update CONTRIBUTING.md with AI Collab Rules', status: 'Planned', priority: 'LOW', subsystem: 'KOIOS', phase: '2a', details: '[Planned] [KOIOS][DOC-CONTRIB-AI-01] Update `CONTRIBUTING.md` (or create if needed) with latest AI collaboration rules (`LOW`)' },
  { id: 'KOIOS-DOC-AUDIT-01', title: 'Periodic Review of `.mdc` Rules & Docs', status: 'Planned', priority: 'MEDIUM', subsystem: 'KOIOS', phase: '2a', details: '[Planned] [KOIOS][KOIOS-DOC-AUDIT-01] Perform Periodic Review of `.mdc` rules and `docs/` for consistency and alignment (`MEDIUM` - Recurring)' },

  // --- 📈 Analysis & Insights (NEXUS Lead) ---
  { id: 'TASK-HTA-01', title: 'Implement Historical File Lifespan Analysis', status: 'DONE', priority: 'HIGH', subsystem: 'NEXUS/KOIOS', phase: '2', details: '[DONE] [NEXUS/KOIOS][TASK-HTA-01] Implement Historical File Lifespan Analysis (Script, CSV, Report) (`HIGH`)' },
  { id: 'HTA-02', title: 'Automate Git History Analysis via CI/CD', status: 'DONE', priority: 'MEDIUM', subsystem: 'SPARC/HARMONY/KOIOS', phase: '2', details: '[DONE] [SPARC/HARMONY/KOIOS][HTA-02] Automate Git History Analysis via CI/CD (GitHub Actions) (`MEDIUM`) (Ref: Evolutionary Preservation)' },
  { id: 'HTA-DASH-01a', title: 'Select Visualization Tool for HTA Dashboard', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/KOIOS', phase: '2', details: '[Planned] [CORUJA/KOIOS][HTA-DASH-01a] Select Visualization Tool for HTA Dashboard (`MEDIUM`)' },
  { id: 'HTA-DASH-01b', title: 'Implement HTA Dashboard Integration', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/KOIOS', phase: '2', details: '[Planned] [CORUJA/KOIOS][HTA-DASH-01b] Implement HTA Dashboard Integration (`MEDIUM`) `depends_on: [HTA-DASH-01a]`' },
  { id: 'HTA-REFINE-01', title: 'Review and Refine HTA Script and Report', status: 'Planned', priority: 'LOW', subsystem: 'NEXUS/KOIOS', phase: '2', details: '[Planned] [NEXUS/KOIOS][HTA-REFINE-01] Review and Refine HTA Script and Report (Performance, Clarity, Artistry) (`LOW`)' },

  // --- 🛡️ Security & Compliance (ETHIK Lead) ---
  { id: 'SEC-AUDIT-01', title: 'Perform Periodic Security & License Audit', status: 'Planned', priority: 'HIGH', subsystem: 'ETHIK/HARMONY', phase: '2', details: '[Planned] [ETHIK/HARMONY][SEC-AUDIT-01] Perform Periodic Security & License Audit (incl. `pip-audit`, license checks, sensitive data review) (`HIGH` - Recurring)' },

  // --- ✨ Orchestration & CI/CD (SPARC Lead) ---
  { id: 'SPARC-CI-SETUP-01', title: 'Set Up Basic CI Pipeline (Lint, Format)', status: 'DONE', priority: 'CRITICAL', subsystem: 'SPARC/HARMONY/KOIOS', phase: '2', details: '[DONE] [SPARC/HARMONY/KOIOS][SPARC-CI-SETUP-01] Set Up Basic CI Pipeline (Lint, Format) (`CRITICAL`)' },
  { id: 'SPARC-CI-TEST-01', title: 'Integrate Unit/Integration Tests into CI', status: 'Planned', priority: 'HIGH', subsystem: 'SPARC/HARMONY/KOIOS', phase: '2', details: '[Planned] [SPARC/HARMONY/KOIOS][SPARC-CI-TEST-01] Integrate Unit/Integration Tests into CI (`HIGH`)' },
  { id: 'SPARC-CD-SETUP-01', title: 'Set Up Basic CD Pipeline (Staging/Prod)', status: 'Planned', priority: 'HIGH', subsystem: 'SPARC/HARMONY', phase: '2', details: '[Planned] [SPARC/HARMONY][SPARC-CD-SETUP-01] Set Up Basic CD Pipeline (Staging/Prod) (`HIGH`)' },
  { id: 'SPARC-MONITOR-01', title: 'Implement Basic Monitoring & Alerting', status: 'Planned', priority: 'MEDIUM', subsystem: 'SPARC/HARMONY', phase: '2', details: '[Planned] [SPARC/HARMONY][SPARC-MONITOR-01] Implement Basic Monitoring & Alerting (`MEDIUM`)' },

  // --- 💻 Environment & Compatibility (HARMONY Lead) ---
  { id: 'HARMONY-DEP-MGMT-01', title: 'Establish Dependency Management Strategy', status: 'DONE', priority: 'CRITICAL', subsystem: 'HARMONY/KOIOS', phase: '2', details: '[DONE] [HARMONY/KOIOS][HARMONY-DEP-MGMT-01] Establish Dependency Management Strategy (Poetry/pyproject.toml) (`CRITICAL`)' },
  { id: 'HARMONY-WIN-COMPAT-01', title: 'Ensure Core Functionality on Windows', status: 'DONE', priority: 'HIGH', subsystem: 'HARMONY', phase: '2', details: '[DONE] [HARMONY][HARMONY-WIN-COMPAT-01] Ensure Core Functionality on Windows (`HIGH`)' },
  { id: 'HARMONY-CONTAINER-01', title: 'Develop Dockerfile for Consistent Env', status: 'Planned', priority: 'MEDIUM', subsystem: 'HARMONY/SPARC', phase: '2', details: '[Planned] [HARMONY/SPARC][HARMONY-CONTAINER-01] Develop Dockerfile for Consistent Env (`MEDIUM`)' },

  // --- 🎨 UI & User Experience (CORUJA Lead) ---
  { id: 'CORUJA-UI-LIB-01', title: 'Select/Implement UI Component Library', status: 'DONE', priority: 'HIGH', subsystem: 'CORUJA/KOIOS', phase: '2', details: '[DONE] [CORUJA/KOIOS][CORUJA-UI-LIB-01] Select/Implement UI Component Library (Shadcn/UI) (`HIGH`)' },
  { id: 'CORUJA-DESIGN-SYS-01', title: 'Define Basic Design System & Style Guide', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/KOIOS', phase: '2', details: '[Planned] [CORUJA/KOIOS][CORUJA-DESIGN-SYS-01] Define Basic Design System & Style Guide (`MEDIUM`)' },
  { id: 'CORUJA-ACCESSIBILITY-01', title: 'Perform Accessibility Audit (WCAG)', status: 'Planned', priority: 'MEDIUM', subsystem: 'CORUJA/ETHIK', phase: '2', details: '[Planned] [CORUJA/ETHIK][CORUJA-ACCESSIBILITY-01] Perform Accessibility Audit (WCAG) (`MEDIUM`)' },
  { id: 'CORUJA-WEB-INIT-01', title: 'Initialize Website Project (Next.js)', status: 'DONE', priority: 'CRITICAL', subsystem: 'CORUJA/HARMONY', phase: '2', details: '[DONE] [CORUJA/HARMONY][CORUJA-WEB-INIT-01] Initialize Website Project (Next.js) (`CRITICAL`)' },
  { id: 'CORUJA-WEB-FOOTER-LINKS-01', title: 'Implement Comprehensive Footer Links', status: 'DONE', priority: 'HIGH', subsystem: 'CORUJA/KOIOS', phase: '2', details: '[DONE] [CORUJA/KOIOS][CORUJA-WEB-FOOTER-LINKS-01] Implement Comprehensive Footer Links (`HIGH`)' },
  { id: 'CORUJA-WEB-ROADMAP-01', title: 'Implement Interactive Roadmap Display', status: 'In Progress', priority: 'HIGH', subsystem: 'CORUJA/KOIOS', phase: '2', details: '[In Progress] [CORUJA/KOIOS][CORUJA-WEB-ROADMAP-01] Implement Interactive Roadmap Display (`HIGH`)', link: 'https://github.com/enioxt/egos/blob/main/website/src/components/Roadmap.tsx' },
  { id: 'CORUJA-WEB-CONTRIB-MODAL-01', title: 'Implement Contribution Modal/Guidance', status: 'In Progress', priority: 'HIGH', subsystem: 'CORUJA/KOIOS/AI', phase: '2', details: '[In Progress] [CORUJA/KOIOS/AI][CORUJA-WEB-CONTRIB-MODAL-01] Implement Contribution Modal/Guidance (`HIGH`)', link: 'https://github.com/enioxt/egos/blob/main/website/src/components/Roadmap.tsx#L113' },
  { id: 'CORUJA-WEB-LLM-API-01', title: 'Develop Backend API for LLM Interaction', status: 'Planned', priority: 'HIGH', subsystem: 'MYCELIUM/AI', phase: '3', details: '[Planned] [MYCELIUM/AI][CORUJA-WEB-LLM-API-01] Develop Backend API for LLM Interaction (`HIGH`)' },
  { id: 'CORUJA-WEB-LLM-UI-01', title: 'Integrate LLM Chat Interface into Modal', status: 'Planned', priority: 'HIGH', subsystem: 'CORUJA/AI', phase: '3', details: '[Planned] [CORUJA/AI][CORUJA-WEB-LLM-UI-01] Integrate LLM Chat Interface into Modal (`HIGH`) `depends_on: [CORUJA-WEB-LLM-API-01, CORUJA-WEB-CONTRIB-MODAL-01]`' },

  // --- 🕸️ Communication & APIs (MYCELIUM Lead) ---
  { id: 'MYCELIUM-API-DESIGN-01', title: 'Establish API Design Standards (Pydantic)', status: 'DONE', priority: 'HIGH', subsystem: 'MYCELIUM/KOIOS', phase: '2', details: '[DONE] [MYCELIUM/KOIOS][MYCELIUM-API-DESIGN-01] Establish API Design Standards (Pydantic) (`HIGH`)' },
  { id: 'MYCELIUM-INTER-SVC-COMM-01', title: 'Define Inter-Subsystem Communication Protocol', status: 'Planned', priority: 'MEDIUM', subsystem: 'MYCELIUM/SPARC', phase: '2', details: '[Planned] [MYCELIUM/SPARC][MYCELIUM-INTER-SVC-COMM-01] Define Inter-Subsystem Communication Protocol (`MEDIUM`)' },

  // --- ⏳ State & Persistence (CRONOS Lead) ---
  { id: 'CRONOS-DB-SELECT-01', title: 'Select Primary Database Technology', status: 'Planned', priority: 'HIGH', subsystem: 'CRONOS/HARMONY', phase: '2', details: '[Planned] [CRONOS/HARMONY][CRONOS-DB-SELECT-01] Select Primary Database Technology (`HIGH`)' },
  { id: 'CRONOS-ORM-SETUP-01', title: 'Set Up ORM (e.g., SQLAlchemy) & Migrations', status: 'Planned', priority: 'HIGH', subsystem: 'CRONOS/HARMONY', phase: '2', details: '[Planned] [CRONOS/HARMONY][CRONOS-ORM-SETUP-01] Set Up ORM & Migrations (`HIGH`) `depends_on: [CRONOS-DB-SELECT-01]`' },
  { id: 'CRONOS-BACKUP-STRAT-01', title: 'Define Backup and Recovery Strategy', status: 'Planned', priority: 'MEDIUM', subsystem: 'CRONOS/SPARC', phase: '2', details: '[Planned] [CRONOS/SPARC][CRONOS-BACKUP-STRAT-01] Define Backup and Recovery Strategy (`MEDIUM`)' },
];
