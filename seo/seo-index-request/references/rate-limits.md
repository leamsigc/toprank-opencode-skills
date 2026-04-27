# Google Indexing Rate Limits

## URL Inspection API

- **Requests per day**: 2000 per site
- **Requests per minute**: 600 per minute
- **Batch size**: Up to 100 URLs per request

## Indexing Speed Tips

### Fastest Methods (Priority Order)

1. **GSC URL Inspection UI**
   - Direct URL: `https://search.google.com/search-console/inspect?url={encoded_url}`
   - Click "Request Indexing" button
   - Real-time (usually within minutes)

2. **GSC Sitemap Resubmit**
   - Submit sitemap again in GSC
   - Affects all URLs in sitemap
   - 1-2 days for full effect

3. **Social Share**
   - Share on Twitter/X, LinkedIn, Facebook
   - Googlebot often crawls within hours
   - Works best for important pages

4. **Internal Links**
   - Link from an already-indexed page
   - Googlebot follows links naturally
   - Works within 1-7 days

### Indirect Triggers (Slower)

5. **Live Fetch (fetch method)**
   - Triggers a Googlebot visit
   - May take 1-7 days
   - Not guaranteed

6. **Sitemap Update**
   - Add URL to sitemap
   - Resubmit sitemap in GSC
   - 1-3 days

## Troubleshooting

### "Too Many Requests" (429 Error)

Solution: Add delay between requests:

```bash
python3 index_request.py --urls-file urls.txt --delay 5
```

### "Permission Denied" (403 Error)

Solution: Re-authenticate gcloud:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters
```

### Page Shows "Submitted" But Not Indexed

This is normal. "Submitted" means Google received the URL
but hasn't processed it yet. Wait 24-48 hours and check again.

### Page Status Changes After Indexing

If an indexed page suddenly becomes NOT_INDEXED:
1. Check for algorithm updates
2. Check for technical issues (server errors, noindex added)
3. Review Search Console for manual actions

## Batch Best Practices

| Batch Size | Recommended Delay |
|-----------|------------------|
| 1-10 URLs | 1 second |
| 11-50 URLs | 2 seconds |
| 51-100 URLs | 5 seconds |
| 100+ URLs | 10 seconds or use sitemap |

## Index Coverage States Explained

| State | Meaning |
|-------|---------|
| Indexed | In Google's index |
| Submitted and indexed | Added via sitemap, now indexed |
| Submitted | Received but not yet processed |
| Crawled - currently not indexed | Googlebot visited but chose not to index |
| Discovered - not indexed | Found via links but not crawled yet |
| Duplicate without user-selected canonical | Competing with another page |
| Blocked by robots.txt | Disallowed in robots.txt |
| Excluded by 'noindex' | Page has noindex directive |
| Soft 404 | Page appears empty/low quality |
| Page not found (404) | URL returns 404 |
| Server error (5xx) | Server errors during crawl |