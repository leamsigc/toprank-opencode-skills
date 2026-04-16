# Codebase Structure

**Analysis Date:** 2026-04-16

## Directory Layout

```
toprank/
├── .claude-plugin/              # Plugin metadata
│   ├── plugin.json              # Skill registry (explicit paths)
│   └── marketplace.json          # Registry entry
├── .mcp.json                    # MCP server config (AdsAgent, Chrome DevTools)
├── bin/                         # CLI tools
│   ├── toprank-config           # Config read/write (bash)
│   ├── toprank-update-check    # Update checker (bash)
│   ├── chrome-detect.sh        # Chrome detection
│   ├── chrome-launch.sh        # Chrome launcher
│   ├── chrome-session.sh       # Chrome session manager
│   └── auth-fallback.sh       # Auth fallback handler
├── google-ads/                  # Google Ads skills
│   ├── shared/                  # Shared logic (all ads skills)
│   │   ├── preamble.md         # Bootstrapping logic
│   │   ├── gaql-cookbook.md    # Query patterns
│   │   └── policy-registry.json
│   ├── ads/                     # Campaign management skill
│   │   ├── SKILL.md
│   │   ├── references/         # Domain knowledge
│   │   │   ├── analysis-heuristics.md
│   │   │   ├── campaign-structure-guide.md
│   │   │   ├── session-checks.md
│   │   │   └── bid-strategy-decision-tree.md
│   │   └── evals/              # Test cases
│   ├── ads-audit/              # Account audit skill
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── account-health-scoring.md
│   │   │   ├── persona-discovery.md
│   │   │   └── business-context.md
│   │   └── evals/
│   └── ads-copy/               # RSA copy generator skill
├── seo/                        # SEO skills
│   ├── shared/                  # Shared logic (all SEO skills)
│   │   ├── preamble.md        # Bootstrapping logic
│   │   └── business-context.md
│   ├── seo-analysis/           # Full audit skill
│   │   ├── SKILL.md            # Main skill file
│   │   ├── scripts/            # Python executables
│   │   │   ├── analyze_gsc.py   # GSC data collection
│   │   │   ├── url_inspection.py  # URL Inspection API
│   │   │   ├── pagespeed.py    # PageSpeed API
│   │   │   ├── cms_detect.py   # CMS detection
│   │   │   ├── detect_js.py    # JavaScript detection
│   │   │   ├── chrome_audit.py  # Chrome DevTools audit
│   │   │   ├── list_gsc_sites.py
│   │   │   ├── show_gsc.py
│   │   │   ├── show_pagespeed.py
│   │   │   ├── preflight.py     # GSC preflight check
│   │   │   ├── preflight_wordpress.py
│   │   │   ├── preflight_strapi.py
│   │   │   ├── preflight_contentful.py
│   │   │   ├── preflight_ghost.py
│   │   │   ├── fetch_wordpress_content.py
│   │   │   ├── fetch_strapi_content.py
│   │   │   ├── fetch_contentful_content.py
│   │   │   ├── fetch_ghost_content.py
│   │   │   └── push_strapi_seo.py
│   │   ├── references/
│   │   │   └── gsc_setup.md
│   │   └── evals/
│   ├── content-writer/
│   ├── keyword-research/
│   │   └── references/
│   ├── meta-tags-optimizer/
│   │   └── references/
│   ├── schema-markup-generator/
│   │   └── references/
│   ├── seo-page/
│   └── setup-cms/
├── gemini/                     # Cross-model review skill
├── toprank-upgrade-skill/      # Self-updater skill
├── test/                      # Test infrastructure
│   ├── unit/                  # Unit tests
│   ├── helpers/               # Test utilities
│   ├── fixtures/              # Test data
│   └── test_*.py              # E2E/eval tests
├── requirements.txt           # Python dependencies
├── requirements-test.txt     # Test dependencies
├── VERSION                   # Version file
└── README.md                 # Project documentation
```

## Directory Purposes

**`.claude-plugin/`:**
- Purpose: Plugin metadata for Claude Code discovery
- Contains: `plugin.json` (skill registry), `marketplace.json`
- Key files: `plugin.json`

**`.mcp.json`:**
- Purpose: MCP server auto-configuration
- Contains: Server definitions with command/args/transport
- Key files: AdsAgent MCP, Chrome DevTools MCP configs

**`bin/`:**
- Purpose: CLI tools for skills to call
- Contains: `toprank-config`, `toprank-update-check`, Chrome helpers
- Key files: All bash executables

**`google-ads/`:**
- Purpose: Google Ads management skills
- Contains: Shared logic + 3 skills (ads, ads-audit, ads-copy)
- Key files: `shared/preamble.md` (bootstrapping for all)

**`seo/`:**
- Purpose: SEO analysis and optimization skills
- Contains: 7 skills including seo-analysis with extensive scripts
- Key files: `seo-analysis/SKILL.md`, `seo-analysis/scripts/*.py`

**`test/`:**
- Purpose: Test infrastructure
- Contains: Unit tests, LLM-judge eval tests, fixtures
- Key files: `test_skill_e2e.py`, `test_skill_llm_eval.py`

## Key File Locations

**Entry Points:**
- `.claude-plugin/plugin.json`: Skill registry (all skills declared here)
- `SKILL.md` files in each skill folder: Individual skill entry points

**Configuration:**
- `bin/toprank-config`: Config CLI (`~/.toprank/config.yaml`)
- `.mcp.json`: MCP server definitions

**Core Logic:**
- `google-ads/ads/SKILL.md`: Campaign management
- `seo/seo-analysis/SKILL.md`: Full SEO audit
- `google-ads/shared/preamble.md`: Ads bootstrapping (all ads skills read this first)
- `seo/shared/preamble.md`: SEO bootstrapping (all SEO skills read this first)

**Scripts:**
- `seo/seo-analysis/scripts/analyze_gsc.py`: GSC data collection
- `seo/seo-analysis/scripts/pagespeed.py`: PageSpeed API
- `seo/seo-analysis/scripts/url_inspection.py`: URL Inspection API
- `seo/seo-analysis/scripts/cms_detect.py`: CMS detection

**Testing:**
- `test/test_skill_e2e.py`: End-to-end skill tests
- `test/test_skill_llm_eval.py`: LLM-judge evaluation

## Naming Conventions

**Skills:**
- Pattern: `<category>/<skill-name>/`
- Example: `google-ads/ads/`, `seo/seo-analysis/`
- SKILL.md: Always capitalized, no spaces

**Scripts:**
- Pattern: `<descriptive-name>.py`
- Example: `analyze_gsc.py`, `url_inspection.py`
- Executable: Python 3.8+ with stdlib only (or requests)

**References:**
- Pattern: `<descriptive-name>.md`
- Example: `analysis-heuristics.md`, `gaql-cookbook.md`

**Functions (in scripts):**
- Pattern: `snake_case`
- Example: `def fetch_gsc_data()`, `def analyze_results()`

## Where to Add New Code

**New Google Ads Skill:**
- Location: `google-ads/<skill-name>/`
- Files required: `SKILL.md` (with frontmatter name/description)
- Files optional: `scripts/`, `references/`, `evals/`
- Registration: Add to `.claude-plugin/plugin.json`

**New SEO Skill:**
- Location: `seo/<skill-name>/`
- Files required: `SKILL.md` (with frontmatter name/description)
- Files optional: `scripts/`, `references/`, `evals/`
- Registration: Add to `.claude-plugin/plugin.json`

**New Script for Existing Skill:**
- Location: `<skill>/scripts/<descriptive-name>.py`
- Requirements: Python 3.8+, stdlib only (or requests)
- Interface: Support `--output` flag for file output
- Output: stderr for progress, stdout for data

**New Reference Document:**
- Location: `<skill>/references/<descriptive-name>.md`
- Content: Markdown with tables, thresholds, playbooks

**New Eval Tests:**
- Location: `<skill>/evals/evals.json` or `test/test_skill_*.py`

## Special Directories

**`~/.toprank/`:**
- Purpose: User-scoped persistent data
- Generated: Yes (runtime-created)
- Committed: No (in `.gitignore`)
- Contains: `config.yaml`, `business-context/`, `personas/`, `audit-log/`

**`~/.adsagent/`:**
- Purpose: Account config and data
- Generated: Yes (runtime-created)
- Committed: No (project-level overrides in `.gitignore`)
- Contains: `config.json`, per-project data directories

**`.adsagent/`:**
- Purpose: Project-local data (when `.adsagent.json` exists in repo)
- Generated: Yes
- Committed: No (in repo's `.gitignore`)
- Contains: Project-specific account data

---

*Structure analysis: 2026-04-16*