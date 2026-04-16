# Technology Stack

**Analysis Date:** 2026-04-16

## Languages

**Primary:**
- Python 3.8+ - SEO scripts and CMS connectors use Python stdlib + requests
- TypeScript/OpenCode Plugin API - Plugin definition in `.opencode/plugin.ts`
- Markdown (SKILL.md) - OpenCode/Claude Code skill definitions

**Secondary:**
- Shell (Bash) - Helper scripts and CLI wrappers (bin/toprank-config)
- JSON - Configuration files (.mcp.json, plugin.json, settings)
- Python - Scripts for CMS content fetching, GSC analysis, PageSpeed

## Runtime

**Environment:**
- OpenCode plugin runtime - Skills execute within OpenCode context via `@opencode-ai/plugin` SDK
- Python 3.8+ (for local scripts) - User's local environment runs CMS fetch/analyze scripts

**Package Manager:**
- npm - Manages OpenCode plugin dependencies via `.opencode/package.json`
- pip - Manages Python dependencies via `requirements.txt`
- Lockfile: `.opencode/package-lock.json` (present)

## Frameworks

**Core:**
- OpenCode Plugin SDK - Skill-based plugin architecture
- MCP (Model Context Protocol) - Server for Chrome DevTools and Google Ads API integration

**Testing:**
- pytest - Unit tests in `test/unit/`
- LLM-judge eval system - Custom eval framework in `test/helpers/`

**Build/Dev:**
- npx - MCP server wrapper via `@opencode-ai/adsagent-mcp` and `@modelcontextprotocol/server-chrome-devtools`

## Key Dependencies

**OpenCode SDK (`.opencode/package.json`):**
- `@opencode-ai/plugin` 1.4.6 - OpenCode plugin SDK

**Python (requirements.txt):**
- `google-auth>=2.0.0` - Authentication for Google Search Console API
- `google-auth-httplib2>=0.2.0` - HTTP transport for Google auth
- `requests>=2.28.0` - HTTP requests for CMS API calls

**Python (requirements-test.txt):**
- `google-genai>=1.0.0` - Gemini API for LLM-judge evaluation
- `pytest>=8.0.0` - Test runner
- `pytest-timeout>=2.3.0` - Timeout handling

**MCP Servers (`.mcp.json`):**
- `@opencode-ai/adsagent-mcp` - Google Ads API via AdsAgent
- `@modelcontextprotocol/server-chrome-devtools` - Chrome DevTools Protocol for headless browsing

## Configuration

**Plugin Config:**
- `.opencode/config.json` - Plugin name, version, skill paths
- `.opencode/package.json` - npm dependencies

**MCP Config:**
- `.mcp.json` - MCP server definitions for adsagent and chrome-devtools
- Environment variables: `${ADSAGENT_API_KEY}`, `${CHROME_REMOTE_DEBUGGING_PORT:-9222}`

**Python Config:**
- `requirements.txt` - Runtime dependencies
- `requirements-test.txt` - Test dependencies

**Legacy (Claude Code compatibility):**
- `.claude-plugin/plugin.json` - Plugin manifest for Claude Code marketplace
- `.claude-plugin/marketplace.json` - Marketplace metadata

## Platform Requirements

**Development:**
- OpenCode CLI or Claude Code with plugin support
- Python 3.8+ (for running SEO scripts locally)
- Chrome browser (for remote debugging) or existing CDP endpoint

**Production:**
- OpenCode/Claude Code runtime environment
- Google Cloud SDK + gcloud CLI (for Search Console API via ADC)
- Google Ads account (via AdsAgent MCP)
- CMS credentials for connected systems (WordPress/Strapi/Contentful/Ghost)

---

*Stack analysis: 2026-04-16*