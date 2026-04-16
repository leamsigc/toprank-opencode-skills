# Testing Patterns

**Analysis Date:** 2026-04-16

## Test Framework

**Runner:**
- pytest - Primary test runner
- unittest - Base classes for unit tests
- Config: Root-level `conftest.py` at `conftest.py`

**Run commands:**
```bash
pytest test/unit/ -v                    # Run unit tests
pytest test/unit/test_analyze_gsc.py -v # Run specific test
EVALS=1 pytest                          # Enable LLM-judge tests
```

## Test File Organization

**Location:**
- `test/unit/test_*.py` - Unit tests (co-located with similar naming)
- `test/test_skill_*.py` - E2E and eval tests
- `test/helpers/*.py` - Test utilities

**Naming:**
- `test_*.py` pattern for test files
- Test classes use PascalCase: `class TestDateRange(unittest.TestCase)`

**Structure:**
```
test/
├── unit/
│   ├── test_analyze_gsc.py
│   ├── test_cms_scripts.py
│   └── test_url_inspection.py
├── helpers/
│   ├── __init__.py
│   ├── session_runner.py
│   ├── llm_judge.py
│   ├── eval_store.py
│   └── touchfiles.py
├── fixtures/
│   ├── mock-analyze-gsc.py
│   ├── sample_gsc_data.json
│   └── mock-gcloud.sh
├── test_skill_e2e.py
├── test_skill_llm_eval.py
└── test_ads_skill_llm_eval.py
```

## Unit Tests

**Location:** `test/unit/`

**Purpose:** Test pure logic functions — no external API calls, no gcloud, no credentials needed.

**Example from `test/unit/test_analyze_gsc.py` (958 lines):**
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
```

**Key patterns:**
- Import script as module using `importlib.util.spec_from_file_location`
- Use `unittest.TestCase` for organization
- Mock external dependencies with `unittest.mock.patch`
- Test boundary conditions explicitly
- Each test class focuses on a specific function

**Test class organization:**
```python
class TestDeriveCannibalization(unittest.TestCase):
    """derive_cannibalization() finds queries where multiple pages compete."""

    def _make_row(self, query, page, clicks, impressions, ctr=0.05, position=8.0):
        return {'keys': [query, page], 'clicks': clicks, 'impressions': impressions,
                'ctr': ctr, 'position': position}
```

## Test Structure

### E2E Tests (`test/test_skill_e2e.py`)

**Purpose:** Spawns `claude -p` with the skill installed in a temp working directory. Uses mock scripts and fixture data so no real Google credentials are needed.

**Key features:**
- Creates temporary workdir with skill copied
- Mocks GSC scripts with fixture data
- Uses mock gcloud CLI
- Records tool calls and output
- Uses LLM judge for report quality scoring

```python
def test_seo_fixture_full_audit():
    result = run_skill_test(
        prompt='Run the seo-analysis skill for sc-domain:example-saas.com...',
        working_directory=workdir,
        max_turns=35,
        timeout_ms=5 * 60 * 1000,
        test_name='seo-fixture-full-audit',
    )
```

### LLM-Judge Tests (`test/helpers/llm_judge.py`)

**Purpose:** Evaluate SKILL.md quality using LLM-as-judge with Gemini.

**Configuration:**
- Model: `gemini-2.0-flash` (configured in `test/helpers/llm_judge.py`)
- API Key: Set via `GEMINI_API_KEY` or `GOOGLE_GENERATIVE_AI_API_KEY` env var
- Package: Requires `google-genai` package

**Run:**
```bash
EVALS=1 pytest test/test_skill_llm_eval.py              # Run all evals
EVALS=1 EVALS_BASE=main pytest                          # Run changed tests only
EVALS=1 EVALS_ALL=1 pytest                              # Run all tests regardless of changes
```

**Cost:** ~$0.02 per run (Gemini Flash)

**Quality gates:**
```python
MIN_CLARITY = 4       # 1-5: can an agent understand what to do?
MIN_COMPLETENESS = 4  # 1-5: is all needed info present?
MIN_ACTIONABILITY = 4  # 1-5: can an agent act without guessing?
```

**Judge scoring:**
- `clarity` - Can an agent understand what to do?
- `completeness` - Is all needed info present?
- `actionability` - Can an agent act without guessing?

## Mocking

**Framework:** `unittest.mock` (MagicMock, patch)

**Patterns:**
- Mock external API calls at the function level
- Mock subprocess calls for CLI tools
- Mock file I/O where needed

**What to Mock:**
- GSC API calls (`gsc.gsc_query`)
- gcloud CLI subprocess calls
- Network requests (urllib)

**What NOT to Mock:**
- Pure logic functions (date parsing, data transformation)
- Internal calculations

Example mocking pattern:
```python
def _run_buckets(self, rows):
    token = 'fake-token'
    mock_data = {'rows': rows}

    with patch.object(gsc, 'gsc_query', return_value=mock_data):
        return gsc.pull_position_buckets(token, 'sc-domain:test.com', '2025-01-01', '2025-03-31')
```

## Fixtures and Factories

**Location:** `test/fixtures/`

**Example fixtures:**
- `mock-analyze-gsc.py` - Mock GSC response data
- `sample_gsc_data.json` - Sample GSC API response JSON
- `mock-gcloud.sh` - Mock gcloud CLI script

**Test data factories:**
```python
def _make_row(self, query, page, clicks, impressions, ctr=0.05, position=8.0):
    return {'keys': [query, page], 'clicks': clicks, 'impressions': impressions,
            'ctr': ctr, 'position': position}
```

## Eval Store

**Purpose:** Collect and store eval results for trend analysis.

**Location:** `test/helpers/eval_store.py`

**Usage:**
```python
from helpers.eval_store import EvalCollector, EvalTestEntry

collector = EvalCollector('llm-judge')
collector.add_test(EvalTestEntry(
    name='test_name',
    suite='test_suite',
    tier='llm-judge',
    passed=True,
    duration_ms=5000,
    cost_usd=0.02,
))
collector.finalize()  # Saves results
```

## Test Types

### Unit Tests
- Location: `test/unit/`
- Scope: Pure logic functions, no external dependencies
- Run: `pytest test/unit/ -v`

### E2E Tests
- Location: `test/test_skill_e2e.py`
- Scope: Full skill workflow with mocked external services
- Requires: `EVALS=1` environment variable
- Timeout: 4-6 minutes per test

### LLM-Judge Tests
- Location: `test/test_skill_llm_eval.py`
- Scope: SKILL.md documentation quality
- Requires: `EVALS=1` + Gemini API key

## Common Patterns

### Async/Subprocess Testing
```python
# Mock subprocess for gcloud calls
mock_result = MagicMock()
mock_result.returncode = 0
mock_result.stdout = 'ya29.my-token\n'
with patch('subprocess.run', return_value=mock_result):
    token = gsc.get_access_token()
```

### Error Testing
```python
def test_exits_when_gcloud_not_found(self):
    with patch('subprocess.run', side_effect=FileNotFoundError):
        with self.assertRaises(SystemExit):
            gsc.get_access_token()
```

### Boundary Testing
```python
def test_boundary_impressions_501(self):
    q = self._make_query(impressions=501, ctr=2.5, position=8)
    opps = self._get_opportunities([q])
    self.assertEqual(len(opps), 1)
```

---

*Testing analysis: 2026-04-16*
