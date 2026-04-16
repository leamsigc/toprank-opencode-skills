# Technology Stack

**Analysis Date:** 2026-04-13

## Languages

**Primary:**
- Python 3.8+ - All SEO scripts and CMS connectors use Python stdlib + requests
- Markdown (SKILL.md) - Claude Code skill definitions

**Secondary:**
- Shell (Bash) - Helper scripts and CLI wrappers
- JSON - Configuration files (.mcp.json, plugin.json, settings)

## Runtime

**Environment:**
- Claude Code plugin runtime - Skills execute within Claude Code context
- Python 3.8+ (for local scripts) - User's local environment runs CMS fetch/analyze scripts

**Package Manager:**
- pip (for local dependencies)
- npm (for MCP server wrapper via npx)

## Frameworks

**Core:**
- Claude Code plugin system - Skill-based plugin architecture
- MCP (Model Context Protocol) - Server for Google Ads API via AdsAgent

**Testing:**
- pytest - Unit tests in `test/unit/`
- LLM-judge eval system - Custom eval framework in `test/helpers/`

**Build/Dev:**
- npx/mcp-remote - HTTP transport wrapper for MCP server

## Key Dependencies

**In `requirements.txt`:**
- `google-auth>=2.0.0` - Authentication for Google Search Console API
- `google-auth-httplib2>=0.2.0` - HTTP transport for Google auth
- `requests>=2.28.0` - HTTP requests for CMS API calls

**No external dependencies for CMS scripts:**
- All CMS connectors (WordPress, Strapi, Contentful, Ghost) use Python stdlib only
- No pip packages required for seo-analysis scripts

## Configuration

**Environment:**
- `~/.claude/settings.json` - Plugin configuration including `env.ADSAGENT_API_KEY`
- `.env` or `.env.local` files - CMS credentials (WP_URL, STRAPI_URL, CONTENTFUL_SPACE_ID, GHOST_URL)
- `.adsagent.json` - Project-level Google Ads account configuration
- `~/.adsagent/config.json` - Global Google Ads account configuration

**Build:**
- `.claude-plugin/plugin.json` - Plugin manifest defining all skills
- `.mcp.json` - MCP server configuration for AdsAgent

## Platform Requirements

**Development:**
- Claude Code installed
- Python 3.8+ (for running SEO scripts locally)
- Google Cloud SDK + gcloud CLI (for Search Console API)
- Optional: Gemini CLI (for gemini skill cross-model review)

**Production:**
- Claude Code plugin runtime
- AdsAgent API key (free at adsagent.org)
- Google Cloud project with Search Console API enabled (for SEO features)
- CMS credentials for connected systems (WordPress/Strapi/Contentful/Ghost)

---

*Stack analysis: 2026-04-13*