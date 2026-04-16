# Pitfalls Research

**Domain:** Claude Code Plugin Enhancement (opencode.ai compatibility, Chrome DevTools integration, remote debug authentication)
**Researched:** 2026-04-13
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: opencode.ai Hardcoded Plugin Skip Block

**What goes wrong:**
Toprank plugin fails to load silently in opencode.ai because its name or path contains "opencode-openai-codex-auth" substring — this triggers a hardcoded skip in opencode's plugin loader (`packages/opencode/src/plugin/index.ts`).

**Why it happens:**
OpenCode uses broad substring matching (`plugin.includes("opencode-openai-codex-auth")`) instead of exact package ID matching. Any plugin with that substring in its name or path gets silently blocked without warning.

**How to avoid:**
- Avoid plugin names containing "opencode-openai-codex-auth" or "opencode-copilot-auth"
- Use `file://` paths that don't contain these substrings
- Test plugin loading with `opencode --verbose` to verify

**Warning signs:**
- Plugin doesn't appear in loaded plugins list
- No error or warning about skipped plugin
- Works in Claude Code but not opencode.ai

**Phase to address:** Phase 1: opencode.ai Plugin Compatibility

---

### Pitfall 2: ESM Import .js Extension Missing

**What goes wrong:**
Plugin fails to load in opencode.ai with module resolution errors because `@opencode-ai/plugin` imports lack `.js` extensions in published npm packages.

**Why it happens:**
- `package.json` exports point to `./src/index.ts` but only `dist/` is published
- Compiled `dist/index.js` has `export * from "./tool"` without `.js` extension
- ESM module resolution fails in Node.js without extensions

**How to avoid:**
- Use local plugin development instead of npm publish during testing
- Create `package.json` in config directory with local dependencies
- Use file:// plugin paths to bypass npm resolution

**Warning signs:**
- `Error [ERR_MODULE_NOT_FOUND]: Cannot find module`
- Plugin loads in Claude Code but fails in opencode.ai
- Check with `opencode --verbose`

**Phase to address:** Phase 1: opencode.ai Plugin Compatibility

---

### Pitfall 3: MCP Tool Naming Convention Mismatch

**What goes wrong:**
Toprank's current `mcp__adsagent__*` tool naming convention may not work correctly in opencode.ai, causing MCP tool calls to fail or be unrecognized.

**Why it happens:**
- opencode.ai uses `mcp__` prefix but constructs names differently (e.g., `adsagent__getAccountInfo` vs `mcp__adsagent__getAccountInfo`)
- Tool names exceeding 64 characters cause issues
- opencode.ai prefixes MCP server name to tool names automatically

**How to avoid:**
- Verify tool naming in opencode.ai vs Claude Code
- Use opencode.ai's MCP configuration instead of `.mcp.json`
- Test MCP tool calls in both environments

**Warning signs:**
- MCP tools appear but calls fail with "tool not found"
- Tool names appear duplicated (e.g., `brave_brave_web_search`)
- Check with `opencode mcp list`

**Phase to address:** Phase 1: opencode.ai Plugin Compatibility

---

### Pitfall 4: Chrome Remote Debug Port Requires --user-data-dir (Chrome 136+)

**What goes wrong:**
Chrome ignores `--remote-debugging-port` flag if `--user-data-dir` is not also specified, breaking existing automation workflows that only set the debug port.

**Why it happens:**
Chrome 136+ security change: remote debugging port no longer works with default Chrome profile to prevent cookie theft by malicious local processes.

**How to avoid:**
- Always use `--user-data-dir=/path/to/profile` alongside `--remote-debugging-port=9222`
- Use isolated/development profile specifically for automation
- Never use default profile for remote debugging

**Warning signs:**
- "Could not find DevToolsActivePort" error
- Chrome starts but debugging port not available
- Security: any local process can connect to debugging port

**Phase to address:** Phase 2: Chrome Remote Debug Authentication

---

### Pitfall 5: Chrome Permission Dialog on Every Connection (autoConnect)

**What goes wrong:**
Using `--autoConnect` with Chrome 144+ triggers a permission dialog on every new connection, blocking automated agent workflows.

**Why it happens:**
Chrome enforces explicit user consent for remote debugging connections to prevent silent browser control. No "remember this choice" option exists for MCP connections.

**How to avoid:**
- Use manual `--browserUrl` connection instead of `--autoConnect` for persistent sessions
- Launch Chrome manually with remote debugging and keep it running
- Configure MCP server with `--browserUrl=http://127.0.0.1:9222` pointing to persistent Chrome instance

**Warning signs:**
- "Allow remote debugging?" dialog appears during automated operations
- Repeated approval prompts in long-running sessions
- Use `--autoConnect` only for short-lived sessions

**Phase to address:** Phase 2: Chrome Remote Debug Authentication

---

### Pitfall 6: Long-Running MCP Sessions Lose Chrome Connection

**What goes wrong:**
MCP server restarts repeatedly in long-running sessions, causing connection churn and triggering repeated Chrome approval prompts.

**Why it happens:**
- MCP client (opencode.ai) controls MCP server lifecycle
- Connection drops but reconnection logic isn't stable
- No persistent browser websocket reuse in server lifecycle

**How to avoid:**
- Use fixed `--browserUrl` instead of `--autoConnect` for stability
- Keep Chrome running externally and reuse connection
- Monitor logs for repeated "Starting Chrome DevTools MCP Server" messages

**Warning signs:**
- Connection errors during otherwise healthy Chrome debugging
- `/tmp/chrome-devtools-mcp.log` shows repeated startup entries
- Reconnect churn triggers Chrome approval prompts

**Phase to address:** Phase 3: chrome-devtools-cli Integration

---

### Pitfall 7: chrome-devtools-mcp Node.js Version Incompatibility

**What goes wrong:**
chrome-devtools-mcp installs successfully but tools fail silently due to Node.js version mismatch.

**Why it happens:**
- chrome-devtools-mcp requires Node.js v20.19+ (latest LTS)
- MCP clients spawn via `child_process.spawn()` without loading user shell profile
- nvm-windows PATH shimming doesn't work with spawn()

**How to avoid:**
- Use absolute paths to node.exe instead of `npx` in MCP config
- Install globally and reference absolute path: `command: "/path/to/node"`, `args: ["/path/to/bin/chrome-devtools-mcp"]`
- Verify with `node --version` in terminal vs what MCP spawn uses

**Warning signs:**
- `npx` MCP servers fail while `.exe` MCP servers work
- No error output at all (silent failure)
- Check Node version: `npx chrome-devtools-mcp@latest --help`

**Phase to address:** Phase 3: chrome-devtools-cli Integration

---

### Pitfall 8: Chrome DevTools "Target Closed" Error

**What goes wrong:**
Browser immediately closes after MCP server starts, causing "Target closed" error on any tool call.

**Why it happens:**
- Chrome already running in background
- Corrupted browser profile in user-data-dir
- Insufficient system permissions to launch Chrome
- Chrome installed via snap or in sandboxed environment

**How to avoid:**
- Close all Chrome instances before MCP server starts
- Clear corrupted profile cache: `rm -rf ~/.cache/chrome-devtools-mcp/`
- Use `--isolated=true` to avoid profile conflicts
- Install Chrome from official渠道, not snap

**Warning signs:**
- "Target closed" error immediately after any tool call
- Chrome process not visible but profile locked
- Works on some machines but not others

**Phase to address:** Phase 3: chrome-devtools-cli Integration

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Use npx in MCP config | Simpler config, auto-install | Breaks on Windows with nvm-windows; silent failures | Never - use absolute paths |
| Skip --user-data-dir in Chrome launch | Simpler command | Chrome 136+ ignores --remote-debugging-port entirely | Never |
| Use --autoConnect for persistent sessions | Auto-discovers Chrome | Repeated permission prompts in long sessions; connection churn | Only for short-lived sessions |
| Use default Chrome profile for debugging | No profile setup needed | Security risk: any local process can access cookies/tokens | Never |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| opencode.ai plugin | Using .claude-plugin format unchanged | Create opencode/ directory with opencode-plugin.json; test with file:// paths |
| MCP servers | Using .mcp.json instead of opencode.json | Use opencode.ai's native mcp config; different naming convention |
| chrome-devtools-mcp | Using npx in command | Use absolute path to node + chrome-devtools-mcp binary |
| Chrome remote debug | Omitting --user-data-dir | Always use with --user-data-dir in Chrome 136+ |
| autoConnect session | Expecting persistent connection | Use --browserUrl to existing Chrome for stability |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Repeated MCP server restarts | Connection errors in long sessions; repeated Chrome approval prompts | Use --browserUrl to persistent Chrome instead of --autoConnect | After 10-30 minutes of idle time |
| Sequential page fetching in SEO audit | Slow audits when crawling multiple pages | Use chrome-devtools parallel tool calls | At >20 pages |
| GSC data re-fetched every invocation | Slow repeated audits; quota consumption | Cache GSC data with TTL in ~/.toprank/cache/ | After 3+ invocations |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Use default Chrome profile for remote debug | Any local process can extract cookies/tokens, hijack sessions | Always use isolated --user-data-dir |
| Expose remote debugging port without firewall | Malicious local apps can control browser | Use only on trusted machines; avoid in shared environments |
| Store API keys in environment variables visible in process listings | Credential exposure via process inspection | Use secret managers; encrypt at rest |
| Connect to remote debug port without authentication | Anyone on network can control browser | Use localhost only; Chrome 144+ autoConnect includes consent dialog |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Silent plugin skip in opencode.ai | Plugin doesn't work, no explanation | Test with `opencode --verbose` and check logs |
| Chrome permission dialog in automation | Blocks agent workflows, requires human intervention | Use --browserUrl to pre-launched Chrome instead of --autoConnect |
| npm dependency resolution failure in .opencode/plugin/ subdirectory | Plugin loads but tools fail | Use local plugin with file:// path; create package.json in config dir |
| Duplicate plugin loading | Event handlers fire twice, confusing behavior | Use singleton pattern or check `opencode debug config` |

---

## "Looks Done But Isn't" Checklist

- [ ] **Plugin Compatibility:** Plugin loads in opencode.ai but tool calls fail — verify actual MCP tool availability
- [ ] **Chrome Connection:** Chrome appears connected but tools fail — check `/tmp/chrome-devtools-mcp.log` for actual connection status
- [ ] **MCP Config:** Using .mcp.json in opencode.ai instead of opencode.json native config
- [ ] **Chrome 136+ Compatibility:** Chrome launches but debugging fails — verify --user-data-dir is present
- [ ] **Tool Naming:** MCP tools visible in list but calls fail — verify naming convention matches opencode.ai pattern

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Plugin silently skipped | LOW | Add verbose logging; rename plugin to avoid substring; use file:// path |
| Chrome remote debug ignored | LOW | Add --user-data-dir flag; use isolated profile |
| Permission dialog blocking | MEDIUM | Kill autoConnect; use --browserUrl to persistent Chrome |
| npx failing on Windows | LOW | Switch to absolute path in MCP config |
| Connection churn in long sessions | MEDIUM | Refactor to use persistent --browserUrl connection |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Plugin skip block | Phase 1: opencode.ai Plugin Compatibility | Test with `opencode --verbose`; check plugin list |
| ESM import .js extension | Phase 1: opencode.ai Plugin Compatibility | Use file:// paths; create config package.json |
| MCP tool naming mismatch | Phase 1: opencode.ai Plugin Compatibility | Verify tool calls in both environments |
| Chrome --user-data-dir requirement | Phase 2: Chrome Remote Debug Auth | Test Chrome 136+ behavior explicitly |
| Permission dialog blocking | Phase 2: Chrome Remote Debug Auth | Run automated test with --autoConnect |
| MCP session connection churn | Phase 3: chrome-devtools-cli Integration | Monitor logs for repeated startups |
| Node.js version incompatibility | Phase 3: chrome-devtools-cli Integration | Use absolute paths; test on Windows |
| Chrome Target closed error | Phase 3: chrome-devtools-cli Integration | Clear cache; use --isolated=true |

---

## Sources

- OpenCode plugin loader issues: GitHub issues #16225, #8006, #13543, #18518, #18094
- Chrome DevTools MCP troubleshooting: https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md
- Chrome remote debugging security changes: https://developer.chrome.com/blog/remote-debugging-port
- chrome-devtools-cli issues: nicoster/chrome-devtools-cli GitHub
- Chrome MCP autoConnect problems: GitHub issues #1094, #825

---

*Pitfalls research for: Toprank Plugin Enhancement (opencode.ai + Chrome DevTools)*
*Researched: 2026-04-13*