# Architecture

**Analysis Date:** 2026-04-13

## Pattern Overview

**Overall:** Claude Code Plugin with Skill-Based Architecture

Toprank is a Claude Code plugin that provides SEO and Google Ads management capabilities through a collection of independent skills. Each skill is a self-contained folder with a `SKILL.md` file (the skill entry point), optional `scripts/` for Python automation, and optional `references/` for domain knowledge.

**Key Characteristics:**
- Skills are namespaced under `/toprank:*` commands (e.g., `/toprank:ads`, `/toprank:seo-analysis`)
- Each skill is independently loadable and reusable
- Shared logic lives in category-level `shared/` directories
- MCP server integration for external APIs (Google Ads via AdsAgent, CMS APIs, PageSpeed)
- Script-based execution (Python 3.8+ stdlib + optional requests)

## Layers

**Plugin Infrastructure:**
- Purpose: Provides plugin metadata, MCP server configuration, and CLI entry points
- Location: `.claude-plugin/` and `.mcp.json`
- Contains: `plugin.json` (skill registry), `marketplace.json` (registry metadata), MCP server definitions
- Depends on: Claude Code core, MCP protocol
- Used by: Claude Code runtime

**Skill Layer:**
- Purpose: Individual skills that handle specific user workflows
- Location: `google-ads/*/`, `seo/*/`, root-level skills
- Contains: `SKILL.md` (skill definition with triggers, tools, steps), `scripts/` (Python executables), `references/` (knowledge docs), `evals/` (test cases)
- Depends on: Plugin infrastructure, shared preambles, MCP tools
- Used by: Claude Code when user invokes `/toprank:skill-name`

**Shared Layer:**
- Purpose: Common logic used across multiple skills in a category
- Location: `google-ads/shared/`, `seo/shared/`
- Contains: `preamble.md` (bootstrapping logic), `gaql-cookbook.md` (query patterns), business context handlers
- Depends on: Plugin infrastructure
- Used by: All skills in the category

**Script Layer:**
- Purpose: Python automation for data collection, API calls, and processing
- Location: `*/scripts/*.py`
- Contains: GSC analysis, URL inspection, PageSpeed analysis, CMS content fetchers
- Depends on: Python 3.8+, optional `requests` library
- Used by: Skills execute scripts via Bash tool

**Data Layer:**
- Purpose: Persistent storage for business context, personas, audit logs, and configuration
- Location: `~/.toprank/` (user home), `.adsagent/` (project-local)
- Contains: `config.yaml`, `business-context/`, `personas/`, audit logs
- Depends on: User filesystem
- Used by: Skills for stateful operations

## Data Flow

**Skill Invocation Flow:**

1. User invokes `/toprank:skill-name` in Claude Code
2. Claude Code loads the skill's `SKILL.md` from the plugin directory
3. Skill reads category-level `shared/preamble.md` for bootstrapping
4. Shared preamble performs:
   - Update check (calls `bin/toprank-update-check`)
   - API key verification (reads `~/.claude/settings.json`)
   - Config resolution (merges project + global config)
   - MCP server detection (calls MCP tool to verify availability)
   - Onboarding if needed (account selection)
5. Skill executes its workflow, reading from `references/` as needed
6. Skills call MCP tools (`mcp__adsagent__*`) or execute scripts (`$SKILL_SCRIPTS/*.py`)
7. Results streamed back to user

**External API Integration Flow:**

1. **Google Ads:** Skills use AdsAgent MCP (`mcp__adsagent__*` tools) via HTTP transport
2. **Search Console:** Scripts use gcloud CLI + Search Console API directly
3. **CMS:** Scripts make direct API calls (WordPress REST, Strapi REST, Contentful, Ghost)
4. **PageSpeed:** Scripts call PageSpeed Insights API

**State Persistence Flow:**

1. Skills write business context to `~/.toprank/business-context/<domain>.json`
2. Personas stored at `~/.toprank/personas/<domain>.json`
3. Audit logs at `~/.toprank/audit-log/<domain>.json`
4. Account baselines at `{data_dir}/account-baseline.json`

## Key Abstractions

**Skill:**
- Purpose: Represents a discrete capability users can invoke
- Examples: `google-ads/ads/`, `seo/seo-analysis/`, `gemini/`
- Pattern: Folder with `SKILL.md` (required), `scripts/` (optional), `references/` (optional)

**Preamble:**
- Purpose: Bootstrapping logic shared across a category's skills
- Examples: `google-ads/shared/preamble.md`, `seo/shared/preamble.md`
- Pattern: Markdown file with step-by-step initialization instructions

**Script:**
- Purpose: Executable Python for data collection and API interaction
- Examples: `seo/seo-analysis/scripts/analyze_gsc.py`, `seo/seo-analysis/scripts/pagespeed.py`
- Pattern: Python 3.8+ with `--output` flag for file output, stderr for progress, stdout for data

**Reference Document:**
- Purpose: Domain knowledge and decision frameworks
- Examples: `google-ads/ads/references/analysis-heuristics.md`, `google-ads/shared/gaql-cookbook.md`
- Pattern: Markdown with tables, thresholds, and playbook steps

**MCP Tool Category:**
- Purpose: Abstracts external API providers
- Pattern: Placeholder prefixes (`~~google-ads`, `~~search-console`, `~~cms`) with default servers and alternatives

## Entry Points

**User Invocation:**
- Location: Claude Code command input
- Triggers: `/toprank:skill-name` or skill trigger keywords
- Responsibilities: Route user intent to the correct skill, pass execution context

**Plugin Loading:**
- Location: `.claude-plugin/plugin.json`
- Triggers: Claude Code startup or `/plugin install`
- Responsibilities: Declare available skills, version, marketplace metadata

**MCP Server:**
- Location: `.mcp.json`
- Triggers: Claude Code startup
- Responsibilities: Auto-configure external MCP servers (AdsAgent)

**CLI Tools:**
- Location: `bin/toprank-config`, `bin/toprank-update-check`
- Triggers: Skills call these directly via Bash
- Responsibilities: Read/write config, check for updates

## Error Handling

**Strategy:** Graceful degradation with user-facing guidance

**Patterns:**
- MCP unavailable: Block and prompt for restart/fix
- API key missing: Block and prompt for signup
- Script failure: Show stderr error, suggest fix
- Missing GSC access: Skip to technical-only audit
- Missing CMS config: Skip CMS phase silently

## Cross-Cutting Concerns

**Logging:** Scripts write to stderr for progress, stdout for data (pipe-friendly)

**Configuration:**
- `~/.toprank/config.yaml` via `bin/toprank-config`
- Project-level `.adsagent.json` for per-project account
- `~/.claude/settings.json` for API keys (env vars)

**Authentication:**
- Google Ads: API key in env var (AdsAgent MCP reads from environment)
- Search Console: gcloud OAuth (cached via Application Default Credentials)
- CMS: Direct API authentication per CMS type

---

*Architecture analysis: 2026-04-13*