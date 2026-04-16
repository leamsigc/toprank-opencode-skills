<!-- GSD:project-start source:PROJECT.md -->
## Project

**Project: Toprank Plugin Enhancement**

Enhance Toprank (Claude Code SEO + Google Ads plugin) to:
1. Become compatible with opencode.ai as a plugin
2. Replace API key authentication with Chrome remote debug mode auto-connect
3. Integrate chrome-devtools-cli for enhanced SEO analysis capabilities

**Core Value:** Make Toprank work seamlessly in opencode.ai while leveraging Chrome DevTools Protocol for better SEO auditing (JavaScript rendering, visual analysis) instead of relying on heavy external APIs (gcloud, AdsAgent MCP).
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.8+ - All SEO scripts and CMS connectors use Python stdlib + requests
- Markdown (SKILL.md) - Claude Code skill definitions
- Shell (Bash) - Helper scripts and CLI wrappers
- JSON - Configuration files (.mcp.json, plugin.json, settings)
## Runtime
- Claude Code plugin runtime - Skills execute within Claude Code context
- Python 3.8+ (for local scripts) - User's local environment runs CMS fetch/analyze scripts
- pip (for local dependencies)
- npm (for MCP server wrapper via npx)
## Frameworks
- Claude Code plugin system - Skill-based plugin architecture
- MCP (Model Context Protocol) - Server for Google Ads API via AdsAgent
- pytest - Unit tests in `test/unit/`
- LLM-judge eval system - Custom eval framework in `test/helpers/`
- npx/mcp-remote - HTTP transport wrapper for MCP server
## Key Dependencies
- `google-auth>=2.0.0` - Authentication for Google Search Console API
- `google-auth-httplib2>=0.2.0` - HTTP transport for Google auth
- `requests>=2.28.0` - HTTP requests for CMS API calls
- All CMS connectors (WordPress, Strapi, Contentful, Ghost) use Python stdlib only
- No pip packages required for seo-analysis scripts
## Configuration
- `~/.claude/settings.json` - Plugin configuration including `env.ADSAGENT_API_KEY`
- `.env` or `.env.local` files - CMS credentials (WP_URL, STRAPI_URL, CONTENTFUL_SPACE_ID, GHOST_URL)
- `.adsagent.json` - Project-level Google Ads account configuration
- `~/.adsagent/config.json` - Global Google Ads account configuration
- `.claude-plugin/plugin.json` - Plugin manifest defining all skills
- `.mcp.json` - MCP server configuration for AdsAgent
## Platform Requirements
- Claude Code installed
- Python 3.8+ (for running SEO scripts locally)
- Google Cloud SDK + gcloud CLI (for Search Console API)
- Optional: Gemini CLI (for gemini skill cross-model review)
- Claude Code plugin runtime
- AdsAgent API key (free at adsagent.org)
- Google Cloud project with Search Console API enabled (for SEO features)
- CMS credentials for connected systems (WordPress/Strapi/Contentful/Ghost)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## SKILL.md Frontmatter Format
- `version: <semver>` - For skills with versioning
- `triggers:` - List of phrases that activate the skill
## Python Script Standards
#!/usr/bin/env python3
- Use Python stdlib only — no `pip install` dependencies
- Always include `--output` flag for file output
- Print JSON to stdout by default
- Include usage examples in docstring
- Exit with error codes: `sys.exit(1)` on failure
## Reference Document Structure
- `references/account-health-scoring.md` — Diagnostic thresholds and benchmarks
- `references/session-checks.md` — Change review procedures
- Use descriptive names: `session-checks.md`, `bid-strategy-decision-tree.md`
- Use `framework` suffix for methodology docs
- Use `guide` or `reference` suffix for how-to docs
## Commit Message Style
## [0.11.3] — 2026-04-12
### Added
- **Change impact review mode** — Users can now say "check my changes"
### Changed
- **Deduped headline formulas** — Extracted to reference file
### Fixed
- **Session-checks query logic** — Fixed maturation status branching
- Use semantic versioning
- Category order: Added, Changed, Fixed, Removed, Deprecated
- Use past tense for changes
- Be specific about what changed and why
## File Naming
- SKILL.md - Main skill definition (uppercase, no spaces)
- `references/*.md` - Reference documentation
- `scripts/*.py` - Helper scripts
- `test/unit/test_*.py` - Unit tests
- `test/helpers/*.py` - Test utilities
- `evals/evals.json` - Skill eval prompts
## Directory Structure
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Skills are namespaced under `/toprank:*` commands (e.g., `/toprank:ads`, `/toprank:seo-analysis`)
- Each skill is independently loadable and reusable
- Shared logic lives in category-level `shared/` directories
- MCP server integration for external APIs (Google Ads via AdsAgent, CMS APIs, PageSpeed)
- Script-based execution (Python 3.8+ stdlib + optional requests)
## Layers
- Purpose: Provides plugin metadata, MCP server configuration, and CLI entry points
- Location: `.claude-plugin/` and `.mcp.json`
- Contains: `plugin.json` (skill registry), `marketplace.json` (registry metadata), MCP server definitions
- Depends on: Claude Code core, MCP protocol
- Used by: Claude Code runtime
- Purpose: Individual skills that handle specific user workflows
- Location: `google-ads/*/`, `seo/*/`, root-level skills
- Contains: `SKILL.md` (skill definition with triggers, tools, steps), `scripts/` (Python executables), `references/` (knowledge docs), `evals/` (test cases)
- Depends on: Plugin infrastructure, shared preambles, MCP tools
- Used by: Claude Code when user invokes `/toprank:skill-name`
- Purpose: Common logic used across multiple skills in a category
- Location: `google-ads/shared/`, `seo/shared/`
- Contains: `preamble.md` (bootstrapping logic), `gaql-cookbook.md` (query patterns), business context handlers
- Depends on: Plugin infrastructure
- Used by: All skills in the category
- Purpose: Python automation for data collection, API calls, and processing
- Location: `*/scripts/*.py`
- Contains: GSC analysis, URL inspection, PageSpeed analysis, CMS content fetchers
- Depends on: Python 3.8+, optional `requests` library
- Used by: Skills execute scripts via Bash tool
- Purpose: Persistent storage for business context, personas, audit logs, and configuration
- Location: `~/.toprank/` (user home), `.adsagent/` (project-local)
- Contains: `config.yaml`, `business-context/`, `personas/`, audit logs
- Depends on: User filesystem
- Used by: Skills for stateful operations
## Data Flow
## Key Abstractions
- Purpose: Represents a discrete capability users can invoke
- Examples: `google-ads/ads/`, `seo/seo-analysis/`, `gemini/`
- Pattern: Folder with `SKILL.md` (required), `scripts/` (optional), `references/` (optional)
- Purpose: Bootstrapping logic shared across a category's skills
- Examples: `google-ads/shared/preamble.md`, `seo/shared/preamble.md`
- Pattern: Markdown file with step-by-step initialization instructions
- Purpose: Executable Python for data collection and API interaction
- Examples: `seo/seo-analysis/scripts/analyze_gsc.py`, `seo/seo-analysis/scripts/pagespeed.py`
- Pattern: Python 3.8+ with `--output` flag for file output, stderr for progress, stdout for data
- Purpose: Domain knowledge and decision frameworks
- Examples: `google-ads/ads/references/analysis-heuristics.md`, `google-ads/shared/gaql-cookbook.md`
- Pattern: Markdown with tables, thresholds, and playbook steps
- Purpose: Abstracts external API providers
- Pattern: Placeholder prefixes (`~~google-ads`, `~~search-console`, `~~cms`) with default servers and alternatives
## Entry Points
- Location: Claude Code command input
- Triggers: `/toprank:skill-name` or skill trigger keywords
- Responsibilities: Route user intent to the correct skill, pass execution context
- Location: `.claude-plugin/plugin.json`
- Triggers: Claude Code startup or `/plugin install`
- Responsibilities: Declare available skills, version, marketplace metadata
- Location: `.mcp.json`
- Triggers: Claude Code startup
- Responsibilities: Auto-configure external MCP servers (AdsAgent)
- Location: `bin/toprank-config`, `bin/toprank-update-check`
- Triggers: Skills call these directly via Bash
- Responsibilities: Read/write config, check for updates
## Error Handling
- MCP unavailable: Block and prompt for restart/fix
- API key missing: Block and prompt for signup
- Script failure: Show stderr error, suggest fix
- Missing GSC access: Skip to technical-only audit
- Missing CMS config: Skip CMS phase silently
## Cross-Cutting Concerns
- `~/.toprank/config.yaml` via `bin/toprank-config`
- Project-level `.adsagent.json` for per-project account
- `~/.claude/settings.json` for API keys (env vars)
- Google Ads: API key in env var (AdsAgent MCP reads from environment)
- Search Console: gcloud OAuth (cached via Application Default Credentials)
- CMS: Direct API authentication per CMS type
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
