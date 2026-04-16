# Requirements: Toprank Plugin Enhancement

## v1 Requirements

### Platform Compatibility

- [ ] **REQ-PC-01**: Create `.opencode/` directory with opencode.ai plugin structure
- [ ] **REQ-PC-02**: Implement TypeScript plugin using `@opencode-ai/plugin` SDK
- [ ] **REQ-PC-03**: Add dual-format coexistence (`.claude-plugin/` + `.opencode/`)
- [ ] **REQ-PC-04**: Verify MCP tool naming (`mcp__adsagent__*`) compatibility

### Chrome Integration

- [ ] **REQ-CH-01**: Configure chrome-devtools-mcp in `opencode.json` or `.mcp.json`
- [ ] **REQ-CH-02**: Add Chrome remote debug detection (`--remote-debugging-port=9222`)
- [ ] **REQ-CH-03**: Implement CDP session reuse for authenticated Google APIs
- [ ] **REQ-CH-04**: Add fallback to env vars when Chrome not available
- [ ] **REQ-CH-05**: Handle Chrome 136+ `--user-data-dir` requirement

### SEO Enhancement

- [ ] **REQ-SE-01**: Refactor seo-analysis to use chrome-devtools instead of WebFetch
- [ ] **REQ-SE-02**: Add JavaScript rendering detection for SPA/SSR sites
- [ ] **REQ-SE-03**: Implement headless browser page audit capability

### Testing

- [ ] **REQ-TEST-01**: Test plugin loading in opencode.ai environment
- [ ] **REQ-TEST-02**: Verify MCP tool invocation works
- [ ] **REQ-TEST-03**: Test Chrome remote debug auto-connect flow

---

## v2 Requirements (Deferred)

- [ ] **REQ-V2-01**: OAuth scope via CDP for Google APIs (requires Phase 2 validation)
- [ ] **REQ-V2-02**: Performance tracing via CDP
- [ ] **REQ-V2-03**: Visual baseline/regression testing
- [ ] **REQ-V2-04**: Network request analysis for SEO
- [ ] **REQ-V2-05**: Remove gcloud CLI dependency (requires OAuth via CDP)

---

## Out of Scope

- [Full skill rewrite] — Keep existing SKILL.md format, adapt for opencode
- [Add new SEO features beyond chrome-devtools integration] — Future phase
- [Direct Google Ads API fallback] — Low priority, MCP works
- [Offline mode] — Not in scope for this project

---

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| REQ-PC-01 | 1 - opencode.ai Plugin Compatibility | ✓ Complete |
| REQ-PC-02 | 1 - opencode.ai Plugin Compatibility | ✓ Complete |
| REQ-PC-03 | 1 - opencode.ai Plugin Compatibility | ✓ Complete |
| REQ-PC-04 | 1 - opencode.ai Plugin Compatibility | ✓ Complete |
| REQ-CH-01 | 2 - Chrome Remote Debug Authentication | ✓ Complete |
| REQ-CH-02 | 2 - Chrome Remote Debug Authentication | ✓ Complete |
| REQ-CH-03 | 2 - Chrome Remote Debug Authentication | ✓ Complete |
| REQ-CH-04 | 2 - Chrome Remote Debug Authentication | ✓ Complete |
| REQ-CH-05 | 2 - Chrome Remote Debug Authentication | ✓ Complete |
| REQ-SE-01 | 4 - chrome-devtools-mcp Integration | Pending (Gap Closure) |
| REQ-SE-02 | 4 - chrome-devtools-mcp Integration | Pending (Gap Closure) |
| REQ-SE-03 | 4 - chrome-devtools-mcp Integration | Pending (Gap Closure) |
| REQ-TEST-03 | 2 - Chrome Remote Debug Authentication | ✓ Complete |

---

*Requirements defined: 2026-04-13*