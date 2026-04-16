# Testing Patterns

**Analysis Date:** 2026-04-13

## Test Framework

**Runner:**
- pytest - Primary test runner
- unittest - Base classes for unit tests
- Config: Root-level `conftest.py`

**Run commands:**
```bash
pytest test/unit/ -v                    # Run unit tests
pytest test/test_skill_llm_eval.py -v   # Run LLM-judge evals
EVALS=1 pytest                          # Enable LLM-judge tests
```

## Unit Tests

**Location:** `test/unit/`

**Purpose:** Test pure logic functions — no external API calls, no gcloud, no credentials needed.

**Example from `test/unit/test_analyze_gsc.py`:**
```python
"""
Unit tests for seo-analysis/scripts/analyze_gsc.py

Tests the pure logic functions — no GSC API calls, no gcloud needed.
These run instantly and catch bugs in the data processing pipeline.

Run: pytest test/unit/test_analyze_gsc.py -v
"""

import importlib.util
import os
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Load script as module without executing main()
_SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'skills', 'seo-analysis', 'scripts', 'analyze_gsc.py'
)
spec = importlib.util.spec_from_file_location('analyze_gsc', _SCRIPT_PATH)
gsc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gsc)


class TestDateRange(unittest.TestCase):
    """date_range() returns the correct window with the 3-day GSC lag."""

    def test_returns_two_strings(self):
        start, end = gsc.date_range(90)
        self.assertIsInstance(start, str)
        self.assertIsInstance(end, str)

    def test_end_is_three_days_ago(self):
        _, end = gsc.date_range(90)
        expected_end = (date.today() - timedelta(days=3)).isoformat()
        self.assertEqual(end, expected_end)
```

**Key patterns:**
- Import script as module using `importlib.util`
- Use unittest.TestCase for organization
- Mock external dependencies (API calls, file I/O)
- Test boundary conditions explicitly

## LLM-Judge Evals

**Location:** `test/helpers/`

**Purpose:** Evaluate SKILL.md quality using LLM-as-judge with Gemini.

**Configuration:**
- Model: `gemini-2.0-flash` (configured in `test/helpers/llm_judge.py`)
- API Key: Set via `GEMINI_API_KEY` or `GOOGLE_GENERATIVE_AI_API_KEY` env var
- Package: Requires `google-genai` package

**Run:**
```bash
EVALS=1 pytest test/test_skill_llm_eval.py              # Run all evals
EVALS=1 EVALS_BASE=main pytest                            # Run changed tests only
EVALS=1 EVALS_ALL=1 pytest                                # Run all tests regardless of changes
```

**Cost:** ~$0.05 per run (Gemini Flash)

## Test Structure

**LLM-judge test file (`test/test_skill_llm_eval.py`):**
```python
"""
LLM-as-a-Judge evals for seo-analysis SKILL.md quality.

Run: EVALS=1 pytest test/test_skill_llm_eval.py
Cost: ~$0.05 per run (Gemini Flash)
"""

import os
import sys
from pathlib import Path

import pytest

from helpers.llm_judge import extract_section, run_judge_test
from helpers.eval_store import EvalCollector
from helpers.touchfiles import (
    select_tests, detect_base_branch, get_changed_files,
    LLM_JUDGE_TOUCHFILES, GLOBAL_TOUCHFILES,
)

ROOT = Path(__file__).parent.parent
SKILL_MD = ROOT / 'skills' / 'seo-analysis' / 'SKILL.md'

EVALS = bool(os.environ.get('EVALS'))
pytestmark = pytest.mark.skipif(not EVALS, reason='Set EVALS=1 to run LLM-judge evals')

# ... selection logic for changed-file detection

SUITE = 'seo-analysis SKILL.md quality'


def _skip(name: str) -> bool:
    return not EVALS or (_selected is not None and name not in _selected)


@pytest.mark.skipif(_skip('seo-phases-clarity'), reason='not selected')
def test_seo_phases_clarity():
    run_judge_test('seo-phases-clarity', SUITE,
        'Phase 1-3 (setup & data collection)',
        extract_section(_skill_md, '## Phase 1', '## Phase 4'),
        _collector)
```

**Quality gates (from `test/helpers/llm_judge.py`):**
```python
MIN_CLARITY = 4       # 1-5: can an agent understand what to do?
MIN_COMPLETENESS = 4  # 1-5: is all needed info present?
MIN_ACTIONABILITY = 4  # 1-5: can an agent act without guessing?
```

**Judge scoring:**
- `clarity` - Can an agent understand what to do?
- `completeness` - Is all needed info present?
- `actionability` - Can an agent act without guessing?

## Skill Eval Prompts

**Location:** Each skill has `evals/evals.json`

**Format:**
```json
{
  "skill_name": "seo-page",
  "evals": [
    {
      "id": 1,
      "prompt": "analyze https://www.adsagent.org — how's the SEO on the homepage?",
      "expected_output": "A scored single-page report covering E-E-A-T, content quality...",
      "files": []
    },
    {
      "id": 2,
      "prompt": "can you check this page for me? https://www.pawsvip.com/services/dog-grooming",
      "expected_output": "A comprehensive page analysis with E-E-A-T scores...",
      "files": []
    }
  ]
}
```

**Purpose:** Defines test prompts that skills should handle correctly. Used for:
- Manual testing during development
- Automated skill evaluation
- Regression testing

## Touchfiles Selection

**Purpose:** Run only tests relevant to changed files.

**Configured in `test/helpers/touchfiles.py`:**
- `LLM_JUDGE_TOUCHFILES` - Maps test names to file patterns they test
- `GLOBAL_TOUCHFILES` - Tests that run on any file change

**Behavior:**
- When changes detected: runs only matching tests
- No changes detected: runs nothing (or all with `EVALS_ALL=1`)

## Test Fixtures

**Location:** `test/fixtures/`

**Example fixtures:**
- `mock-analyze-gsc.py` - Mock GSC response data
- `sample_gsc_data.json` - Sample GSC API response
- `mock-gcloud.sh` - Mock gcloud CLI responses

## Eval Store

**Purpose:** Collect and store eval results for trend analysis.

**Location:** `test/helpers/eval_store.py`

**Usage:**
```python
from helpers.eval_store import EvalCollector

collector = EvalCollector('llm-judge')
# ... run tests ...
collector.finalize()  # Saves results
```

---

*Testing analysis: 2026-04-13*