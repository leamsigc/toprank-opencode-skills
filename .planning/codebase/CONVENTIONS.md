# Coding Conventions

**Analysis Date:** 2026-04-16

## SKILL.md Frontmatter Format

Every skill must have YAML frontmatter with required fields:

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
- Print progress/errors to stderr
- Include usage examples in docstring
- Exit with error codes: `sys.exit(1)` on failure

## Naming Patterns

**Files:**
- SKILL.md - Main skill definition (uppercase, no spaces)
- `references/*.md` - Reference documentation (descriptive names)
- `scripts/*.py` - Helper scripts (snake_case)
- `test/unit/test_*.py` - Unit tests (test_ prefix)
- `test/helpers/*.py` - Test utilities (snake_case)

**Functions:**
- snake_case - `def get_access_token()`, `def derive_cannibalization()`

**Variables:**
- snake_case - `token`, `site_url`, `results`

**Types:**
- PascalCase for classes - `class TestDateRange`, `class JudgeScore`
- camelCase for dataclass fields

## Code Style

**Formatting:**
- No automated formatter detected (manual formatting used)
- 4-space indentation
- Maximum line length ~100 characters

**Linting:**
- Not detected - no linting config found

**Import Organization:**
1. Standard library imports (os, sys, json, etc.)
2. Third-party imports (from unittest.mock, etc.)
3. Local imports (relative paths)

## Error Handling

**Patterns:**
- API failures return empty data structures (not exceptions)
- Network errors logged to stderr, return `{"rows": []}`
- Authentication errors exit with `sys.exit(1)` after user-friendly message

Example from `seo/seo-analysis/scripts/analyze_gsc.py`:
```python
except urllib.error.HTTPError as e:
    err_body = e.read().decode() if e.fp else "(no body)"
    print(f"GSC API error {e.code}: {err_body}", file=sys.stderr)
    return {"rows": []}
except urllib.error.URLError as e:
    print(f"GSC API network error: {e.reason}", file=sys.stderr)
    return {"rows": []}
```

## Logging

**Framework:** stderr printing

**Patterns:**
- Progress messages to stderr: `print(f"Pulling {args.days} days...", file=sys.stderr)`
- Success indicators: `print(f"  ✓ {name}", file=sys.stderr)`
- Error messages with context: `print("ERROR: gcloud not found...", file=sys.stderr)`
- Summary output at end with key metrics

## Comments

**When to Comment:**
- Document external dependencies in docstrings
- Explain non-obvious business logic thresholds
- Document API call limits and rate considerations

**Docstrings:**
- Module-level docstrings for main scripts
- Function docstrings with usage examples

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

*Convention analysis: 2026-04-16*
