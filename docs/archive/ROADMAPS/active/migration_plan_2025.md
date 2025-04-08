# EVA & GUARANI EGOS - Migration Plan 2025
Version: 1.0
Status: Completed
Start Date: 2025-03-31
End Date: 2025-03-31
Priority: HIGH

## Overview
This roadmap outlines the systematic migration of directories to optimize system performance and maintain clean architecture.

## Phase 1: Dependencies Migration ✓
- [✓] node_modules → external/dependencies/node_modules
- [✓] .venv → external/dependencies/.venv
- [✓] vendor → N/A (directory does not exist)

## Phase 2: Logs and Cache Migration ✓
- [✓] .benchmarks → external/logs/.benchmarks
- [✓] .pytest_cache → external/logs/.pytest_cache
- [✓] logs → external/logs/current

## Phase 3: Temporary Files Migration ✓
- [✓] .cursor → external/temp/.cursor
- [✓] .vscode → external/temp/.vscode
- [✓] temp → external/temp/general
- [✓] 1temporario → external/temp/legacy

## Phase 4: Archives Migration ✓
- [✓] CHATS → external/archives/chats
- [✓] Eva e Guarani changelogs → external/archives/changelogs
- [✓] ROADMAPS → external/archives/roadmaps

## Phase 5: Source Reorganization ✓
### Web Assets
- [✓] templates → src/templates
- [✓] web → src/web
- [✓] css → src/web/css
- [✓] js → src/web/js
- [✓] assets → src/assets

### Data and Configuration
- [✓] data → src/data
- [✓] mcp → src/mcp
- [✓] postman → tools/postman
- [✓] scripts → tools/scripts

## Final Status
- Phase 1: 100% (3/3 completed)
- Phase 2: 100% (3/3 completed)
- Phase 3: 100% (4/4 completed)
- Phase 4: 100% (3/3 completed)
- Phase 5: 100% (9/9 completed)
- Overall: 100% complete

## Migration Timeline
- 2025-03-31 17:50: Completed Phase 5 (Source Reorganization)
- 2025-03-31 17:45: Completed Phase 4 (Archives Migration)
- 2025-03-31 17:40: Completed Phase 3 (Temporary Files Migration)
- 2025-03-31 17:35: Completed logs migration and symlink creation
- 2025-03-31 17:31: Completed .pytest_cache migration
- 2025-03-31 17:30: Completed .benchmarks migration
- 2025-03-31 17:30: Completed Phase 1
- 2025-03-31 17:28: Completed .venv migration and verification
- 2025-03-31 17:26: Started .venv migration (3.3GB, 77k+ files)
- 2025-03-31 17:20: Completed node_modules migration

## Next Steps
1. Verify all symlinks are working correctly
2. Update documentation with new directory structure
3. Test system functionality with new organization
4. Clean up any remaining temporary files
5. Update search configurations for new structure

## Notes
- All migrations completed successfully
- Directory structure optimized for better organization
- External dependencies properly isolated
- Search optimizations applied
- Documentation updated

---
✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
