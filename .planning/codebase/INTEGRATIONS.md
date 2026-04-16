# External Integrations

**Analysis Date:** 2026-04-13

## APIs & External Services

### Google Ads

- **AdsAgent MCP** - Primary Google Ads API integration
  - SDK/Client: MCP server via `mcp__adsagent__*` tools
  - Endpoint: `https://adsagent.org/api/mcp` (via npx/mcp-remote)
  - Auth: `ADSAGENT_API_KEY` environment variable (stored in `~/.claude/settings.json`)
  - Reference: `google-ads/shared/preamble.md` handles all Google Ads integration

- **Google Ads MCP (alternative)** - Fallback option
  - SDK/Client: MCP server via `mcp__google_ads_mcp__*` tools
  - Auth: OAuth-based (different from AdsAgent)
  - Reference: Detected automatically in preamble if AdsAgent unavailable

### Google Search Console

- **Google Search Console API** - SEO analysis data source
  - SDK/Client: Direct REST API calls via Python `urllib` (no Google client library)
  - Auth: `gcloud auth application-default print-access-token`
  - API Endpoint: `https://searchconsole.googleapis.com/webmasters/v3/`
  - Reference: `seo/seo-analysis/scripts/analyze_gsc.py`
  - Setup: Requires Google Cloud SDK, Search Console API enabled, OAuth login

- **gcloud CLI** - Token acquisition
  - Used via: `gcloud auth application-default login --scopes=...`
  - Scopes: `https://www.googleapis.com/auth/webmasters`, `webmasters.readonly`

### CMS Connectors

**WordPress:**
- Interface: WordPress REST API (`/wp-json/wp/v2/`)
- Auth: Basic Auth with Application Password
- Env vars: `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- SEO data: Yoast SEO (`yoast_head_json`) and RankMath (`meta.rank_math_*`)
- Reference: `seo/seo-analysis/scripts/fetch_wordpress_content.py`

**Strapi:**
- Interface: Strapi REST API (`/api/{content-type}`)
- Auth: Bearer token (`STRAPI_API_KEY`)
- Env vars: `STRAPI_URL`, `STRAPI_API_KEY`, `STRAPI_CONTENT_TYPE`, `STRAPI_VERSION`
- Versions: Supports both v4 (nested attributes) and v5 (flat response)
- SEO data: plugin-seo component or custom root fields
- Reference: `seo/seo-analysis/scripts/fetch_strapi_content.py`

**Contentful:**
- Interface: Contentful Content API
- Auth: Space ID + Access Token
- Env vars: `CONTENTFUL_SPACE_ID`, `CONTENTFUL_ACCESS_TOKEN`, `CONTENTFUL_ENVIRONMENT`
- Reference: `seo/seo-analysis/scripts/fetch_contentful_content.py`

**Ghost:**
- Interface: Ghost Content API
- Auth: Admin API key or Content API key
- Env vars: `GHOST_URL`, `GHOST_ADMIN_API_KEY` or `GHOST_CONTENT_API_KEY`
- Reference: `seo/seo-analysis/scripts/fetch_ghost_content.py`

### Cross-Model Review

- **Google Gemini CLI** - Secondary opinion for Google Ads/SEO decisions
  - Available via: `gemini` command
  - Used by: `/toprank:gemini` skill
  - Reference: `gemini/SKILL.md`
  - Note: Optional; skill gracefully degrades if not installed

### Chrome DevTools (Future)

- **chrome-devtools-cli** - Intended for remote debugging mode
  - Status: Referenced in available skills but not yet integrated
  - Use case: Future site testing and QA features

## Data Storage

**Local storage:**
- Project-level: `.adsagent/` directory (when `.adsagent.json` exists in repo)
- Global: `~/.adsagent/` for account configuration
- Temp files: Secure temp files for script output (`/tmp/cms_content_{uid}.json`)

**No external database:**
- Plugin does not require external database
- All data flows through APIs and is processed in-memory

## Authentication & Identity

**Auth Providers:**
- AdsAgent: API key via environment variable (`ADSAGENT_API_KEY`)
- Google Cloud: OAuth via gcloud ADC (Application Default Credentials)
- CMS: Various (API keys, Basic Auth, Bearer tokens)

## Monitoring & Observability

**No external services:**
- No error tracking service configured
- No external logging (uses stderr/stdout for script output)

## CI/CD & Deployment

**Hosting:**
- Distribution: Claude Code plugin marketplace
- Repository: GitHub (`nowork-studio/toprank`)
- Install: `/plugin marketplace add nowork-studio/toprank` + `/plugin install toprank@nowork-studio`

**CI Pipeline:**
- Not applicable (plugin distributed via marketplace)

## Environment Configuration

**Required env vars for full functionality:**
- `ADSAGENT_API_KEY` - Google Ads API (in `~/.claude/settings.json`)
- `GLOUD_CONFIG` - Optional, for non-default gcloud config

**CMS env vars (per CMS):**
- WordPress: `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- Strapi: `STRAPI_URL`, `STRAPI_API_KEY`, `STRAPI_CONTENT_TYPE`
- Contentful: `CONTENTFUL_SPACE_ID`, `CONTENTFUL_ACCESS_TOKEN`
- Ghost: `GHOST_URL`, `GHOST_ADMIN_API_KEY`

**Secrets location:**
- API keys stored in `~/.claude/settings.json` under `env` object
- CMS credentials in `.env` or `.env.local` (should be in `.gitignore`)
- Account ID in `.adsagent.json` (project) or `~/.adsagent/config.json` (global)

## Webhooks & Callbacks

**Incoming:**
- None - Plugin is pull-based, not event-driven

**Outgoing:**
- None - No outgoing webhooks configured

---

*Integration audit: 2026-04-13*