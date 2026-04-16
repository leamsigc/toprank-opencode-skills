# Feature Landscape

**Domain:** Claude Code Plugin Enhancement (SEO + Google Ads)
**Researched:** 2026-04-13
**Project:** Toprank Plugin Enhancement

## Executive Summary

This FEATURES.md documents the feature requirements for enhancing Toprank to be compatible with opencode.ai, use Chrome remote debug for authentication, and integrate chrome-devtools-cli for SEO analysis. Based on ecosystem research, features are categorized as table stakes (essential for viability), differentiators (competitive advantage), and anti-features (deliberately excluded). The research identifies significant architectural differences between Claude Code's JSON manifest plugin format and opencode.ai's TypeScript SDK approach, requiring a dual-format strategy.

## Feature Categories Overview

| Category | Count | Description |
|----------|-------|-------------|
| Table Stakes | 4 | Features users expect; missing = product fails |
| Differentiators | 5 | Features that differentiate from existing solutions |
| Anti-Features | 4 | Features explicitly excluded from scope |

---

## Table Stakes

Features users expect. Without these, the product cannot be considered viable.

### 1. opencode.ai Plugin Compatibility

**Feature:** opencode.ai Plugin Adapter

**Why Expected:** PROJECT.md explicitly targets opencode.ai as the deployment platform. The plugin must work in opencode.ai's environment, not just Claude Code.

**Complexity:** High

**Technical Requirements:**
- Create TypeScript plugin using `@opencode-ai/plugin` SDK
- Export plugin function returning hooks object
- Use Zod schema for tool argument validation
- Place in `.opencode/plugins/` directory or configure in `opencode.json`
- Support context object: `client`, `project`, `directory`, `worktree`, `serverUrl`, `$`

**Implementation Pattern:**
```typescript
import { Plugin, tool } from '@opencode-ai/plugin'
import { z } from 'zod'

export const ToprankPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      'toprank-seo': tool({
        description: 'Run SEO analysis',
        args: {
          url: tool.schema.string().describe('URL to analyze')
        },
        async execute(args, context) {
          // Implementation
        }
      })
    }
  }
}
```

**Dual Compatibility Strategy:**
- Maintain `.claude-plugin/plugin.json` for Claude Code (existing)
- Add `.opencode/` directory with TypeScript plugin for opencode.ai
- Avoids complete rewrite; both formats coexist

**Source:** opencode.ai plugin documentation, SDK API reference (HIGH confidence)

---

### 2. Chrome Remote Debug Auto-Connect

**Feature:** Chrome Remote Debugging Auto-Connect

**Why Expected:** PROJECT.md specifies replacing API key authentication with CDP auto-connect. Manual key management is a known pain point (CONCERNS.md).

**Complexity:** High

**Technical Requirements:**
- Use Chrome DevTools MCP server (`chrome-devtools-mcp`)
- Support `--autoConnect` flag (Chrome 144+) for permission-based connection
- Support `--browserUrl=http://127.0.0.1:9222` for explicit connection
- Configure with dedicated profile `--user-data-dir` to avoid cookie collision
- Handle connection failures gracefully with user-friendly error messages

**Chrome 144+ Auto-Connect Flow:**
1. Navigate to `chrome://inspect/#devices`
2. Enable "Allow remote debugging from this device" toggle
3. MCP server requests connection; user approves once
4. Subsequent connections auto-connect via cached permission

**Explicit Connection Flow:**
1. Launch Chrome with `--remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-debug-profile"`
2. Configure MCP server with `--browserUrl=http://127.0.0.1:9222`
3. No permission dialogs; dedicated profile avoids conflicts

**Source:** Chrome DevTools MCP documentation, Scalified blog (HIGH confidence)

---

### 3. chrome-devtools-cli Integration (Basic)

**Feature:** Headless Browser SEO Analysis

**Why Expected:** CONCERNS.md identifies WebFetch limitations (no JavaScript execution, no interactive features). SEO audits of SPA/SSR sites require real browser rendering.

**Complexity:** Medium

**Technical Requirements:**
- Detect chrome-devtools availability via skill check
- Graceful degradation to WebFetch when CDP unavailable
- Script layer integration: `scripts/chrome_crawl.py` using CDP
- Support `--use-chrome` flag on skills for method selection

**Basic Integration Points:**
1. **Page Fetch:** Replace WebFetch with CDP `Page.navigate` + `Page.loadEventFired`
2. **HTML Extraction:** Use `DOM.getDocument` to extract rendered content
3. **Screenshot:** Use `Page.captureScreenshot` for visual baseline

**Not Included in Table Stakes (defer to differentiators):**
- Performance tracing (Core Web Vitals)
- Visual regression comparison
- Network request analysis

**Source:** CONCERNS.md migration path, Chrome DevTools Protocol docs (MEDIUM confidence)

---

### 4. MCP Tool Naming Compatibility

**Feature:** MCP Server Tool Naming Standardization

**Why Expected:** CONCERNS.md identifies `mcp__adsagent__*` pattern may not work in opencode.ai. Inconsistent tool naming causes invocation failures.

**Complexity:** Low

**Technical Requirements:**
- Verify tool naming format works in both platforms
- Support both standard MCP tool invocation and platform-specific patterns
- Add detection logic to determine available format at runtime

**Formats to Support:**
| Platform | Format Example | Notes |
|----------|----------------|-------|
| Claude Code | `mcp__adsagent__getAccountInfo` | Current double-underscore format |
| opencode.ai | Standard MCP tools via SDK | Platform determines format |
| Fallback | Direct API call | When MCP unavailable |

**Source:** CONCERNS.md MCP compatibility concern (HIGH confidence)

---

## Differentiators

Features that set Toprank apart from existing solutions. Not expected, but valued.

### 5. OAuth 2.0 Authentication via CDP Session

**Feature:** OAuth-Based API Authentication

**Why Expected:** Replaces environment variable API keys with Chrome session authentication. Users authenticate once in browser; plugin inherits authenticated state.

**Complexity:** High

**Value Proposition:**
- No manual API key management
- Uses user's existing Google authentication
- Automatic token refresh via Chrome session
- Aligns with enterprise security standards (CONCERNS.md recommends OAuth)

**Implementation:**
1. User authenticates to Google services via Chrome (once)
2. CDP connection reads cookies/session state
3. Scripts use authenticated session for API calls
4. No environment variables required

**Scope Limitation:** Requires Google services accessible via authenticated browser session; some APIs may still need service account or API key.

**Source:** CONCERNS.md authentication debt, OAuth MCP best practices (MEDIUM confidence)

---

### 6. Chrome Auto-Reconnect on Restart

**Feature:** Resilient Chrome Connection

**Why Expected:** Chrome restarts clear CDP connection. Plugin should automatically restore connection without user intervention.

**Complexity:** Medium

**Value Proposition:**
- Uninterrupted workflow after system restart
- Handles Chrome crashes gracefully
- Reduces "Chrome disconnected" support requests

**Implementation:**
1. Plugin maintains connection state
2. On operation, verify CDP connection active
3. If disconnected, attempt reconnection with exponential backoff
4. Notify user only after max retries exceeded

**Source:** Chrome DevTools operational patterns (LOW confidence - needs validation)

---

### 7. Performance Tracing Integration

**Feature:** Core Web Vitals via CDP

**Why Expected:** SEO analysis benefits from real performance metrics (LCP, INP, CLS). PageSpeed API is a fallback; CDP provides direct browser metrics.

**Complexity:** Medium

**Value Proposition:**
- Real user-centric performance metrics
- No PageSpeed API quota limits
- Detailed waterfall analysis

**CDP Integration:**
```typescript
// Performance tracing via CDP
await client.call('Performance.startTrace')
await client.navigateTo(url)
const metrics = await client.call('Performance.stopTrace')
// Extract LCP, INP, CLS from metrics
```

**Source:** Chrome DevTools performance domains (MEDIUM confidence)

---

### 8. Visual Regression Baseline

**Feature:** Visual Audit Snapshots

**Why Expected:** Enables visual SEO audit (layout shifts, viewport issues) without external screenshot services.

**Complexity:** Medium

**Value Proposition:**
- Detect layout shifts between audits
- Document visual state for reference
- No external service dependencies

**Implementation:**
1. Capture screenshot via `Page.captureScreenshot` on audit URLs
2. Store baseline in `~/.toprank/visual-baseline/`
3. Compare current vs baseline; flag significant differences

**Source:** CONCERNS.md visual audit opportunity (LOW confidence - needs validation)

---

### 9. Network Request Analysis

**Feature:** CDP Network Debugging Integration

**Why Expected:** Analyze blocked resources, CORS issues, and response times directly in SEO audit.

**Complexity:** Low

**Value Proposition:**
- Identify render-blocking requests
- Detect CORS configuration issues
- Measure response times without external tools

**Implementation:**
1. Enable network tracking via CDP
2. Analyze request patterns post-navigation
3. Surface findings in audit report

**Source:** Chrome DevTools network domain (MEDIUM confidence)

---

## Anti-Features

Features to explicitly NOT build. Reasons and alternatives documented.

### Anti-Feature 1: Full Browser Extension

**Why Avoid:** Extension installation adds friction; requires separate installation and permissions flow.

**Alternative:** Use Chrome DevTools MCP (standalone server) which doesn't require extension.

---

### Anti-Feature 2: Multi-Account Chrome Sessions

**Why Avoid:** CONCERNS.md explicitly defers multi-account support as non-priority.

**Alternative:** Single authenticated Chrome session; user switches accounts via browser profile.

---

### Anti-Feature 3: Browser Extension Development Tools

**Why Avoid:** Out of scope per PROJECT.md; focus is SEO analysis, not extension development.

**Alternative:** Provide SEO analysis capabilities; leave extension debugging to existing tools.

---

### Anti-Feature 4: Continuous Screenshot Recording

**Why Avoid:** Storage and privacy concerns; audit snapshots (occasional) sufficient.

**Alternative:** On-demand screenshots via skill trigger; visual baseline comparison.

---

## Feature Dependencies

```
Feature 1 (opencode.ai Plugin)
  └─ Feature 4 (MCP Tool Naming) — must align for tools to invoke correctly

Feature 2 (Chrome Remote Debug)
  └─ Feature 6 (Auto-Reconnect) — depends on connection state management
  └─ Feature 5 (OAuth via CDP) — uses authenticated session
  └─ Feature 3 (chrome-devtools Integration) — requires CDP access

Feature 3 (chrome-devtools Basic)
  └─ Feature 7 (Performance Tracing) — uses CDP Performance domain
  └─ Feature 8 (Visual Regression) — uses CDP screenshot
  └─ Feature 9 (Network Analysis) — uses CDP Network domain
```

**Dependency Notes:**
- Each layer builds on the previous
- Graceful degradation: if Feature 2 fails, fall back to current API key approach
- Feature 3 is foundational for Features 7-9 (differentiators)

---

## MVP Recommendation

For initial release, prioritize:

### Must Have (Phase 1)
1. **Feature 1:** opencode.ai plugin adapter (TypeScript SDK)
2. **Feature 4:** MCP tool naming compatibility
3. **Feature 2:** Chrome remote debug with explicit connection (--browserUrl)

### Should Have (Phase 2)
4. **Feature 3:** Basic chrome-devtools integration (page fetch + HTML extraction)
5. **Feature 6:** Auto-reconnect handling

### Can Have (Phase 3)
6. **Feature 5:** OAuth via CDP session
7. **Feature 7:** Performance tracing
8. **Feature 8:** Visual baseline

### Defer
- **Feature 9:** Network analysis (low priority vs effort)
- Multi-account support (explicitly out of scope)

---

## Complexity Assessment

| Feature | Complexity | Risk | Validation Required |
|---------|------------|------|---------------------|
| opencode.ai adapter | High | Medium | Test actual plugin loading |
| Chrome remote debug | High | High | Connection reliability varies by Chrome version |
| chrome-devtools basic | Medium | Low | Well-documented CDP |
| MCP tool naming | Low | Low | Format testing |
| OAuth via CDP | High | Medium | Not all APIs accessible via browser |
| Auto-reconnect | Medium | Low | Standard error handling |
| Performance tracing | Medium | Low | Well-documented CDP |
| Visual regression | Medium | Medium | Storage management |
| Network analysis | Low | Low | CDP documentation |

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| opencode.ai requirements | HIGH | Official SDK documentation |
| Chrome remote debug | HIGH | Official MCP docs, verified working |
| chrome-devtools integration | MEDIUM | CDP comprehensive; skill integration untested |
| MCP tool compatibility | HIGH | Known concern from CONCERNS.md |
| OAuth via CDP | MEDIUM | Theory sound; implementation needs research |
| Visual regression | LOW | Proposed feature; no existing pattern |

---

## Sources

### Primary Sources (HIGH Confidence)
- opencode.ai Plugin SDK: https://opencode.ai/docs/plugins
- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp
- Claude Code plugin manifest: https://docs.anthropic.com/en/docs/claude-code/plugins-reference

### Secondary Sources (MEDIUM Confidence)
- CDP authentication patterns: https://developer.chrome.com/docs/devtools/protocol-monitor
- Chrome auto-connect: Scalified blog (2026-02-23)
- OAuth in MCP: https://paiml.github.io/rust-mcp-sdk/course/part5-security/ch13-01-why-oauth.html

### Local Context (HIGH Confidence)
- PROJECT.md (features explicitly targeted)
- CONCERNS.md (technical debt, migration path)
- ARCHITECTURE.md (current implementation)

---

*Research completed: 2026-04-13*