# Project Research Summary

**Project:** Toprank Plugin Enhancement
**Domain:** Claude Code Plugin Enhancement (opencode.ai compatibility, Chrome DevTools integration, remote debug authentication)
**Researched:** 2026-04-13
**Confidence:** MEDIUM

## Executive Summary

Toprank plugin requires strategic adaptation for three new capabilities: opencode.ai plugin compatibility, chrome-devtools-cli integration, and Chrome remote debug authentication. The existing Claude Code plugin architecture provides a strong foundation, but requires migrating from JSON-based plugin manifests to TypeScript SDK-based plugins for opencode.ai compatibility. Research confirms that opencode.ai uses a fundamentally different extensibility model — JavaScript/TypeScript plugins via `@opencode-ai/plugin` SDK rather than Claude Code's JSON `plugin.json` format.

The recommended approach is a dual-format strategy: maintain existing `.claude-plugin/` for Claude Code while adding `.opencode/` directory with TypeScript plugins for opencode.ai. Chrome remote debugging replaces API key authentication using CDP session reuse, which eliminates manual API key management but introduces new pitfalls around Chrome 136+ security changes requiring `--user-data-dir`. The chrome-devtools-mcp MCP server provides CLI-level integration for SEO analysis of JavaScript-heavy sites that WebFetch cannot render.

Key risks include silent plugin blocking due to hardcoded substring matching in opencode.ai, ESM module resolution failures, Chrome permission dialogs blocking automation, and MCP connection churn in long-running sessions. These are all addressable with the mitigation strategies identified in PITFALLS.md.

## Key Findings

### Recommended Stack

**Core technologies:**
- `@opencode-ai/plugin` — Plugin SDK for opencode.ai compatibility; defines `Plugin` type, `tool()` helper, event hooks
- `chrome-devtools-mcp` — Google's official Chrome DevTools MCP server (33K+ stars); provides both MCP tools and CLI interface
- `websockets` ^14.0 — Raw CDP WebSocket connection for Chrome remote debug auth; ~100KB vs 50MB for Playwright
- `rookiepy` — Browser cookie extraction without CDP; cross-browser (Chrome, Firefox, Edge)
- `zod` ^3.23 — Schema validation required by `@opencode-ai/plugin` tool schema

**Critical version requirements:**
- Chrome must use `--user-data-dir` alongside `--remote-debugging-port` (Chrome 136+ security change)
- chrome-devtools-mcp requires Node.js v20.19+ — use absolute paths, not npx, in MCP config

### Expected Features

**Must have (table stakes):**
- **opencode.ai plugin adapter** — TypeScript plugin using `@opencode-ai/plugin` SDK with Zod schema
- **Chrome remote debug auto-connect** — CDP session reuse replacing API key authentication
- **chrome-devtools-cli integration** — Headless browser SEO analysis for JavaScript-heavy sites
- **MCP tool naming compatibility** — Verify `mcp__adsagent__*` format works in opencode.ai

**Should have (competitive):**
- **OAuth via CDP session** — No manual API key management; inherits user's authenticated state
- **Chrome auto-reconnect** — Resilient connection handling after Chrome restarts
- **Performance tracing** — Core Web Vitals via CDP without PageSpeed API quotas

**Defer (v2+):**
- **Network request analysis** — Low priority vs implementation effort
- **Multi-account support** — Explicitly out of scope per CONCERNS.md

### Architecture Approach

Toprank uses a three-layer architecture: (1) Skill Layer for individual workflows unchanged from current implementation, (2) Plugin Infrastructure that migrates from Claude Code's `.claude-plugin/plugin.json` to opencode.ai's `.opencode/skills/*/SKILL.md` with YAML frontmatter, (3) MCP Integration layer enhanced with chrome-devtools-mcp for CDP-based SEO analysis.

**Major components:**
1. **Skill Layer** — Individual skill workflows in `*/<skill-name>/SKILL.md`; self-contained with references/, scripts/, evals/
2. **Plugin Infrastructure** — Skill discovery, MCP configuration; converts JSON manifests to YAML frontmatter for opencode.ai
3. **MCP Integration** — chrome-devtools-mcp + AdsAgent MCP; graceful degradation to env vars when MCP unavailable

### Critical Pitfalls

1. **opencode.ai hardcoded plugin skip block** — Plugin names containing "opencode-openai-codex-auth" substring get silently blocked; avoid this pattern entirely
2. **ESM import .js extension missing** — Published npm packages lack `.js` extensions; use `file://` paths or local plugin development
3. **Chrome --user-data-dir requirement** — Chrome 136+ ignores `--remote-debugging-port` without dedicated profile; always use both flags
4. **Chrome permission dialog on every connection** — `--autoConnect` triggers repeated approval prompts; use `--browserUrl` to persistent Chrome instead
5. **MCP session connection churn** — MCP server restarts cause Chrome reconnection; use fixed `--browserUrl` connection for stability

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: opencode.ai Plugin Compatibility
**Rationale:** Foundational — all other phases depend on plugin loading correctly in opencode.ai
**Delivers:** TypeScript plugin using `@opencode-ai/plugin` SDK, converted skill SKILL.md files with YAML frontmatter
**Addresses:** Features 1, 4 from FEATURES.md (opencode.ai adapter, MCP tool naming)
**Avoids:** Pitfall 1 (plugin skip block), Pitfall 2 (ESM import), Pitfall 3 (MCP tool naming)

### Phase 2: Chrome Remote Debug Authentication
**Rationale:** Required before chrome-devtools integration can use authenticated sessions
**Delivers:** CDP detection script, modified preamble.md with auth fallback logic, connection state management
**Addresses:** Feature 2 from FEATURES.md (Chrome remote debug)
**Avoids:** Pitfall 4 (--user-data-dir requirement), Pitfall 5 (permission dialog)

### Phase 3: chrome-devtools-cli Integration
**Rationale:** Builds on Phase 2 auth layer for CDP-based SEO analysis
**Delivers:** CDP-based SEO scripts, headless browser page fetch + HTML extraction, visual screenshots
**Addresses:** Feature 3 from FEATURES.md (basic chrome-devtools integration)
**Avoids:** Pitfall 6 (connection churn), Pitfall 7 (Node.js version), Pitfall 8 (Target closed)

### Phase 4: Advanced Features
**Rationale:** Optional enhancements build on proven infrastructure
**Delivers:** OAuth via CDP session, performance tracing, visual regression baseline
**Addresses:** Features 5, 6, 7, 8 from FEATURES.md

### Phase Ordering Rationale

- Phase 1 first because no other work matters if plugin doesn't load in opencode.ai
- Phase 2 before 3 because chrome-devtools needs CDP access for authenticated requests
- Phase 3 before 4 because differentiators depend on CDP infrastructure
- Dependencies flow: Feature 1 → Feature 4, Feature 2 → Feature 6/5/3, Feature 3 → Features 7/8/9

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Chrome remote debug auth — connection reliability varies by Chrome version; Chrome 144/146 behavior differences unclear
- **Phase 4:** OAuth via CDP — some Google APIs may still need service account; needs validation

Phases with standard patterns (skip research-phase):
- **Phase 3:** chrome-devtools basic — CDP comprehensive, well-documented; skill integration is new but MCP is standard

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Official SDK docs for opencode.ai + chrome-devtools-mcp; npm package version requirements need validation |
| Features | MEDIUM | Official SDK documentation HIGH for requirements; implementation patterns MEDIUM |
| Architecture | MEDIUM | Docs confirm skill/plugin model; no direct plugin.json migration guide |
| Pitfalls | HIGH | Concrete issues with fixes documented; Chrome security changes well-documented |

**Overall confidence:** MEDIUM

### Gaps to Address

- **opencode.ai skill permission system** — Requires testing; docs don't cover migration from Claude Code
- **MCP vs CDP performance comparison** — For SEO rendering, theoretical advantage understood but not benchmarked
- **Chrome remote debug cross-platform** — Research focused on Linux; Windows/macOS behavior may differ

## Sources

### Primary (HIGH confidence)
- opencode.ai plugins documentation: https://opencode.ai/docs/plugins
- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp
- opencode.ai config schema: https://opencode.ai/docs/config

### Secondary (MEDIUM confidence)
- CDP authentication patterns: https://developer.chrome.com/docs/devtools/protocol-monitor
- Chrome auto-connect: Scalified blog (2026-02-23)

### Tertiary (LOW confidence)
- Visual regression pattern: Proposed feature, no existing pattern validated
- Auto-reconnect handling: Standard error handling theory, needs implementation validation

---

*Research completed: 2026-04-13*
*Ready for roadmap: yes*