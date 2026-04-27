# toprank-opencode-skills

**SEO + Google Ads skills for opencode.ai. Data-driven decisions, not dashboards.**

This project is based on the original [Toprank](https://github.com/nowork-studio/toprank) for Claude Code, migrated to work natively as opencode.ai skills. Instead of external API keys, this version uses Chrome DevTools Protocol via MCP for direct browser-based SEO analysis and auditing capabilities.

Toprank gives your AI agent direct access to Google Search Console and Google Ads. It analyzes your traffic, surfaces what's hurting your rankings, finds wasted ad spend, and tells you exactly what to fix. When you have access to the repo, it goes further: rewriting meta tags, fixing headings, adding structured data, and shipping the changes.

> *"Am I wasting money on ads right now?"*
> *"Why did my traffic drop and how do I fix it?"*
> *"How do I get more conversions without spending more?"*

Free, open-source. Install in 30 seconds.

---

## See It Work

### Google Ads

```
You:    /toprank:ads-audit

Claude: Connected to your Google Ads account (MyStore).

        3 campaigns active. $2,400 spent this month.

        Scorecard:
        ┌──────────────────────┬──────────┬──────────────────────────────┐
        │ Dimension            │ Status   │ Summary                      │
        ├──────────────────────┼──────────┼──────────────────────────────┤
        │ Conversion tracking  │ OK       │ 3 actions firing correctly   │
        │ Keyword health       │ Critical │ 8 keywords burning cash      │
        │ Search term quality  │ Warning  │ 12 irrelevant queries        │
        │ Impression share     │ Warning  │ Losing 35% to rank           │
        │ Spend efficiency     │ Critical │ $340/mo wasted               │
        └──────────────────────┴──────────┴──────────────────────────────┘

        Top 3 actions:
        1. Pause 3 keywords ($210/mo, zero conversions)
        2. Add 12 negative keywords ($130/mo wasted on irrelevant terms)
        3. Increase bids 15% on 2 high-converting keywords losing IS

        Business context saved — /toprank:ads-copy and /toprank:ads will use it.

You:    Do it all.

        [paused 3 wasteful keywords — saved $210/mo]
        [added 12 negative keywords — saved $130/mo]
        [increased bids on 2 high-performers]

        Done. All changes are reversible within 7 days.
```

### SEO

```
You:    /toprank:seo-analysis

Claude: Found your site at mystore.com — pulling Search Console data now.

        [90 days of real traffic data loaded]
        [pages crawled for technical issues]

        Three things hurting you most:

        Your homepage lives at two addresses. Google splits your ranking
        power between them. Easy fix.

        Two pages targeting the same search terms — they compete against
        each other and neither wins.

        One page gets 400 monthly impressions but ranks #52. The title
        doesn't match what people actually search for.

        Here's your 30-day plan, most impactful first.
```

---

## Install

toprank-opencode-skills is designed as native skills for opencode.ai.

### opencode.ai Installation

Run in opencode.ai:

```
/plugin add https://github.com/leamsigc/toprank-opencode-skills
```

All skills available as `/toprank:*` commands.

**Install scripts:**

```bash
./bin/opencode-test    # Verify plugin structure and dependencies
./bin/opencode-install # Show install instructions
```

### Dependencies

Toprank requires these tools:

| Dependency | Purpose | Install |
|------------|----------|---------|
| **npx** | Run MCP servers without global install | Part of npm |
| **@modelcontextprotocol/server-chrome-devtools** | Chrome DevTools Protocol | Auto-installed via MCP |

### Chrome DevTools MCP

No external API keys required for SEO analysis. This version uses the Chrome DevTools MCP server directly which provides:
- Full JavaScript rendering analysis
- Visual page element inspection
- Runtime performance metrics
- Network request inspection
- DOM accessibility checks

Configure via `.mcp.json`:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-chrome-devtools"],
      "env": {
        "CHROME_REMOTE_DEBUGGING_PORT": "9222"
      }
    }
  }
}
```

Start Chrome with remote debugging:
```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

### Test and Verify

After adding the plugin, verify it works:

```bash
# In opencode:

/plugin add https://github.com/leamsigc/toprank-opencode-skills

# Test available skills:
/toprank:ads
/toprank:seo-analysis mystore.com

# Verify MCP servers loaded:
/mcp list
```

**Chrome must be running** with remote debugging enabled for SEO analysis to use Chrome DevTools features.

---

## Skills

### Google Ads

| Skill | What it does |
|-------|-------------|
| [`ads-audit`](google-ads/ads-audit/) | Account audit + business context setup. Run this first. Scores 7 health dimensions, identifies wasted spend, builds business profile. |
| [`ads`](google-ads/ads/) | Campaign management. Read performance, optimize keywords, adjust bids/budgets, add negatives, create campaigns. |
| [`ads-copy`](google-ads/ads-copy/) | RSA copy generator + A/B testing. Data-driven headlines and descriptions with character counts and pin positions. |

### SEO

| Skill | What it does |
|-------|-------------|
| [`seo-analysis`](seo/seo-analysis/) | Full SEO audit with GSC data. Quick wins, traffic drops, technical issues, 30-day action plan. |
| [`content-writer`](seo/content-writer/) | SEO content creation following E-E-A-T guidelines. Blog posts, landing pages, content improvements. |
| [`keyword-research`](seo/keyword-research/) | Keyword discovery, intent classification, topic clusters, prioritized content calendar. |
| [`meta-tags-optimizer`](seo/meta-tags-optimizer/) | Title tags, meta descriptions, OG/Twitter cards with A/B variations and CTR estimates. |
| [`schema-markup-generator`](seo/schema-markup-generator/) | JSON-LD structured data for rich results. FAQ, HowTo, Article, Product, LocalBusiness. |
| [`setup-cms`](seo/setup-cms/) | Connect WordPress, Strapi, Contentful, or Ghost for automated SEO field audits. |

### Cross-Model

| Skill | What it does |
|-------|-------------|
| [`gemini`](gemini/) | Second opinion from Google Gemini. Review (pass/fail gate), challenge (adversarial stress test), or consult (open Q&A). Especially strong on Google Ads and SEO decisions — Gemini has native Google ecosystem knowledge. |

All skills are namespaced: `/toprank:ads`, `/toprank:seo-analysis`, `/toprank:gemini`, etc.

---

## How It Works

Toprank uses opencode.ai skill architecture. Each skill is a `SKILL.md` file with supporting reference documents, scripts, and eval tests.

```
toprank-opencode-skills/
├── .mcp.json                    <- Chrome DevTools MCP configuration
├── google-ads/
│   ├── ads/                     <- campaign management
│   ├── ads-audit/               <- account audit + business context
│   └── ads-copy/                <- RSA copy generator + A/B testing
├── seo/
│   ├── seo-analysis/            <- full SEO audit with GSC data
│   ├── content-writer/          <- E-E-A-T content creation
│   ├── keyword-research/        <- keyword discovery + topic clusters
│   ├── meta-tags-optimizer/     <- title tags, meta descriptions, OG
│   ├── schema-markup-generator/ <- JSON-LD structured data
│   ├── seo-page/                <- single-page deep analysis
│   └── setup-cms/               <- CMS connector
├── gemini/                      <- cross-model review via Gemini CLI
├── toprank-upgrade-skill/       <- self-updater
├── test/                        <- unit + LLM-judge eval tests
└── VERSION
```

---

## Connectors

Toprank skills reference external tools using the `~~category` placeholder pattern. This makes skills tool-agnostic — they work with any MCP server that provides the required capability.

| Category | Placeholder | Default Server | Alternatives |
|----------|-------------|---------------|--------------|
| Google Ads | `~~google-ads` | Chrome DevTools Protocol | Any Google Ads MCP server |
| Search Console | `~~search-console` | gcloud CLI + Search Console API | Any GSC-compatible MCP server |
| CMS | `~~cms` | Direct API (WordPress REST, Strapi, Contentful, Ghost) | Any CMS MCP server |

Skills use conditional blocks based on available tools. If a connector is not available, the skill gracefully degrades — for example, `seo-analysis` can still run a technical crawl without GSC data.

**Setup:**
- **Chrome DevTools:** No API keys required. Just start Chrome with remote debugging enabled.
- **Search Console:** See `seo/shared/preamble.md`. Requires Google Cloud SDK, Search Console API enabled, and OAuth login.
- **CMS:** Run `/toprank:setup-cms` to configure WordPress, Strapi, Contentful, or Ghost.

---

## Contributing

Each skill lives in its own folder under a category directory:

```
seo/                      <- SEO skills go here
└── your-skill-name/
    ├── SKILL.md          <- required
    ├── scripts/          <- optional
    └── references/       <- optional

google-ads/               <- Google Ads skills go here
└── your-skill-name/
    └── SKILL.md          <- required
```

**SKILL.md** needs a frontmatter header with `name` and `description`, then step-by-step instructions in the imperative.

**Scripts:** Python 3.8+ stdlib only (or `requests`). Accept `--output` for file output. stderr for progress, stdout for data.

**Pull requests:** One skill per PR. Test your skill before submitting. Bump `VERSION` and update `CHANGELOG.md`.

Questions? Open an issue at https://github.com/leamsigc/toprank-opencode-skills

---

## Repository

https://github.com/leamsigc/toprank-opencode-skills

---

## License

[MIT](LICENSE)