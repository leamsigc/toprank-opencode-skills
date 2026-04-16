# Phase 5: Converting Claude Code Plugin - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-16
**Phase:** 05-converting-claude-code-plugin
**Areas discussed:** Skill parity, Skill format, Directory structure, MCP integration

---

## Skill Parity

| Option | Description | Selected |
|--------|-------------|----------|
| All 10 skills | Move all 10 skills (ads, ads-audit, ads-copy, seo-analysis, content-writer, keyword-research, meta-tags-optimizer, schema-markup-generator, setup-cms, gemini) to opencode.ai plugin, ensuring full feature parity | ✓ |
| Core skills only | Only move the core 2 skills shown in current plugin.ts (ads, seo-analysis) to start | |
| Hybrid approach | Keep skills in Claude Code format but load them dynamically via opencode.ai plugin system | |

**User's choice:** All 10 skills
**Notes:** User explicitly stated "without losing any feature of the current implementation (required)" in the original context - full feature parity is non-negotiable

---

## Skill Format

| Option | Description | Selected |
|--------|-------------|----------|
| plugin.ts definitions | Convert all SKILL.md files to TypeScript definitions in plugin.ts (skills array with name, path, triggers) | ✓ |
| Direct SKILL.md reference | Keep SKILL.md files as-is, configure plugin.ts to reference them directly | |
| Use native format | Use opencode.ai's native skill format if different from SKILL.md | |

**User's choice:** plugin.ts definitions
**Notes:** Prepends to existing `.opencode/plugin.ts` structure which already shows the pattern

---

## Directory Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Dual format coexistence | Keep both .claude-plugin/ and .opencode/ directories - Claude Code uses one, opencode.ai uses the other | ✓ |
| Migrate to .opencode/ | Migrate entirely to .opencode/ format and deprecate .claude-plugin/ | |
| Single unified directory | Consolidate into a single directory that works for both platforms | |

**User's choice:** Dual format coexistence
**Notes:** Both platforms have different formats - maintain both for now

---

## MCP Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Wrap MCP server | Wrap AdsAgent MCP server for opencode.ai using npx, keep same mcp__adsagent__ tool naming pattern | |
| Direct tool calling | Use opencode.ai's native tool calling directly without MCP layer | ✓ |
| Hybrid MCP + direct | Support both - MCP tools when available, direct API as fallback | |

**User's choice:** Direct tool calling
**Notes:** User chose "Direct tool calling" - this is a significant architectural change from current `mcp__adsagent__*` pattern

---

## Deferred Ideas

No deferred ideas captured - all questions were within phase scope
