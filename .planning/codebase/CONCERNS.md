# Codebase Concerns

**Analysis Date:** 2026-04-13

## Tech Debt

### API Key Authentication via Environment Variables

**Issue:** Current API key authentication relies entirely on environment variables (`ADSAGENT_API_KEY`, `PAGESPEED_API_KEY`, etc.) stored in `~/.claude/settings.json` or `.env` files.

**Files:**
- `.mcp.json` - Uses `${ADSAGENT_API_KEY}` substitution
- `bin/toprank-config` - Reads from `~/.toprank/config.yaml`
- `seo/seo-analysis/scripts/preflight.py` - Checks for `PAGESPEED_API_KEY` in environment

**Impact:** Users must manually manage API keys, set environment variables, and handle key rotation. No unified credential management. The plugin cannot automatically refresh or rotate keys.

**Fix approach:** Implement a credential manager abstraction layer that:
1. Reads from `~/.claude/settings.json` (current approach, preserve compatibility)
2. Adds support for external credential providers
3. Provides `toprank-config creds` subcommand for credential management

### gcloud CLI Dependency for Google Search Console

**Issue:** The `seo-analysis` skill requires gcloud CLI installed and configured to authenticate to Google Search Console. This is a heavy dependency for a plugin that should be lightweight.

**Files:**
- `seo/seo-analysis/scripts/preflight.py` - Requires gcloud for all GSC operations
- `seo/seo-analysis/scripts/analyze_gsc.py` - Uses gcloud token
- `seo/seo-analysis/scripts/list_gsc_sites.py` - Uses gcloud token

**Impact:** Users without gcloud installed cannot use SEO features. The gcloud auth flow requires interactive browser login, which breaks in automated contexts. Quota project configuration is error-prone.

**Fix approach:** Add OAuth 2.0 Service Account support as an alternative to gcloud ADC:
1. Support `GOOGLE_SERVICE_ACCOUNT_JSON` env var with service account credentials
2. Update scripts to detect service account vs ADC and use appropriate client
3. Document service account setup in `references/gsc_setup.md`

### MCP Server Dependency for Google Ads

**Issue:** Google Ads functionality depends entirely on the external AdsAgent MCP server (`https://adsagent.org/api/mcp`). If this service goes down or changes, the plugin breaks.

**Files:**
- `.mcp.json` - Defines MCP server connection to adsagent.org
- `google-ads/shared/preamble.md` - Detects MCP availability

**Impact:** No offline capability. Feature parity depends on external service. No way to debug MCP issues internally.

**Fix approach:** Provide a fallback:
1. Add support for Google Ads API directly via googleads-python library
2. Use AdsAgent MCP as primary, direct API as fallback when MCP unavailable
3. Surface MCP errors with actionable diagnostics

---

## Known Bugs

### MCP Tool Naming Convention Incompatibility

**Issue:** MCP tool names use double-underscore prefix (`mcp__adsagent__*`) which may not be recognized by all Claude Code versions or opencode.ai.

**Files:**
- `.mcp.json` - Uses `mcp__adsagent__*` tool pattern
- `google-ads/shared/preamble.md` - Calls `mcp__adsagent__getAccountInfo`

**Trigger:** Running in opencode.ai or different Claude Code version

**Workaround:** Update to standard MCP tool invocation format when confirmed.

### Script Exit Codes Not Consistently Handled

**Issue:** Some scripts return exit code 0 even on partial failures, making error detection unreliable.

**Files:**
- `seo/seo-analysis/scripts/cms_detect.py` - Exit codes 0/1/2 for different states
- `seo/seo-analysis/scripts/fetch_strapi_content.py` - Partial success not distinguished

**Trigger:** CMS fetch operations with mixed success

**Workaround:** Document expected exit codes in skill documentation; update scripts to distinguish states clearly.

---

## Security Considerations

### API Keys in Environment Variables

**Risk:** API keys are stored in `~/.claude/settings.json` under `env` object, which may be synced across devices or visible in process listings.

**Files:**
- `.mcp.json` - References `${ADSAGENT_API_KEY}`
- `bin/toprank-config` - Stores config in user home directory

**Current mitigation:** Keys stored in Claude Code's settings.json, which is gitignored and user-local.

**Recommendations:**
1. Add support for external secret managers (1Password, Bitwarden)
2. Implement key encryption at rest
3. Add `toprank-config secrets` subcommand to rotate keys

### gcloud ADC Credentials File Access

**Risk:** The plugin reads gcloud Application Default Credentials from `~/.config/gcloud/application_default_credentials.json`, which contains long-lived tokens.

**Files:**
- `seo/seo-analysis/scripts/preflight.py` - Reads ADC for token
- `seo/seo-analysis/scripts/analyze_gsc.py` - Uses gcloud token

**Current mitigation:** Credentials are user-controlled and scoped to specific APIs.

**Recommendations:**
1. Warn users about ADC token scope
2. Document how to revoke and re-authenticate
3. Add `toprank-gcloud-revoke` helper script

---

## Performance Bottlenecks

### Sequential Script Execution in SEO Analysis

**Issue:** Phase 5 (technical SEO audit) runs page fetches sequentially when parallel execution would be faster.

**Files:**
- `seo/seo-analysis/SKILL.md` - Line 792-795 mentions parallel but doesn't enforce

**Cause:** WebFetch calls could run in parallel but skill documentation doesn't mandate it.

**Improvement path:** Refactor skill to explicitly use parallel tool calls for all Phase 5 fetches.

### GSC Data Pulled on Every Invocation

**Issue:** Each SEO audit re-fetches all GSC data from the API, even when recent data exists.

**Files:**
- `seo/seo-analysis/scripts/analyze_gsc.py` - Always pulls fresh data
- `seo/seo-analysis/SKILL.md` - No data caching between sessions

**Cause:** No session-level caching mechanism; data is not persisted between skill invocations.

**Improvement path:**
1. Cache GSC data in `~/.toprank/cache/` with TTL
2. Use cache by default, allow `--refresh` flag for fresh data
3. Add `toprank-cache-clear` command

---

## Fragile Areas

### preamble.md Bootstrapping Logic

**Files:**
- `google-ads/shared/preamble.md` - Complex branching logic for MCP detection
- `seo/seo-analysis/scripts/preflight.py` - Many failure modes to handle

**Why fragile:** Multiple interdependent checks (gcloud, project, API, credentials, quota project). Failure at any step blocks all subsequent steps. Error messages may not match user's actual problem.

**Safe modification:** Add more granular error diagnostics with specific fix suggestions per failure mode.

### MCP Server Connection Without Health Check

**Files:**
- `.mcp.json` - No connection health verification
- `google-ads/shared/preamble.md` - Uses MCP tools without pre-flight check

**Why fragile:** If MCP server is unreachable, the first tool call fails with an opaque error. No way to distinguish network issues from server issues from auth issues.

**Safe modification:** Add `toprank-mcp-health` command to verify connectivity before skill execution.

---

## Scaling Limits

### GSC API Quota

**Current capacity:** Varies by Google Cloud project; typically 10,000-100,000 requests/day

**Limit:** Large sites (>10,000 pages) may hit GSC API limits during deep audits

**Scaling path:**
1. Implement pagination with rate limiting
2. Add quota tracking and warnings
3. Support batch analysis over multiple sessions

### MCP Request Size

**Current capacity:** Depends on AdsAgent server; no documented limit

**Limit:** Large account operations (10,000+ keywords) may timeout

**Scaling path:**
1. Add bulk operation timeouts
2. Implement progress tracking for long operations
3. Add `--async` flag for operations that complete via webhook

---

## Dependencies at Risk

### AdsAgent MCP Server

**Risk:** External service dependency — `https://adsagent.org/api/mcp`

**Impact:** If adsagent.org goes down or changes API, all Google Ads features break.

**Migration plan:**
1. Implement direct Google Ads API as fallback (see Tech Debt section)
2. Document alternative MCP servers if available
3. Add local-only mode for read-only operations

### gcloud CLI

**Risk:** Heavy system dependency required for core SEO functionality

**Impact:** Users must install 300+ MB SDK for a plugin that should be lightweight

**Migration plan:**
1. Add service account support (OAuth 2.0) as alternative (see Tech Debt section)
2. Document minimal gcloud install for CI/automated contexts

---

## opencode.ai Plugin Compatibility

### Current Status: Not Tested

**Issue:** The plugin is built for Claude Code (`@nowork-studio/toprank`) and has not been verified to work with opencode.ai's plugin system.

**Files:**
- `.claude-plugin/plugin.json` - Claude Code specific format
- `.claude-plugin/marketplace.json` - Claude Code marketplace metadata

**Requirements for opencode.ai compatibility:**
1. Verify `plugin.json` format is compatible or create `opencode-plugin.json`
2. Test MCP server integration with opencode.ai's MCP handling
3. Verify skill invocation pattern (`/toprank:*` vs opencode.ai's command format)
4. Test environment variable substitution in `.mcp.json`

**Fix approach:**
1. Create `opencode/` directory with opencode.ai-specific configurations
2. Add `opencode-plugin.json` if format differs from `plugin.json`
3. Test skill loading in opencode.ai environment

---

## Chrome DevTools Integration (Future)

### Current Architecture: Not Integrated

**Issue:** The `seo-analysis` skill uses WebFetch for site auditing, which is limited (no JavaScript execution, no interactive features).

**Files:**
- `seo/seo-analysis/SKILL.md` - Uses WebFetch for page auditing
- `seo/seo-analysis/scripts/pagespeed.py` - Uses PageSpeed API instead of real browser

**Integration opportunity:**
1. Use chrome-devtools-cli for headless browser-based site auditing
2. Enable JavaScript rendering for SPA/SSR site analysis
3. Support interactive features (forms, auth flows, dynamic content)
4. Enable visual regression testing for design consistency

**Requirements:**
1. Install chrome-devtools-cli skill
2. Refactor Phase 5 to use chrome-devtools instead of/in addition to WebFetch
3. Update skill to detect chrome-devtools availability and use appropriate method

**Fix approach:**
1. Add `toprank-chrome-check` to verify chrome-devtools availability
2. Create `seo/seo-analysis/scripts/chrome_audit.py` for headless crawling
3. Add `--use-chrome` flag to skills that support both methods

---

## Test Coverage Gaps

### preamble.md Bootstrapping Logic

**What's not tested:** MCP detection, API key verification, config resolution

**Files:**
- `google-ads/shared/preamble.md` - Not covered by unit tests
- `seo/seo-analysis/scripts/preflight.py` - Partial coverage

**Risk:** Breaking changes to preamble logic silently break multiple skills

**Priority:** High

### CMS Connectors

**What's not tested:** All CMS connectors have unit tests but no integration tests against live CMS instances

**Files:**
- `seo/seo-analysis/scripts/fetch_wordpress_content.py`
- `seo/seo-analysis/scripts/fetch_strapi_content.py`
- `seo/seo-analysis/scripts/fetch_contentful_content.py`
- `seo/seo-analysis/scripts/fetch_ghost_content.py`

**Risk:** API changes in CMS platforms break connectors silently

**Priority:** Medium — requires live credentials for each CMS type

### MCP Tool Integration

**What's not tested:** Actual MCP tool calls to AdsAgent

**Files:**
- `.mcp.json` - No integration test coverage
- `google-ads/ads/SKILL.md` - Assumes MCP tools work

**Risk:** MCP server changes break functionality without test coverage catching it

**Priority:** Medium — requires live AdsAgent connection

---

## Migration Path: MCP to chrome-devtools CLI

### Phase 1: Detect chrome-devtools Availability

**Implementation:**
1. Add `toprank-chrome-available` helper that checks for chrome-devtools-cli skill
2. Store detection in `~/.toprank/config.yaml`
3. Gracefully degrade to WebFetch if chrome-devtools unavailable

### Phase 2: Create chrome-devtools-Based Scripts

**New files:**
- `seo/seo-analysis/scripts/chrome_crawl.py` - Headless crawl using chrome-devtools
- `seo/seo-analysis/scripts/chrome_pagespeed.py` - Lighthouse via CDP
- `seo/seo-analysis/scripts/chrome_screenshot.py` - Visual regression baseline

**Pattern:**
```python
# Example chrome-devtools integration
import json
import subprocess

def run_chrome_audit(urls: list[str], output_file: str):
    """Run headless Chrome audit via CDP."""
    # Connect to Chrome via chrome-devtools-cli
    # Fetch each URL, extract SEO signals
    # Write results to output_file
```

### Phase 3: Update Skills to Use chrome-devtools

**Files to update:**
- `seo/seo-analysis/SKILL.md` - Phase 5 and 5.5
- Add new trigger patterns for chrome-specific features

**Changes:**
1. Add `--use-chrome` flag to skills
2. Update Phase 5 to prefer chrome-devtools when available
3. Add "visual audit" feature using chrome-devtools screenshot

### Phase 4: Remove gcloud Dependency (Long-term)

**Goal:** Use chrome-devtools for all Google properties instead of API calls

**Implementation:**
1. Scrape Google Search Console directly via headless Chrome
2. Use Chrome extension for Google Ads (if available)
3. Remove gcloud requirement entirely

**Risk:** May violate Google Terms of Service. Verify before implementing.

---

## Missing Critical Features

### Offline Mode

**Problem:** No functionality works without internet connectivity

**Impact:** Users cannot use plugin on airplane, in remote locations, or during outages

**Priority:** Medium — Add read-only mode with cached data

### Session Persistence

**Problem:** Each skill invocation starts fresh; no state carries between invocations

**Impact:** Repeated audits re-fetch all data; no baseline tracking across sessions

**Priority:** Medium — Implement session-level caching

### Multi-Account Support

**Problem:** Single Google Ads account at a time; switching requires re-configuration

**Impact:** Agencies managing multiple client accounts cannot easily switch contexts

**Priority:** Low — Add `toprank-switch-account` command

---

*Concerns audit: 2026-04-13*