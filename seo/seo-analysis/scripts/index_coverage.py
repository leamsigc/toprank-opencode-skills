#!/usr/bin/env python3
"""
Fetch Google Search Console Index Coverage data via CDP.
Opens GSC Index Coverage report and extracts URLs by indexing status.

This script uses Chrome DevTools to navigate the live GSC interface
when gcloud API is not available.

Usage:
  python3 index_coverage.py --domain "example.com"
  python3 index_coverage.py --domain "example.com" --output coverage.json
"""

import argparse
import json
import os
import sys
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


URL_INSPECTION_API = "https://www.googleapis.com/searchconsole/v1"


def get_access_token_gcloud():
    """Get access token via gcloud."""
    import subprocess
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def get_access_token_oauth2():
    """Try oauth2 for token."""
    import subprocess
    try:
        result = subprocess.run(
            ["oauth2", "token", "print-access-token"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def inspect_url_gcloud(token, site_url, target_url):
    """Call URL Inspection API with gcloud token."""
    import urllib.error
    import urllib.request

    api_url = f"{URL_INSPECTION_API}/urlInspectionIndex"
    body = {
        "inspectionUrl": target_url,
        "siteUrl": site_url
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(
            api_url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else "(no body)"
        return {"error": f"HTTP {e.code}", "detail": error_body}
    except Exception as e:
        return {"error": str(e)}


def parse_coverage_from_response(inspection_result):
    """Parse URL Inspection result into coverage format."""
    result = {
        "index_status": "unknown",
        "coverage_state": None,
        "mobile_usability": None,
        "rich_results": [],
        "last_crawled": None,
        "referring_sitemaps": []
    }

    index_result = inspection_result.get("indexResult", {})

    if index_result.get("indexingStatus"):
        status = index_result["indexingStatus"]
        if "INDEXED" in status:
            result["index_status"] = "indexed"
        elif "CRAWLED" in status and "NOT_INDEXED" in status:
            result["index_status"] = "crawled_not_indexed"
        elif "NOT_INDEXED" in status:
            result["index_status"] = "not_indexed"
        else:
            result["index_status"] = status.lower()

    if index_result.get("coverageState"):
        result["coverage_state"] = index_result["coverageState"]

    if index_result.get("mobileUsability"):
        result["mobile_usability"] = index_result["mobileUsability"].get("verdict", "UNKNOWN")

    if index_result.get("richResult"):
        rr = index_result["richResult"]
        result["rich_results"] = [r.get("type") for r in rr.get("richResultTypes", [])]

    if index_result.get("lastCrawled"):
        result["last_crawled"] = index_result["lastCrawled"]

    if index_result.get("referringSitemaps"):
        result["referring_sitemaps"] = index_result["referringSitemaps"]

    return result


def classify_issue(result):
    """Classify the indexing issue for reporting."""
    status = result.get("index_status", "unknown")
    state = result.get("coverage_state", "")

    if status == "indexed":
        return None

    if "noindex" in str(state).lower() or "exclu" in str(state).lower():
        return "Excluded: noindex tag"

    if "duplicate" in str(state).lower():
        return "Duplicate without canonical"

    if "server" in str(state).lower() or "error" in str(state).lower():
        return "Server error"

    if "not" in str(state).lower() and "found" in str(state).lower():
        return "Page not found (404)"

    if "robots" in str(state).lower() or "blocked" in str(state).lower():
        return "Blocked by robots.txt"

    if status == "not_indexed":
        return "Not indexed"

    if status == "crawled_not_indexed":
        return "Crawled but not indexed"

    return f"Issue: {status} - {state}"


def inspect_urls_batch(site_url, urls, token=None, max_workers=5):
    """Inspect multiple URLs in parallel."""
    if not token:
        token = get_access_token_gcloud() or get_access_token_oauth2()

    results = []

    def inspect_one(url):
        if token:
            raw = inspect_url_gcloud(token, site_url, url)
        else:
            raw = {"error": "No token available"}

        parsed = parse_coverage_from_response(raw)
        parsed["url"] = url
        parsed["issue"] = classify_issue(parsed)
        return parsed

    tasks = urls[:500]  # Limit to prevent quota exhaustion

    with ThreadPoolExecutor(max_workers=min(max_workers, len(tasks))) as pool:
        futures = {pool.submit(inspect_one, url): url for url in tasks}
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                url = futures[future]
                results.append({"url": url, "error": str(e)})

    return results


def compare_sitemap_vs_index(sitemap_urls, coverage_results):
    """Compare sitemap URLs against indexing status."""
    indexed = []
    not_indexed = []
    unknown = []

    sitemap_set = set(sitemap_urls)

    for result in coverage_results:
        url = result.get("url", "")
        status = result.get("index_status", "unknown")

        if status == "indexed":
            indexed.append(url)
        elif status == "not_indexed" or status == "crawled_not_indexed" or "not" in status:
            not_indexed.append(url)
        else:
            unknown.append(url)

    return {
        "total_in_sitemap": len(sitemap_set),
        "indexed_count": len(indexed),
        "not_indexed_count": len(not_indexed),
        "unknown_count": len(unknown),
        "indexed_urls": indexed[:50],
        "not_indexed_urls": not_indexed[:50],
        "unknown_urls": unknown[:50]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch GSC Index Coverage via URL Inspection API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --domain example.com --urls-file urls.txt
  %(prog)s --domain example.com --sitemap sitemap.json
  %(prog)s --domain example.com --urls "https://example.com/,https://example.com/about"
        '''
    )
    parser.add_argument("--domain", "-d", required=True,
                        help="Domain (e.g., example.com)")
    parser.add_argument("--site", "-s",
                        help="GSC site URL (default: sc-domain:DOMAIN)")
    parser.add_argument("--urls", "-u",
                        help="Comma-separated URLs to check")
    parser.add_argument("--urls-file",
                        help="File with URLs (one per line)")
    parser.add_argument("--sitemap",
                        help="JSON file with sitemap URLs (from sitemap_fetch.py)")
    parser.add_argument("--output", "-o",
                        help="Output file (JSON)")
    parser.add_argument("--workers", type=int, default=5,
                        help="Max parallel workers (default: 5)")

    args = parser.parse_args()

    domain = args.domain.strip().lstrip("www.")
    site_url = args.site or f"sc-domain:{domain}"

    urls = []

    # Load URLs from various sources
    if args.urls:
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]

    elif args.urls_file:
        with open(args.urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    elif args.sitemap:
        with open(args.sitemap) as f:
            data = json.load(f)
            urls = data.get("all_urls", [])

    if not urls:
        print("ERROR: No URLs provided. Use --urls, --urls-file, or --sitemap", file=sys.stderr)
        sys.exit(1)

    print(f"Checking {len(urls)} URLs for indexing status...", file=sys.stderr)

    # Get token
    token = get_access_token_gcloud()

    # Inspect URLs
    results = inspect_urls_batch(site_url, urls, token=token, max_workers=args.workers)

    # Build output
    output = {
        "domain": domain,
        "site_url": site_url,
        "urls_checked": len(urls),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

    # Add sitemap comparison if URLs came from sitemap
    if args.sitemap:
        with open(args.sitemap) as f:
            sitemap_data = json.load(f)
            sitemap_urls = sitemap_data.get("all_urls", [])

        output["sitemap_comparison"] = compare_sitemap_vs_index(sitemap_urls, results)

    # Summary
    indexed = [r for r in results if r.get("index_status") == "indexed"]
    not_indexed = [r for r in results if r.get("index_status") != "indexed"]

    output["summary"] = {
        "total": len(results),
        "indexed": len(indexed),
        "not_indexed": len(not_indexed),
        "coverage_percent": round(len(indexed) / len(results) * 100, 1) if results else 0
    }

    output_json = json.dumps(output, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    print(f"\nIndexed: {len(indexed)}/{len(results)} ({output['summary']['coverage_percent']}%)",
          file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())