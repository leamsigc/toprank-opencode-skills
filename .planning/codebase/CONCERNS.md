# Codebase Concerns

**Analysis Date:** 2026-04-16

## Tech Debt

### API Key Authentication via Environment Variables

**Issue:** Current API key authentication relies entirely on environment variables (`ADSAGENT_API_KEY`, `PAGESPEED_API_KEY`) stored in `~/.claude/settings.json` or `.env` files.

**Files:**
- `.mcp.json` - Uses `${ADSAGENT_API_KEY}` substitution
- `bin/toprank-config` - Reads from `~/.toprank/config.yaml`
- `seo/seo-analysis/scripts/pagespeed.py` - Checks for `PAGESPEED_API_KEY` in environment

**Impact:** Users must manually manage API keys, set environment variables, and handle key rotation. No unified credential management. The plugin cannot automatically refresh or rotate keys.

**Fix approach:** Implement a credential manager abstraction layer that:
1. Reads from `~/.claude/settings.json` (current approach, preserve compatibility)
2. Adds support for external credential providers
3. Provides `toprank-config creds` subcommand for credential management

### gcloud CLI Dependency for Google Search Console

**Issue:** The `seo-analysis` skill requires gcloud CLI installed and configured to authenticate to Google Search Console. This is a heavy dependency for a plugin that should be lightweight.

**Files:**
- `seo/seo-analysis/scripts/preflight.py` - Requires gcloud for all GSC operations (lines 29-72 check for gcloud)
- `seo/seo-analysis/scripts/analyze_gsc.py` - Uses gcloud token via `get_access_token()` (lines 55-81)
- `seo/seo-analysis/scripts/url_inspection.py` - Uses gcloud token (lines 53-78)
- `seo/seo-analysis/scripts/list_gsc_sites.py` - Uses gcloud token

**Impact:** Users without gcloud installed cannot use SEO features. The gcloud auth flow requires interactive browser login, which breaks in automated contexts. Quota project configuration is error-prone.

**Fix approach:** Add OAuth 2.0 Service Account support as an alternative to gcloud ADC:
1. Support `GOOGLE_SERVICE_ACCOUNT_JSON` env var with service account credentials
2. Update scripts to detect service account vs ADC and use appropriate client
3. Document service account setup in `references/gsc_setup.md`

### MCP Server Dependency for Google Ads

**Issue:** Google Ads functionality depends entirely on the external AdsAgent MCP server (`https://adsagent.org/api/mcp`). If this service goes down or changes, the plugin breaks.

**Files:**
- `.mcp.json` - Defines MCP server connection to adsagent.org (lines 2-12)
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
- `google-ads/shared/preamble.md` - Calls `mcp__adsagent__get_account_info`

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
- `seo/seo-analysis/scripts/analyze_gsc.py` - Uses gcloud token (reads quota_project_id from ADC file, lines 39-52)

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
- `seo/seo-analysis/SKILL.md` - Mentions parallel but doesn't enforce
- `seo/seo-analysis/scripts/url_inspection.py` - Uses ThreadPoolExecutor but only 3 workers (line 254)

**Cause:** WebFetch calls could run in parallel but skill documentation doesn't mandate it. URL inspection uses only 3 concurrent workers.

**Improvement path:** Refactor skill to explicitly use parallel tool calls for all Phase 5 fetches. Increase concurrency in url_inspection.py.

### GSC Data Pulled on Every Invocation

**Issue:** Each SEO audit re-fetches all GSC data from the API, even when recent data exists.

**Files:**
- `seo/seo-analysis/scripts/analyze_gsc.py` - Always pulls fresh data (lines 519-544)
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
- `seo/seo-analysis/scripts/preflight.py` - Many failure modes to handle (412 lines of checks)

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

### Current Status: In Development

**Issue:** The plugin was originally built for Claude Code and has undergone modifications for opencode.ai compatibility.

**Files:**
- `.opencode/plugin.ts` - OpenCode plugin definition (27 lines)
- `.opencode/skills/index.ts` - OpenCode skills index
- `.mcp.json` - MCP server configuration with env substitution

**What's done:**
- Created `.opencode/` directory with plugin.ts format
- MCP servers configured with `${CHROME_REMOTE_DEBUGGING_PORT}` default

**What's needed:**
1. Verify `plugin.json` format is compatible or create `opencode-plugin.json`
2. Test MCP server integration with opencode.ai's MCP handling
3. Verify skill invocation pattern (`/toprank:*` vs opencode.ai's command format)
4. Test environment variable substitution in `.mcp.json`

---

## chrome-devtools Integration Status

### Architecture: Partially Integrated

**Issue:** The `seo-analysis` skill uses WebFetch for site auditing, which is limited (no JavaScript execution, no interactive features). Chrome DevTools MCP is configured but not actively used by skills.

**Files:**
- `.mcp.json` - chrome-devtools MCP server configured (lines 13-22)
- `seo/seo-analysis/scripts/detect_js.py` - JavaScript detection script
- `seo/seo-analysis/scripts/chrome_audit.py` - Chrome-based audit script

**Integration opportunity:**
1. Use chrome-devtools-cli for headless browser-based site auditing
2. Enable JavaScript rendering for SPA/SSR site analysis
3. Support interactive features (forms, auth flows, dynamic content)
4. Enable visual regression testing for design consistency

**Requirements:**
1. Install chrome-devtools-cli skill (user's system)
2. Refactor Phase 5 to use chrome-devtools instead of/in addition to WebFetch
3. Update skill to detect chrome-devtools availability and use appropriate method

**Fix approach:**
1. Add `toprank-chrome-check` to verify chrome-devtools availability
2. Create `seo/seo-analysis/scripts/chrome_audit.py` for headless crawling (already exists)
3. Add `--use-chrome` flag to skills that support both methods

---

## Test Coverage Gaps

### preamble.md Bootstrapping Logic

**What's not tested:** MCP detection, API key verification, config resolution

**Files:**
- `google-ads/shared/preamble.md` - Not covered by unit tests
- `seo/seo-analysis/scripts/preflight.py` - Not covered by unit tests

**Risk:** Breaking changes to preamble logic silently break multiple skills

**Priority:** High

### CMS Connectors

**What's not tested:** All CMS connectors have unit tests but no integration tests against live CMS instances

**Files:**
- `seo/seo-analysis/scripts/fetch_wordpress_content.py` - No integration tests
- `seo/seo-analysis/scripts/fetch_strapi_content.py` - No integration tests
- `seo/seo-analysis/scripts/fetch_contentful_content.py` - No integration tests
- `seo/seo-analysis/scripts/fetch_ghost_content.py` - No integration tests

**Risk:** API changes in CMS platforms break connectors silently

**Priority:** Medium — requires live credentials for each CMS type

### MCP Tool Integration

**What's not tested:** Actual MCP tool calls to AdsAgent or chrome-devtools

**Files:**
- `.mcp.json` - No integration test coverage
- `google-ads/ads/SKILL.md` - Assumes MCP tools work

**Risk:** MCP server changes break functionality without test coverage catching it

**Priority:** Medium — requires live MCP connection

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

## CMS Connector SSRF Protection

### Status: Implemented

The CMS fetch scripts include SSRF protection to prevent attacks against internal networks.

**Implementation:**
- `fetch_wordpress_content.py` - Uses `validate_url()` with IP blacklist check (lines 41-69)
- `fetch_strapi_content.py` - Includes SSRF protection
- `fetch_contentful_content.py` - Includes SSRF protection
- `fetch_ghost_content.py` - Includes SSRF protection

**What's protected:**
- Blocks loopback, private, and link-local IPs
- Prevents access to internal services via the CMS API

**Recommendation:** Document SSRF protection in security documentation

---

*Concerns audit: 2026-04-16*