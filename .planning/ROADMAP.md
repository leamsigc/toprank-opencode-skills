# Roadmap: Toprank Plugin Enhancement

## Phases

- [x] **Phase 1: opencode.ai Plugin Compatibility** - Create `.opencode/` directory structure and TypeScript plugin using `@opencode-ai/plugin` SDK (completed 2026-04-13)
- [x] **Phase 2: Chrome Remote Debug Authentication** - Implement CDP session reuse for authenticated Google APIs with fallback (completed 2026-04-13)
- [x] **Phase 3: chrome-devtools-cli Integration** - Add headless browser SEO analysis using CDP instead of WebFetch (completed 2026-04-13)
- [x] **Phase 4: chrome-devtools-mcp Integration** - Refactor SEO scripts to use @modelcontextprotocol/server-chrome-devtools MCP instead of CLI (completed 2026-04-13)
- [ ] **Phase 5: Convert Claude Code Plugin** - Convert existing .claude-plugin to opencode.ai native skills with full feature parity

---

## Phase Details

### Phase 1: opencode.ai Plugin Compatibility
**Goal**: Users can load and execute Toprank skills in opencode.ai environment
**Depends on**: Nothing (first phase)
**Requirements**: REQ-PC-01, REQ-PC-02, REQ-PC-03, REQ-PC-04, REQ-TEST-01, REQ-TEST-02
**Success Criteria** (what must be TRUE):
  1. User can install Toprank plugin in opencode.ai via plugin directory
  2. Skills are discovered and listed by opencode.ai plugin system
  3. MCP tools (`mcp__adsagent__*`) are available and callable
  4. Plugin does not get silently blocked (no "opencode-openai-codex-auth" pattern)
**Plans**: 01-01 (plugin structure), 01-02 (MCP + testing)
**UI hint**: yes

### Phase 2: Chrome Remote Debug Authentication
**Goal**: Users can authenticate to Google APIs via Chrome remote debug instead of API keys
**Depends on**: Phase 1
**Requirements**: REQ-CH-01, REQ-CH-02, REQ-CH-03, REQ-CH-04, REQ-CH-05, REQ-TEST-03
**Success Criteria** (what must be TRUE):
  1. User can connect to Chrome with `--remote-debugging-port=9222`
  2. Authenticated session persists across plugin tool invocations
  3. Fallback to environment variables works when Chrome unavailable
  4. Chrome 136+ with `--user-data-dir` works correctly
**Plans**: 2 plans (02-01, 02-02)

Plans:
- [x] 02-01-PLAN.md — Configure chrome-devtools-mcp and Chrome remote debug detection
- [x] 02-02-PLAN.md — Implement CDP session reuse and auth fallback

Plans:
- [x] 03-01-PLAN.md — chrome-devtools-cli Integration

### Phase 3: chrome-devtools-cli Integration
**Goal**: Users can perform SEO analysis using headless Chrome via CDP
**Depends on**: Phase 2
**Requirements**: REQ-SE-01, REQ-SE-02, REQ-SE-03
**Success Criteria** (what must be TRUE):
  1. SEO analysis runs in headless Chrome, rendering JavaScript
  2. SPA/SSR sites are detected and handled correctly
  3. Page audit captures full rendered HTML output
**Plans**: 1 plan (03-01)

### Phase 4: chrome-devtools-mcp Integration
**Goal**: Refactor SEO scripts to use @modelcontextprotocol/server-chrome-devtools MCP instead of CLI
**Depends on**: Phase 3
**Requirements**: REQ-SE-01, REQ-SE-02, REQ-SE-03
**Success Criteria** (what must be TRUE):
  1. SEO analysis uses MCP tools (navigate_page, take_snapshot, lighthouse_audit)
  2. SPA/SSR detection via MCP CDP calls
  3. Headless audit via MCP server (no CLI fallback required)
**Gap Closure**: Closes gaps from v1.0-MILESTONE-AUDIT.md - scripts used CLI instead of MCP
**Plans**: 1 plan (04-01)

Plans:
- [x] 04-01-PLAN.md — chrome-devtools-mcp Integration

### Phase 5: Convert Claude Code Plugin
**Goal**: Convert existing Claude Code plugin (`.claude-plugin/`) to opencode.ai native skills (`.opencode/`) with full feature parity
**Depends on**: Phase 1
**Requirements**: New requirements to be defined
**Success Criteria** (what must be TRUE):
  1. All 10 skills from .claude-plugin/plugin.json are available in opencode.ai
  2. Skills work identically in both Claude Code and opencode.ai environments
  3. MCP tool patterns replaced with native opencode.ai tool calling
  4. No feature loss compared to current implementation
**Plans**: To be planned

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|--------------|--------|-----------|
| 1. opencode.ai Plugin Compatibility | 2/2 | Complete    | 2026-04-13 |
| 2. Chrome Remote Debug Authentication | 2/2 | Complete    | 2026-04-13 |
| 3. chrome-devtools-cli Integration | 1/1 | Complete    | 2026-04-13 |
| 4. chrome-devtools-mcp Integration | 1/1 | Complete    | 2026-04-13 |
| 5. Convert Claude Code Plugin | 0/0 | In Progress | — |

---

## Coverage

| REQ-ID | Phase |
|--------|-------|
| REQ-PC-01 | 1 |
| REQ-PC-02 | 1 |
| REQ-PC-03 | 1 |
| REQ-PC-04 | 1 |
| REQ-CH-01 | 2 |
| REQ-CH-02 | 2 |
| REQ-CH-03 | 2 |
| REQ-CH-04 | 2 |
| REQ-CH-05 | 2 |
| REQ-SE-01 | 3, 4 |
| REQ-SE-02 | 3, 4 |
| REQ-SE-03 | 3, 4 |
| REQ-TEST-01 | 1 |
| REQ-TEST-02 | 1 |
| REQ-TEST-03 | 2 |

**Mapped: 15/15 ✓**
**Orphaned: 0**

---

*Roadmap created: 2026-04-13*