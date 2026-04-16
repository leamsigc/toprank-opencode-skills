# Phase 5: Converting Claude Code Plugin - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Convert the existing Toprank Claude Code plugin (`.claude-plugin/`) to work as a native skill in opencode.ai (`.opencode/`), maintaining full feature parity with the current implementation — all 10 skills must work identically in both environments.

</domain>

<decisions>
## Implementation Decisions

### Skill Parity
- **D-01:** ALL 10 existing skills from `.claude-plugin/plugin.json` must be converted to work in opencode.ai:
  - ads, ads-audit, ads-copy
  - seo-analysis, seo-page, content-writer, keyword-research, meta-tags-optimizer, schema-markup-generator, setup-cms
  - gemini, toprank-upgrade-skill

### Skill Format
- **D-02:** Skills will be defined as TypeScript definitions in `.opencode/plugin.ts` with the skills array containing name, path, and triggers
- **D-03:** Keep existing SKILL.md files in their current locations; convert them to plugin.ts references rather than converting format
- **D-04:** Each skill needs a `Skill` object in plugin.ts with:
  - `name`: unique skill identifier
  - `path`: path to skill directory (e.g., `./skills/ads`)
  - `triggers`: array of trigger phrases

### Directory Structure
- **D-05:** Maintain dual-format coexistence — both `.claude-plugin/` (for Claude Code) and `.opencode/` (for opencode.ai) directories remain
- **D-06:** Claude Code uses `.claude-plugin/plugin.json` format; opencode.ai uses `.opencode/plugin.ts` format
- **D-07:** Skills are physically located in root directories (e.g., `google-ads/ads/SKILL.md`) but referenced from both plugin manifests

### MCP Integration
- **D-08:** Use opencode.ai's native tool calling directly instead of MCP layer
- **D-09:** Replace `mcp__adsagent__*` tool patterns with opencode.ai native tool invocation
- **D-10:** Skills call tools directly via opencode.ai's tool system rather than through MCP server wrapper (npx)
- **D-11:** Fallback to direct API calls if native tool calling fails

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Implementation
- `.claude-plugin/plugin.json` — Current skill registry (10 skills)
- `.opencode/plugin.ts` — Current opencode.ai plugin skeleton (only 2 skills)
- `.opencode/config.json` — opencode.ai configuration

### Skill Definitions
- `google-ads/ads/SKILL.md` — Core ads skill (reference for conversion pattern)
- `seo/seo-analysis/SKILL.md` — SEO analysis skill (reference for conversion pattern)

### Architecture
- `.planning/codebase/ARCHITECTURE.md` — Plugin architecture overview

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.opencode/plugin.ts` — Existing skeleton with skill definition pattern
- `.opencode/skills/index.ts` — Skills index file
- SKILL.md files exist in 12 locations, each with frontmatter and structured content

### Established Patterns
- Plugin defines skills as array of objects with name/path/triggers
- Skills directory structure: `{category}/{skill}/SKILL.md`
- MCP tool calls use `mcp__server__tool` naming pattern (to be replaced)

### Integration Points
- Skills use MCP preamble for setup (`../shared/preamble.md`)
- Skills reference each other via `/toprank:skill-name` triggers
- Chrome DevTools MCP integrated for SEO (Phase 4)

</code_context>

<specifics>
## Specific Ideas

- All 10 skills from `.claude-plugin/plugin.json` must have corresponding entries in `.opencode/plugin.ts`
- The current `.opencode/plugin.ts` only has 2 skills (ads, seo-analysis) — this is incomplete
- Need to research opencode.ai's native tool calling API vs MCP approach
- The tool calling pattern change (`mcp__adsagent__*` → native) affects all Google Ads skills

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-converting-claude-code-plugin*
*Context gathered: 2026-04-16*
