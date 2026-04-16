# Stack Research

**Domain:** Claude Code Plugin Enhancement for opencode.ai compatibility and Chrome DevTools integration
**Researched:** 2026-04-13
**Confidence:** MEDIUM

## Executive Summary

Toprank plugin requires three major stack changes:

1. **opencode.ai plugin format** — Not JSON-based like Claude Code. Requires JavaScript/TypeScript plugin using `@opencode-ai/plugin` package with hooks-based architecture, not skill-based.

2. **chrome-devtools-cli** — Use `chrome-devtools-mcp` (Google's official) which now includes a CLI interface, not the legacy skill format.

3. **Chrome remote debug auth** — CDP pattern using raw WebSocket connection to reuse authenticated sessions without OAuth flows.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `@opencode-ai/plugin` | latest | Plugin SDK for opencode.ai | Required for opencode.ai plugin compatibility. Defines `Plugin` type, `tool()` helper, event hooks. |
| `chrome-devtools-mcp` | latest | Chrome DevTools Protocol CLI + MCP | Google's official implementation (33K+ stars). Includes both MCP server and CLI interface. Replaces skill-based approach. |
| `websockets` | ^14.0 | Raw CDP WebSocket connection | Minimal dependency for Chrome remote debug auth. ~100KB vs 50MB for Playwright. |
| `rookiepy` | latest | Browser cookie extraction | Cross-browser (Chrome, Firefox, Edge). Extract cookies without CDP connection. |
| `zod` | ^3.23 | Schema validation for tool args | Required by `@opencode-ai/plugin` tool schema. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `puppeteer` | ^23.0 | Browser automation fallback | When chrome-devtools-mcp unavailable or need custom CDP handling |
| `selenium-webdriver` | ^4.20 | Alternative automation | Cross-browser testing with CDP fallback |
| `playwright` | ^1.50 | Legacy MCP integration | Only if existing AdsAgent MCP requires it |
| `googleapis` | ^140.0 | Direct Google API fallback | When MCP unavailable and direct API needed |

### Development Tools

| Tool | Purpose | Notes |
|------|--------|-------|
| `bun` | Package manager | opencode.ai uses bun for plugin dependencies. Run `bun install` at startup. |
| `typescript` | Type-safe plugins | Recommended for plugin development |
| `npx` | Run MCP servers | For testing MCP integration |

## Installation

```bash
# Core dependencies for opencode.ai plugin
cd .opencode/plugins/toprank
bun init
bun add @opencode-ai/plugin zod

# Chrome DevTools CLI (for headless browser)
npm install -g chrome-devtools-mcp

# For authentication (Python option)
pip install websockets rookiepy

# For direct Google API fallback (if needed)
pip install googleapis google-auth-oauthlib
```

## opencode.ai Plugin Architecture

### Key Differences from Claude Code

| Aspect | Claude Code | opencode.ai |
|--------|------------|------------|
| Format | JSON (`plugin.json`) | JavaScript/TypeScript |
| Skills | `.claude/skills/*` | `.opencode/tools/*` or custom tools |
| MCP | `.mcp.json` | `mcp` field in `opencode.json` |
| Invocation | `/skill-name` | Custom tools via `tool()` |

### Plugin Structure for Toprank

```
.opencode/
├── plugins/
│   └── toprank/
│       ├── index.ts              # Main plugin entry
│       ├── package.json        # Dependencies
│       └── tools/
│           ├── seo-tool.ts     # SEO analysis tool
│           ├── ads-tool.ts     # Google Ads tool
│           └── chrome-tool.ts  # Chrome DevTools integration
├── tools/                     # Project-level custom tools
│   └── toprank/
└── opencode.json               # Plugin + MCP config
```

### Minimal Plugin Example

```typescript
// .opencode/plugins/toprank/index.ts
import { tool, type Plugin } from "@opencode-ai/plugin"
import { z } from "zod"

export const ToprankPlugin: Plugin = async ({ project, client, $, directory }) => {
  return {
    tool: {
      toprank_seo_audit: tool({
        description: "Run comprehensive SEO audit",
        args: {
          url: tool.schema.string().describe("URL to audit"),
          useChrome: tool.schema.boolean().default(false).describe("Use headless Chrome"),
        },
        async execute(args, context) {
          // Implementation
          const result = args.useChrome
            ? await $(`chrome-devtools navigate ${args.url}`)
            : await fetch(args.url)
          return result
        },
      }),
    },
  }
}
```

## chrome-devtools-cli Integration

### chrome-devtools-mcp CLI (Recommended)

Install globally:
```bash
npm install -g chrome-devtools-mcp
```

Usage:
```bash
chrome-devtools navigate_page --type url --url "https://example.com"
chrome-devtools take_snapshot
chrome-devtools lighthouse_audit --mode navigation
```

### CDP Connection from Plugin

```typescript
// Connect to running Chrome via WebSocket
const ws = new WebSocket('ws://127.0.0.1:9222/devtools/browser');

// Or via chrome-devtools-mcp CLI
const result = await $`chrome-devtools navigate_page --type url --url "${url}"`;
```

### Installation Prerequisites

Chrome must run with remote debugging:
```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

## Chrome Remote Debug Auth

### Method 1: CDP Session Reuse (Recommended)

Connect to existing Chrome session for authenticated access:

```python
import asyncio
import websockets

async def get_chrome_cookies(port: int = 9222) -> dict:
    """Extract cookies from running Chrome via CDP."""
    async with websockets.connect(f'ws://127.0.0.1:{port}/devtools/browser') as ws:
        # Get targets
        await ws.send('{"id":1,"method":"Target.getTargets"}')
        response = json.loads(await ws.recv())
        
        # Navigate to get cookies
        target_id = response['result']['targetInfos'][0]['targetId']
        await ws.send(json.dumps({
            "id": 2,
            "method": "Network.getCookies",
            "params": {"domain": ".google.com"}
        }))
        result = json.loads(await ws.recv())
        return result['result']['cookies']
```

### Method 2: Cookie File Extraction (No CDP Required)

Use `rookiepy` to extract browser cookies:

```python
from rookiepy import chrome

# Extract cookies from default Chrome profile
cookies = chrome()
google_cookies = [c for c in cookies if 'google.com' in c['domain']]

# Save as JSON for later use
import json
with open('storage_state.json', 'w') as f:
    json.dump(google_cookies, f)
```

### Method 3: Extension-Based Auth

Build lightweight extension for cookie injection. Higher effort but works with Chrome settings toggle (Chrome 146+).

### Comparison

| Method | Dependencies | Auth Reuse | Effort | Security |
|--------|-------------|------------|--------|----------|
| CDP Session | `websockets` (~100KB) | Yes | Low | Local port exposure |
| Cookie File | `rookiepy` (~1MB) | Manual export | Low | No port exposure |
| Extension | Extension + native | Yes | High | Chrome 146+ toggle |
| Playwright | ~50MB | Via context | Medium | Isolated |

**Recommendation:** Use CDP session for primary auth (reuse existing Chrome), cookie file as offline fallback.

## MCP Server Integration

### For opencode.ai

```json
// opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "chrome-devtools": {
        "command": "npx",
        "args": ["-y", "chrome-devtools-mcp@latest"]
      }
    },
    "adsagent": {
      "command": "npx",
      "args": ["-y", "adsagent-mcp@latest"],
      "env": {
        "ADSAGENT_API_KEY": "${ADSAGENT_API_KEY}"
      }
    }
  }
}
```

### For Claude Code (Preserve)

```json
// .mcp.json - Keep for Claude Code compatibility
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "adsagent": {
      "command": "npx", 
      "args": ["-y", "@nowork-studio/adsagent-mcp"],
      "env": {
        "ADSAGENT_API_KEY": "${ADSAGENT_API_KEY}"
      }
    }
  }
}
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|--------------|--------------|--------------------------|
| chrome-devtools-mcp | agent-browser | Rust binary, faster startup, similar features |
| chrome-devtools-mcp | playwright MCP | If already invested in Playwright ecosystem |
| CDP session | rookiepy | When can't start Chrome with debugging port |
| CDP session | Extension auth | Chrome 146+ with native settings toggle |
| No local MCP | Direct googleapis | When offline mode critical |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|------------|
| Claude Code `plugin.json` format | Incompatible with opencode.ai | JavaScript/TypeScript plugin |
| Skill-based chrome-devtools | Legacy format, CLI available | `chrome-devtools-mcp` CLI |
| Environment variable auth alone | No session reuse, manual rotation | CDP session reuse |
| Playwright for auth only | 50MB dependency waste | Raw CDP + websockets |
| MCP `mcp__adsagent__*` tool names | Double underscore may not work | Test and adapt to opencode.ai format |

## Stack Patterns by Variant

**If targeting opencode.ai only:**
- Build full JavaScript/TypeScript plugin architecture
- Use `@opencode-ai/plugin` for all custom tools
- Configure MCP servers in `opencode.json`

**If targeting both Claude Code AND opencode.ai:**
- Maintain dual format: JSON skills + JS plugin bridge
- Create wrapper plugin that loads Claude Code skills
- Test MCP tool naming in both environments

**If Chrome auth is priority:**
- Use CDP session for active sessions
- Cookie file as offline backup
- Document both approaches in skill/SKILL.md

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `@opencode-ai/plugin` | opencode.ai ^1.0 | Check `engines` field in npm |
| `chrome-devtools-mcp` | Chrome 80+ | CDP protocol stable |
| `websockets` | Python 3.8+ | Async i/o required |
| `rookiepy` | Chrome/Firefox/Edge | Platform-specific keyring deps |
| `googleapis` | Python 3.8+ | OAuth flow complexity |

## Sources

- opencode.ai plugins documentation: https://opencode.ai/docs/plugins — HIGH (official)
- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp — HIGH (official, 33K stars)
- opencode.ai config schema: https://opencode.ai/docs/config — HIGH (official)
- CDP pattern for auth: https://dev.to/timtech4u/your-browser-has-a-remote-control — MEDIUM (technical blog)
- rookiepy for cookies: https://github.com/RoookieTeam/rookiepy — MEDIUM (community)

---

*Stack research for: Toprank plugin stack*
*Researched: 2026-04-13*