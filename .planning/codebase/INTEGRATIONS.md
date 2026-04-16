# External Integrations

**Analysis Date:** 2026-04-16

## APIs & External Services

### Google Ads

- **AdsAgent MCP** - Primary Google Ads API integration
  - MCP Server: `@opencode-ai/adsagent-mcp` (via npx)
  - Auth: `ADSAGENT_API_KEY` environment variable
  - Env reference: `${ADSAGENT_API_KEY}` in `.mcp.json`
  - Reference: `google-ads/shared/preamble.md` handles integration

- **Google Ads API Alternative** - Fallback via AdsAgent
  - MCP server handles API access transparently

### Google Search Console

- **Google Search Console API** - SEO analysis data source
  - SDK/Client: Direct REST via Python `google-auth` + `urllib`
  - Auth: Application Default Credentials (ADC) via `gcloud auth application-default login`
  - API Endpoint: `https://searchconsole.googleapis.com/webmasters/v3/`
  - Reference: `seo/seo-analysis/scripts/analyze_gsc.py`

- **URL Inspection API** - Per-URL indexing status
  - Script: `seo/seo-analysis/scripts/url_inspection.py`
  - Auth: Same ADC as Search Console

- **PageSpeed Insights API** - Core Web Vitals metrics
  - Script: `seo/seo-analysis/scripts/pagespeed.py`
  - Auth: API key (optional) or anonymous

### Chrome DevTools

- **Chrome DevTools Protocol (CDP)** - Headless page rendering for JS-heavy sites
  - MCP Server: `@modelcontextprotocol/server-chrome-devtools`
  - Connection: Remote debugging port (default 9222)
  - Env var: `${CHROME_REMOTE_DEBUGGING_PORT:-9222}`
  - Scripts: `seo/seo-analysis/scripts/chrome_audit.py`, `seo/seo-analysis/scripts/detect_js.py`

### CMS Connectors

**WordPress:**
- Interface: WordPress REST API (`/wp-json/wp/v2/`)
- Auth: Basic Auth with Application Password
- Env vars: `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- SEO data: Yoast SEO (`yoast_head_json`) and RankMath (`meta.rank_math_*`)
- Scripts: `fetch_wordpress_content.py`, `preflight_wordpress.py`

**Strapi:**
- Interface: Strapi REST API (`/api/{content-type}`)
- Auth: Bearer token
- Env vars: `STRAPI_URL`, `STRAPI_API_KEY`, `STRAPI_CONTENT_TYPE`
- Versions: v4 (nested attributes) and v5 (flat response)
- Scripts: `fetch_strapi_content.py`, `push_strapi_seo.py`, `preflight_strapi.py`

**Contentful:**
- Interface: Contentful Content API
- Auth: Space ID + Access Token
- Env vars: `CONTENTFUL_SPACE_ID`, `CONTENTFUL_ACCESS_TOKEN`, `CONTENTFUL_ENVIRONMENT`
- Scripts: `fetch_contentful_content.py`, `preflight_contentful.py`

**Ghost:**
- Interface: Ghost Content API + Admin API
- Env vars: `GHOST_URL`, `GHOST_ADMIN_API_KEY` or `GHOST_CONTENT_API_KEY`
- Scripts: `fetch_ghost_content.py`, `preflight_ghost.py`

All CMS fetchers use Python stdlib `urllib` (requests available but not required).

### Cross-Model Review

- **Google Gemini CLI** - Secondary opinion for Google Ads/SEO decisions
  - Reference: `gemini/SKILL.md`
  - Note: Optional; skill gracefully degrades if not installed

## Data Storage

**Local storage:**
- `~/.toprank/` - User home directory for config, business context, audit logs
- Project-level: `.adsagent.json` (Google Ads account configuration)
- Global: `~/.adsagent/config.json` (account configuration)
- Temp files: Secure temp files for script output (`/tmp/cms_content_{uid}.json`)

**No external database:**
- Plugin is pull-based, stateless
- All data flows through APIs and is processed in-memory

## Authentication & Identity

**Auth Providers:**
- Google Ads (AdsAgent): API key via `ADSAGENT_API_KEY` env var
- Google Search Console/URL Inspection: OAuth via gcloud ADC
- PageSpeed: API key (optional) or anonymous
- CMS: Various (API keys, Basic Auth, Bearer tokens per CMS)

**ADC Setup:**
```bash
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/webmasters,webmasters.readonly
```

## Monitoring & Observability

**No external services:**
- No error tracking service configured
- No external logging (uses stderr/stdout for script output)

## CI/CD & Distribution

**Hosting:**
- OpenCode plugin marketplace
- Claude Code plugin marketplace (`.claude-plugin/marketplace.json`)
- Repository: GitHub (`nowork-studio/toprank`)

**CI Pipeline:**
- None (plugin distributed via marketplace)

## Environment Configuration

**Required env vars:**
- `ADSAGENT_API_KEY` - Google Ads API (get free at adsagent.org)
- `CHROME_REMOTE_DEBUGGING_PORT` - Chrome debug port (optional, defaults to 9222)

**CMS env vars (per CMS type):**
- WordPress: `WP_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`
- Strapi: `STRAPI_URL`, `STRAPI_API_KEY`, `STRAPI_CONTENT_TYPE`
- Contentful: `CONTENTFUL_SPACE_ID`, `CONTENTFUL_ACCESS_TOKEN`
- Ghost: `GHOST_URL`, `GHOST_ADMIN_API_KEY`

**Secrets location:**
- API keys in `.mcp.json` env section (substituted from user environment)
- CMS credentials in `.env` or `.env.local` (should be in `.gitignore`)
- Account ID in `.adsagent.json` (project) or `~/.adsagent/config.json` (global)

## Webhooks & Callbacks

**Incoming:**
- None - Plugin is pull-based, not event-driven

**Outgoing:**
- None - No outgoing webhooks configured

---

*Integration audit: 2026-04-16*