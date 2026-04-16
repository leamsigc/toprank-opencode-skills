# Project: Toprank Plugin Enhancement

## What This Is

Enhance Toprank (Claude Code SEO + Google Ads plugin) to:
1. Become compatible with opencode.ai as a plugin
2. Replace API key authentication with Chrome remote debug mode auto-connect
3. Integrate chrome-devtools-cli for enhanced SEO analysis capabilities

## Core Value

Make Toprank work seamlessly in opencode.ai while leveraging Chrome DevTools Protocol for better SEO auditing (JavaScript rendering, visual analysis) instead of relying on heavy external APIs (gcloud, AdsAgent MCP).

## Context

**Existing codebase:** Toprank v0.11.3 is a Claude Code plugin with:
- 10 skills (SEO analysis, content writer, Google Ads management, etc.)
- MCP integration via AdsAgent for Google Ads
- gcloud CLI dependency for Google Search Console
- Environment variable-based API key management

**Key constraints from codebase analysis:**
- Current `.claude-plugin/plugin.json` format may need adjustment for opencode.ai
- MCP tool naming uses `mcp__adsagent__*` pattern (may not work in opencode.ai)
- Skills use `~~category` placeholder pattern for tool-agnostic execution

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| opencode.ai plugin compatibility | Test and adapt plugin.json format | — Pending |
| Chrome remote debug for API auth | Replace env vars with CDP auto-connect | — Pending |
| chrome-devtools-cli integration | Add headless browser SEO analysis | — Pending |
| Keep MCP as primary (with fallback) | Preserve existing AdsAgent integration | — Pending |

---

## Requirements

### Validated

- ✓ Toprank skills execute in Claude Code — existing
- ✓ Google Ads via AdsAgent MCP — existing
- ✓ SEO analysis via gcloud + WebFetch — existing
- ✓ SKILL.md format with frontmatter — existing

### Active

- [ ] Opencode.ai plugin compatibility — test and adapt
- [ ] Chrome remote debug auto-connect for authentication
- [ ] chrome-devtools-cli integration for SEO analysis
- [ ] Fallback from MCP to direct API when unavailable
- [ ] Remove gcloud dependency via Chrome-based GSC access

### Out of Scope

- [Full rewrite of skill system] — maintain current structure
- [Add new SEO features beyond chrome-devtools integration] — defer to future phase
- [Multi-account support] — not priority for this project

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

*Last updated: 2026-04-13 after project initialization*