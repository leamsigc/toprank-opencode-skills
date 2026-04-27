---
name: seo-index-request
argument-hint: "<URL(s) to index, e.g. https://example.com/new-page>"
description: >
  Request Google to index specific URLs. Checks current indexing status, identifies
  pages not in Google's index, and triggers re-crawl/indexing. Supports URL Inspection
  API (gcloud), Chrome DevTools CDP, and indirect crawl triggering. Use this skill
  when: new pages aren't showing in search, you submitted new content, pages got
  deindexed, you fixed indexing issues, or need to check why a URL isn't ranking.
  Also triggers on: "index this page", "request indexing", "submit to Google",
  "reindex page", "force reindex", "why not indexed", "check indexing status",
  "update Google index", or any request to get URLs into Google's index.
---

# SEO Index Request

You are an indexing specialist. Your job is to help users get their URLs into
Google's index and keep them there. You check indexing status, identify issues,
and trigger re-crawling when needed.

---

## Phase 0 — Get Target URLs

Ask the user for the URL(s) to check or index:

> "Enter the URL(s) you want to check or index (comma-separated, or one per line)"

Accept:
- Single URL: `https://example.com/blog/new-post`
- Multiple URLs: `https://example.com/page1, https://example.com/page2`
- URL list (ask user to paste)

Derive domain if not provided:

```bash
DOMAIN=$(python3 -c "import sys; from urllib.parse import urlparse; print(urlparse(sys.argv[1]).netloc.lstrip('www.'))" "$PAGE_URL")
```

---

## Phase 1 — Check Indexing Status

Choose the method based on available tools:

### Method A: URL Inspection API (requires gcloud)

```bash
SKILL_SCRIPTS=$(find ~/.claude/plugins ~/.claude/skills .agents/skills -type d -name scripts -path "*seo-index-request*" 2>/dev/null | head -1)
[ -z "$SKILL_SCRIPTS" ] && SKILL_SCRIPTS="./seo/seo-index-request/scripts"

python3 "$SKILL_SCRIPTS/index_request.py" \
  --domain "$DOMAIN" \
  --url "https://example.com/page" \
  --method api \
  --output /tmp/index_status.json
```

### Method B: CDP-based (via chrome-devtools)

If no gcloud available, use CDP to navigate GSC:

```bash
# Navigate to GSC URL Inspection
chrome-devtools_new_page(url="https://search.google.com/search-console/inspect?url={ENCODED_URL}")

# Extract status via evaluate_script
chrome-devtools_evaluate_script(() => {
  return document.querySelector('.index-status')?.innerText || 'Not found';
})
```

### Method C: Check if page is indexed (quick)

Use Google search to check if indexed:

```bash
# Search for the URL in Google
site:example.com/page-to-check
```

---

## Phase 2 — Analyze Results

### Indexing Status Categories

| Status | Meaning | Action Needed? |
|--------|---------|----------------|
| `INDEXED` | Page is in Google's index | No |
| `NOT_INDEXED` | Page not indexed | Yes - find why |
| `CRAWLED_NOT_INDEXED` | Google crawled but didn't index | Yes - fix issues |
| `SUBMITTED` | Submitted but not yet indexed | Wait or re-submit |
| `UNKNOWN` | Could not determine | Check manually |

### Common Reasons for Not Indexing

| Issue | Check | Fix |
|-------|-------|-----|
| Noindex tag | View page source | Remove noindex |
| Canonical to other URL | Check canonical tag | Fix canonical |
| Blocked by robots.txt | Check robots.txt | Allow in robots.txt |
| Thin/duplicate content | Compare to similar pages | Add unique content |
| 4xx/5xx error | Check response code | Fix server issues |
| Not in sitemap | Check sitemap | Add to sitemap |
| Very new | Wait 24-48 hours | Be patient |

---

## Phase 3 — Request Indexing

For pages NOT indexed, trigger indexing:

### Option 1: Submit via GSC URL Inspection

Navigate to:
```
https://search.google.com/search-console/inspect?url={ENCODED_URL}
```

Click "Request Indexing" button in the UI.

### Option 2: Use CDP to automate

```bash
# Navigate to inspection page
chrome-devtools_navigate_page(url="https://search.google.com/search-console/inspect?url={ENCODED_URL}")

# Click the indexing button
chrome-devtools_click(uid="<button-uid>")  # Find the "Request Indexing" button
```

### Option 3: Trigger via sitemap

If URL is in sitemap, resubmit sitemap:

1. Go to GSC → Sitemaps
2. Click "Resubmit" next to your sitemap

### Option 4: Indirect trigger (live fetch)

```bash
# Fetch the URL - Googlebot may re-crawl
python3 "$SKILL_SCRIPTS/index_request.py" \
  --url "https://example.com/page" \
  --method fetch
```

This triggers a fetch which notifies Googlebot.

---

## Phase 4 — Report Results

Output a structured report:

---

# Index Request Report — [domain.com]
*[date]*

## Summary

| Metric | Count |
|--------|-------|
| URLs Checked | N |
| Indexed | N |
| Not Indexed | N |
| Errors | N |

## Detailed Results

| URL | Status | Coverage State | Action |
|-----|--------|---------------|--------|
| /page1 | Indexed | - | None needed |
| /page2 | Not Indexed | Exclusion: noindex | Remove noindex tag |
| /page3 | Crawled Not Indexed | - | Fix thin content |

## Actions Taken

- [ ] **/page2**: Remove `<meta name="robots" content="noindex">` from HTML
- [ ] **/page3**: Add more unique content (minimum 300 words)
- [ ] **/page4**: Fix canonical URL to point to itself

## Next Steps

1. Fix identified issues
2. Wait 24-48 hours for re-crawl
3. Run `/seo-analysis` to verify indexing

---

## Tips for Faster Indexing

1. **Internal links**: Ensure the page is linked from at least 1 other indexed page
2. **Sitemap**: Add new pages to sitemap and resubmit in GSC
3. **Share on social**: Social signals can trigger faster crawling
4. **Google News**: If news content, submit to Google News
5. **API**: For bulk indexing, use URL Inspection API (requires gcloud setup)

---

## Batch Processing

For multiple URLs:

```bash
# Create URL list
echo "https://example.com/page1
https://example.com/page2
https://example.com/page3" > /tmp/urls.txt

# Process batch
python3 "$SKILL_SCRIPTS/index_request.py" \
  --domain "$DOMAIN" \
  --urls-file /tmp/urls.txt \
  --method api \
  --delay 2 \
  --output /tmp/batch_index.json
```

**Note**: Google's indexing has rate limits. Use `--delay 2` or higher between
requests to avoid 429 errors.