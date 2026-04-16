# Architecture Research: Toprank Plugin Enhancement

**Research Date:** 2026-04-13
**Domain:** Plugin Architecture Integration
**Confidence:** MEDIUM

## Executive Summary

This research addresses integrating Toprank with three new capabilities: opencode.ai plugin compatibility, chrome-devtools-cli integration, and Chrome remote debug authentication. The existing Claude Code plugin architecture provides a strong foundation, but requires strategic adaptation for OpenCode's different extensibility model.

**Key Finding:** OpenCode uses a three-tier extensibility system (skills → agents → plugins) where Claude Code uses a single plugin format. Toprank's skill-based architecture maps well, but requires converting `.claude-plugin/plugin.json` declarations into individual `SKILL.md` files with OpenCode-compatible frontmatter.

## Architecture Comparison

### Claude Code vs OpenCode Architecture

| Dimension | Claude Code | OpenCode |
|-----------|-------------|----------|
| **Plugin Format** | `.claude-plugin/plugin.json` + folder skills | `.opencode/skills/*/SKILL.md` + npm plugins |
| **Skill Discovery** | Explicit registry in plugin.json | Path-based discovery + permissions config |
| **MCP Integration** | `.mcp.json` + `mcp__*` tool namespace | Plugins provide tools via `@opencode-ai/plugin` SDK |
| **Tool Naming** | `mcp__server__tool` | Plugin-provided tools (no prefix) |

### Current Toprank Architecture

```
toprank/
├── .claude-plugin/
│   ├── plugin.json           # Skill registry (explicit paths)
│   └── marketplace.json     # Registry metadata
├── .mcp.json                # MCP server config (AdsAgent)
├── google-ads/              # Category with 3 skills
│   ├── shared/preamble.md   # Bootstrapping
│   ├── ads/SKILL.md
│   ├── ads-audit/SKILL.md
│   └── ads-copy/SKILL.md
└── seo/                     # Category with 7 skills
    ├── shared/preamble.md
    ├── seo-analysis/SKILL.md
    └── ... (6 more skills)
```

### Target OpenCode Architecture

```
toprank/
├── SKILL.md                 # Root skill for category routing
├── google-ads/
│   ├── SKILL.md             # Google Ads category skill
│   ├── ads/SKILL.md         # Individual skill
│   ├── ads-audit/SKILL.md
│   └── ads-copy/SKILL.md
├── seo/
│   ├── SKILL.md             # SEO category skill
│   ├── seo-analysis/SKILL.md
│   └── ... (6 more)
├── .opencode/
│   └── plugins/
│       └── toprank.ts       # Optional: plugin for MCP/tools
└── .mcp.json                # Keep for MCP compatibility
```

## Component Boundaries

### Layer 1: Skill Layer (Unchanged)

**Responsibility:** Individual skill workflows
**Location:** `*/<skill-name>/SKILL.md`
**Boundaries:**
- Each skill is self-contained with its own references/, scripts/, evals/
- Category-level shared/ provides bootstrapping via preamble.md
- Skills execute scripts via Bash tool or call MCP tools

**Data Flow:**
```
User invocation → Skill SKILL.md → shared/preamble.md → script execution / MCP tools
```

### Layer 2: Plugin Infrastructure (Migrates to OpenCode)

**Responsibility:** Skill discovery, MCP configuration
**Current:** `.claude-plugin/plugin.json`
**Target:** Convert to `.opencode/skills/*/SKILL.md` with YAML frontmatter

**Migration Pattern:**
```yaml
---
name: toprank-seo-analysis
description: Full SEO audit with GSC, PageSpeed, CMS detection
license: MIT
compatibility: opencode, claude
---
```

### Layer 3: MCP Integration (Enhanced with CDP)

**Current:** AdsAgent MCP via `.mcp.json`
**Enhanced:** Add chrome-devtools-mcp for CDP-based SEO analysis

```json
{
  "mcpServers": {
    "adsagent": {
      "command": "npx",
      "args": ["-y", "adsagent-mcp@latest"]
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--headless"]
    }
  }
}
```

## Chrome DevTools Integration Architecture

### Option 1: chrome-devtools-mcp (Recommended)

**Architecture:**
```
Toprank Skill → chrome-devtools-mcp → CDP WebSocket → Chrome Browser
```

**Component Responsibilities:**
| Component | Responsibility | Connection |
|-----------|---------------|------------|
| `chrome-devtools-mcp` | MCP server wrapper | Exposes CDP as MCP tools |
| CDP Protocol | 53 domains, 644 methods | WebSocket JSON-RPC |
| Chrome Browser | Execution target | `--remote-debugging-port=9222` |

**Integration Path:**
1. Add chrome-devtools-mcp to `.mcp.json`
2. Skills call CDP tools via MCP: `mcp__chrome-devtools__*`
3. Use for: JavaScript rendering, visual analysis, network interception

### Option 2: chrome-devtools-cli (Alternative)

**Architecture:**
```
Toprank Script → chrome-devtools CLI → CDP → Chrome
```

**Use Case:** When MCP not available, fall back to CLI execution

```python
# seo-analysis/scripts/cdp_fetch.py
import subprocess
result = subprocess.run([
    'chrome-devtools', 'network', 'list-requests',
    '--url', target_url, '--format', 'json'
], capture_output=True)
```

## Chrome Remote Debug Authentication Architecture

### Authentication Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Toprank Skill  │────▶│  Config Resolver │────▶│ Chrome Remote   │
└─────────────────┘     └──────────────────┘     │ Debug Endpoint  │
                          │                       └─────────────────┘
                          ▼                              │
                   ┌──────────────────┐                  │
                   │ Preamble Check   │                  │
                   │ - CDP available? │                  │
                   │ - Auth required? │                  │
                   └──────────────────┘                  │
                          │                              ▼
                   ┌──────────────────┐◀───── HTTP /json/version
                   │ Fallback: env    │        (returns WebSocket URL)
                   │ vars API key     │
                   └──────────────────┘
```

### Implementation

**Step 1: Chrome Launch with Remote Debugging**
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=~/.toprank/chrome-data
```

**Step 2: Detect CDP Availability**
```python
# bin/cdp-detect
#!/bin/bash
curl -s http://localhost:9222/json/version | jq -r '.webSocketDebuggerUrl'
```

**Step 3: Auth Flow**
```javascript
// CDP auth for protected resources
client.send('Fetch.enable', { handleAuthRequests: true })
client.on('Fetch.authRequired', (params) => {
  client.send('Fetch.continueWithAuth', {
    interceptionId: params.interceptionId,
    authChallengeResponse: { username, password }
  })
})
```

### Replace API Key with CDP Auth

**Current (env var):**
```bash
export GOOGLE_ADS_API_KEY="..."
# AdsAgent reads from environment
```

**Target (CDP auto-connect):**
```yaml
# preamble.md
1. Check if Chrome running with remote debugging
2. If available → use CDP for auth (no API key needed)
3. If not → fallback to env var API key
```

## Data Flow Architecture

### Skill Invocation Flow (Enhanced)

```
1. User invokes /toprank:seo-analysis
2. OpenCode loads .opencode/skills/seo/seo-analysis/SKILL.md
3. Skill reads seo/shared/preamble.md
4. Preamble performs:
   a. CDP detection (curl localhost:9222/json/version)
   b. MCP server detection
   c. Config resolution (merge project + global)
   d. Onboarding if needed
5. Skill executes workflow:
   a. If CDP available → use chrome-devtools-mcp for JS rendering
   b. Else → use gcloud CLI / WebFetch
   c. Call MCP tools if available
   d. Execute Python scripts for analysis
6. Results streamed to user
```

### External API Integration (Enhanced)

| Service | Current | Enhanced |
|---------|---------|----------|
| Google Ads | AdsAgent MCP | Keep MCP, add CDP fallback |
| Search Console | gcloud CLI | CDP network interception |
| PageSpeed API | Direct API | Keep direct API |
| CMS | Direct API | Keep direct API |
| SEO Rendering | WebFetch | **CDP for JS-heavy sites** |

## Build Order Recommendations

### Phase 1: OpenCode Compatibility

1. Convert `.claude-plugin/plugin.json` to individual `SKILL.md` files
2. Add OpenCode frontmatter to each skill
3. Test skill discovery in OpenCode

**Dependencies:** None (foundational)
**Risk:** Low

### Phase 2: MCP Enhancement

1. Add chrome-devtools-mcp to `.mcp.json`
2. Create CDP-based SEO scripts in `seo/seo-analysis/scripts/`
3. Test MCP tool availability in skills

**Dependencies:** Phase 1
**Risk:** Medium (new MCP dependency)

### Phase 3: Chrome Remote Debug Auth

1. Create CDP detection script in `bin/`
2. Modify preamble.md to check CDP availability
3. Add fallback logic: CDP → env vars
4. Test auth flow

**Dependencies:** Phase 2
**Risk:** Medium (changes auth pattern)

### Phase 4: Script Migration

1. Migrate Python scripts to use CDP when available
2. Keep gcloud as fallback
3. Document new CDP-based workflow

**Dependencies:** Phase 3
**Risk:** Low (enhancement)

## Component Communication Matrix

| From | To | Protocol | Purpose |
|------|-----|----------|---------|
| Skill SKILL.md | shared/preamble.md | File include | Bootstrapping |
| Preamble | bin/toprank-config | CLI | Config read/write |
| Preamble | bin/cdp-detect | CLI | CDP availability |
| Skill | MCP tools | JSON-RPC | External APIs |
| Skill | Python scripts | stdout/stderr | Data collection |
| Skill | chrome-devtools-mcp | MCP protocol | CDP operations |

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Instead |
|-------------|---------|---------|
| Hardcoded MCP tool names | Breaks in OpenCode (different namespace) | Use dynamic tool discovery |
| Block on MCP unavailable | Kills UX when MCP fails | Graceful degradation with fallback |
| CDP as required dependency | Browser may not be available | Always fallback to env vars/API |
| Skip preamble execution | Loses config resolution | Always execute preamble first |

## Scalability Considerations

| Scale | CDP Strategy | MCP Strategy |
|-------|--------------|--------------|
| Single user, local Chrome | Direct connection | Local MCP server |
| Team, shared Chrome | Remote debugging (port forwarding) | Team MCP server |
| CI/CD | Headless Chrome | Mock/overridden MCP |

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| OpenCode architecture | MEDIUM | Docs confirm skill/plugin model, but no direct plugin.json migration guide |
| chrome-devtools-mcp | HIGH | Official Google npm package, well documented |
| Chrome remote debug auth | HIGH | Standard CDP pattern, documented in Puppeteer/playwright |
| Integration approach | MEDIUM | Theoretical integration, needs phase validation |

## Gaps to Address

- OpenCode skill permission system requires testing
- MCP vs CDP performance comparison for SEO rendering
- Chrome remote debug on different OS platforms (Linux specific testing)
- opencode-agent-skills plugin for dynamic skill loading

---

*Research complete: 2026-04-13*