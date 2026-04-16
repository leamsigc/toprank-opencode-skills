# Coding Conventions

**Analysis Date:** 2026-04-13

## SKILL.md Frontmatter Format

Every skill must have YAML frontmatter with these required fields:

```yaml
---
name: <skill-name>
description: <Brief description of what the skill does>
argument-hint: "<Optional hint about expected arguments>"
---
```

**Optional fields:**
- `version: <semver>` - For skills with versioning
- `triggers:` - List of phrases that activate the skill

**Example from `google-ads/ads/SKILL.md`:**
```yaml
---
name: ads
description: Manage Google Ads — performance, keywords, bids, budgets, negatives, campaigns, ads, search terms, QS, location targeting, bulk operations. Use for any mention of Google Ads, CPA, ROAS, ad spend, or campaign settings.
argument-hint: "<campaign name, keyword, or 'show performance'>"
version: 3.2.0
triggers:
  - google ads
  - campaigns
  - keywords
  - ad spend
  - CPA
  - ROAS
---
```

**Example from `seo/seo-page/SKILL.md`:**
```yaml
---
name: seo-page
argument-hint: "<URL of the page to analyze, e.g. https://example.com/blog/my-post>"
description: >
  Single-page SEO audit: deep content quality evaluation using Google's E-E-A-T
  framework, Helpful Content guidelines, on-page SEO factors, search intent
  alignment, technical signals, and readability analysis.
---
```

## Python Script Standards

All helper scripts in `scripts/` directories follow these conventions:

**Shebang and imports:**
```python
#!/usr/bin/env python3
"""
<Module docstring explaining purpose and usage.

Usage:
  python3 script.py --site "sc-domain:example.com" --days 90
"""

import argparse
import json
import os
import sys
# ... other stdlib only imports
```

**Argparse for CLI flags:**
```python
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--site', required=True, help='GSC site URL or property')
parser.add_argument('--days', type=int, default=90, help='Number of days to analyze')
parser.add_argument('--output', help='Output JSON file path')
args = parser.parse_args()
```

**Output to file or stdout:**
```python
def main():
    args = parser.parse_args()
    data = fetch_data(args)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        print(json.dumps(data, indent=2))
```

**Key requirements:**
- Use Python stdlib only — no `pip install` dependencies
- Always include `--output` flag for file output
- Print JSON to stdout by default
- Include usage examples in docstring
- Exit with error codes: `sys.exit(1)` on failure

## Reference Document Structure

Reference documents live in `references/` subdirectories within each skill:

```
<skill>/
├── SKILL.md
├── references/
│   ├── content-quality-framework.md
│   ├── session-checks.md
│   └── workflow-playbooks.md
└── scripts/
    └── *.py
```

**Referencing from SKILL.md:**
```markdown
**Always read before Phase 2:**
- `references/account-health-scoring.md` — Diagnostic thresholds and benchmarks
- `references/session-checks.md` — Change review procedures
```

**Reference document naming:**
- Use descriptive names: `session-checks.md`, `bid-strategy-decision-tree.md`
- Use `framework` suffix for methodology docs
- Use `guide` or `reference` suffix for how-to docs

## Commit Message Style

Follows [Keep a Changelog](https://keepachangelog.com/) format:

```
## [0.11.3] — 2026-04-12

### Added
- **Change impact review mode** — Users can now say "check my changes"

### Changed
- **Deduped headline formulas** — Extracted to reference file

### Fixed
- **Session-checks query logic** — Fixed maturation status branching
```

**Rules:**
- Use semantic versioning
- Category order: Added, Changed, Fixed, Removed, Deprecated
- Use past tense for changes
- Be specific about what changed and why

## File Naming

**Skills:**
- SKILL.md - Main skill definition (uppercase, no spaces)
- `references/*.md` - Reference documentation
- `scripts/*.py` - Helper scripts

**Tests:**
- `test/unit/test_*.py` - Unit tests
- `test/helpers/*.py` - Test utilities
- `evals/evals.json` - Skill eval prompts

## Directory Structure

```
toprank/
├── seo/
│   ├── seo-page/SKILL.md
│   ├── seo-page/references/
│   ├── seo-page/scripts/
│   └── seo-page/evals/evals.json
├── google-ads/
│   ├── ads/SKILL.md
│   ├── ads/references/
│   └── ads/evals/evals.json
├── test/
│   ├── unit/test_*.py
│   ├── helpers/*.py
│   └── test_skill_*.py
└── bin/
```

---

*Convention analysis: 2026-04-13*