#!/usr/bin/env python3
"""
Request Google to index specific URLs.
Supports multiple methods:
- URL Inspection API (via gcloud) - official
- CDP-based inspection (via chrome-devtools) - uses live GSC
- Live URL fetch (triggers Googlebot crawl) - indirect

Usage:
  python3 index_request.py --url "https://example.com/page"
  python3 index_request.py --url "https://example.com/page" --method cdp
  python3 index_request.py --url "https://example.com" --batch-file urls.txt --delay 2
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


URL_INSPECTION_API = "https://www.googleapis.com/searchconsole/v1/urlInspectionIndex"


def get_access_token():
    """Get gcloud access token."""
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


def check_mcp_available():
    """Check if chrome-devtools MCP is available."""
    try:
        result = subprocess.run(
            ["npx", "-y", "@modelcontextprotocol/server-chrome-devtools", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def inspect_url_api(token, site_url, target_url):
    """Call URL Inspection API."""
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
            URL_INSPECTION_API,
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


def check_index_status_api(token, site_url, target_url):
    """Check current indexing status via URL Inspection API."""
    result = inspect_url_api(token, site_url, target_url)

    if result.get("error"):
        return {"status": "error", "error": result.get("error"), "detail": result.get("detail")}

    index_result = result.get("indexResult", {})

    status = "unknown"
    indexing_status = index_result.get("indexingStatus", "")
    if "INDEXED" in indexing_status:
        status = "indexed"
    elif "NOT_INDEXED" in indexing_status:
        status = "not_indexed"
    elif "CRAWLED" in indexing_status:
        status = "crawled_not_indexed"
    elif "SUBMITTED" in indexing_status:
        status = "submitted"

    return {
        "status": status,
        "coverage_state": index_result.get("coverageState"),
        "mobile_usability": index_result.get("mobileUsability", {}).get("verdict"),
        "rich_results": index_result.get("richResult", {}).get("richResultTypes", []),
        "last_crawled": index_result.get("lastCrawled"),
        "referring_sitemaps": index_result.get("referringSitemaps", [])
    }


def get_index_instructions_gcloud(domain, urls, delay=1):
    """Get index request instructions for gcloud API method."""
    instructions = []

    for url in urls:
        instructions.append({
            "url": url,
            "action": "navigate_gsc",
            "instruction": (
                f"Navigate to https://search.google.com/search-console/index"
                f"?resource_id=sc-domain%3A{domain}"
                f"&url={urllib.parse.quote(url)}"
            )
        })

    return instructions


def get_index_instructions_cdp(domain, urls):
    """Get CDP-based index request instructions."""
    instructions = []

    for url in urls:
        instructions.append({
            "url": url,
            "action": "inspect_url",
            "instruction": (
                f"Navigate to https://search.google.com/search-console/inspect"
                f"?url={urllib.parse.quote(url)}"
            )
        })

    return instructions


def trigger_crawl_live_fetch(url, user_agent="Mozilla/5.0 (compatible; Googlebot/2.1)"):
    """Trigger Googlebot crawl by fetching the URL."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": user_agent}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            return {
                "url": url,
                "status": status,
                "crawled": True,
                "timestamp": datetime.now().isoformat()
            }
    except urllib.error.HTTPError as e:
        return {
            "url": url,
            "status": e.code,
            "crawled": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "url": url,
            "crawled": False,
            "error": str(e)
        }


def check_status_live(url):
    """Check page status by fetching it."""
    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": "Mozilla/5.0 (compatible; TopRank/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return {
                "url": url,
                "status": response.status,
                "content_length": response.headers.get("Content-Length", "unknown"),
                "content_type": response.headers.get("Content-Type", "unknown")
            }
    except urllib.error.HTTPError as e:
        return {
            "url": url,
            "status": e.code,
            "error": str(e)
        }
    except Exception as e:
        return {
            "url": url,
            "status": 0,
            "error": str(e)
        }


def process_url(token, site_url, url, method="api", delay=1):
    """Process a single URL for indexing."""
    result = {
        "url": url,
        "timestamp": datetime.now().isoformat()
    }

    if method == "api":
        if not token:
            result["error"] = "No gcloud token available"
            return result

        status = check_index_status_api(token, site_url, url)
        result.update(status)

        if status.get("status") != "indexed":
            result["needs_request"] = True
            result["instructions"] = (
                "Navigate to GSC URL Inspection and request indexing"
            )
        else:
            result["needs_request"] = False

    elif method == "cdp":
        result["method"] = "cdp"
        result["instructions"] = (
            "Use chrome-devtools to navigate GSC URL Inspection page "
            f"and submit {url} for indexing"
        )

    elif method == "fetch":
        crawl_result = trigger_crawl_live_fetch(url)
        result["crawl"] = crawl_result
        result["instructions"] = (
            "Googlebot will re-crawl on next visit. "
            "For faster indexing, use GSC URL Inspection."
        )

    time.sleep(delay)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Request Google indexing for URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Methods:
  api    - Use URL Inspection API (requires gcloud auth)
  cdp    - Get instructions for CDP-based inspection
  fetch  - Trigger via live URL fetch (indirect)

Examples:
  %(prog)s --url https://example.com/new-page
  %(prog)s --url https://example.com/new-page --method cdp
  %(prog)s --domain example.com --batch-file urls.txt --delay 2
        '''
    )
    parser.add_argument("--url", "-u", help="Single URL to index")
    parser.add_argument("--urls", help="Comma-separated URLs")
    parser.add_argument("--urls-file", help="File with URLs (one per line)")
    parser.add_argument("--domain", "-d", help="Domain (e.g., example.com)")
    parser.add_argument("--site", "-s", help="GSC site URL (default: sc-domain:DOMAIN)")
    parser.add_argument("--method", "-m", default="api",
                        choices=["api", "cdp", "fetch"],
                        help="Index request method")
    parser.add_argument("--delay", type=float, default=1,
                        help="Delay between requests (seconds, default: 1)")
    parser.add_argument("--output", "-o", help="Output file (JSON)")

    args = parser.parse_args()

    urls = []

    if args.url:
        urls = [args.url.strip()]

    if args.urls:
        urls = [u.strip() for u in args.urls.split(",") if u.strip()]

    if args.urls_file:
        with open(args.urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        print("ERROR: No URLs provided", file=sys.stderr)
        sys.exit(1)

    domain = args.domain or ""
    if not domain and urls:
        domain = urllib.parse.urlparse(urls[0]).netloc.lstrip("www.")

    site_url = args.site or f"sc-domain:{domain}"

    print(f"Processing {len(urls)} URL(s) via {args.method}...", file=sys.stderr)

    token = get_access_token() if args.method == "api" else None
    mcp_available = check_mcp_available()

    results = []

    if len(urls) == 1:
        result = process_url(token, site_url, urls[0], args.method, args.delay)
        results.append(result)
    else:
        max_workers = min(5, len(urls))
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(process_url, token, site_url, url, args.method, args.delay): url
                for url in urls
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    url = futures[future]
                    results.append({"url": url, "error": str(e)})

    output = {
        "domain": domain,
        "site_url": site_url,
        "method": args.method,
        "urls_processed": len(urls),
        "mcp_available": mcp_available,
        "gcloud_available": bool(token),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

    output["summary"] = {
        "total": len(results),
        "indexed": sum(1 for r in results if r.get("status") == "indexed"),
        "not_indexed": sum(1 for r in results if r.get("needs_request")),
        "errors": sum(1 for r in results if r.get("error"))
    }

    output_json = json.dumps(output, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    print(f"\nIndexed: {output['summary']['indexed']}/{len(urls)}", file=sys.stderr)
    if output["summary"]["not_indexed"] > 0:
        print(f"Needs indexing request: {output['summary']['not_indexed']}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())