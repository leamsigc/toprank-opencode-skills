#!/usr/bin/env python3
"""
Fetch and parse XML sitemaps for SEO analysis.
Outputs structured JSON with all URLs, metadata, and validation issues.

Supports:
- Standard XML sitemaps (single and index)
- Simple sitemaps (list of URLs)
- Auto-discovery from robots.txt

Usage:
  python3 sitemap_fetch.py --url "https://example.com/sitemap.xml"
  python3 sitemap_fetch.py --url "https://example.com" --discover
  python3 sitemap_fetch.py --url "https://example.com" --output sitemap.json
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime
from xml.etree import ElementTree as ET


DEFAULT_SITEMAPS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/sitemap-news.xml",
    "/sitemap-products.xml",
    "/sitemap-images.xml",
    "/sitemap-video.xml",
]


def get_sitemap_from_robots(url):
    """Extract sitemap URL from robots.txt."""
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        req = urllib.request.Request(robots_url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; TopRank/1.0)"
        })
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode("utf-8", errors="ignore")
            for line in content.split("\n"):
                line = line.strip()
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    return sitemap_url
    except Exception as e:
        pass
    return None


def fetch_sitemap(url, depth=0, max_depth=3, visited=None):
    """
    Fetch and parse a sitemap URL.
    Returns dict with URLs, type, metadata, and any errors.
    """
    if visited is None:
        visited = set()

    if depth > max_depth:
        return {"url": url, "type": "error", "error": "max_depth_exceeded", "entries": []}

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; TopRank/1.0)"
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8", errors="ignore")
            content_type = response.headers.get("Content-Type", "")

    except urllib.error.HTTPError as e:
        return {"url": url, "type": "error", "error": f"HTTP {e.code}", "entries": []}
    except urllib.error.URLError as e:
        return {"url": url, "type": "error", "error": str(e.reason), "entries": []}
    except Exception as e:
        return {"url": url, "type": "error", "error": str(e), "entries": []}

    # Track visited to prevent loops
    visited.add(url)

    # Check content type
    if "xml" in content_type:
        return parse_xml_sitemap(url, content, depth, visited)
    elif content.strip().startswith("<") and "urlset" in content.lower():
        return parse_xml_sitemap(url, content, depth, visited)
    else:
        return parse_simple_sitemap(url, content, depth, visited)


def parse_xml_sitemap(url, content, depth, visited):
    """Parse standard XML sitemap or sitemap index."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return {"url": url, "type": "error", "error": f"XML parse: {e}", "entries": []}

    tag = root.tag.lower()

    # Sitemap index - extract child sitemaps
    if "sitemapindex" in tag:
        return parse_sitemap_index(url, root, depth, visited)

    # Urlset - extract URLs
    elif "urlset" in tag:
        return parse_urlset(url, root, content)

    # Unknown format
    return {"url": url, "type": "error", "error": "Unknown XML format", "entries": []}


def parse_sitemap_index(url, root, depth, visited):
    """Parse a sitemap index and fetch child sitemaps recursively."""
    entries = []
    metadata = {"child_sitemaps": []}

    for child in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap") or root.findall(".//sitemap"):
        loc_elem = child.find("loc") or child.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc_elem is None:
            continue

        sitemap_url = loc_elem.text.strip() if loc_elem.text else ""

        # Get lastmod if available
        lastmod_elem = child.find("lastmod") or child.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        lastmod = lastmod_elem.text if lastmod_elem is not None and lastmod_elem.text else None

        metadata["child_sitemaps"].append({
            "url": sitemap_url,
            "lastmod": lastmod
        })

        # Fetch child sitemap if not too deep
        if depth < 2 and sitemap_url not in visited:
            child_result = fetch_sitemap(sitemap_url, depth + 1, 3, visited)
            if child_result.get("entries"):
                entries.extend(child_result["entries"])
            metadata["child_sitemaps"][-1]["entry_count"] = len(child_result.get("entries", []))

    return {
        "url": url,
        "type": "sitemap_index",
        "metadata": metadata,
        "entries": entries,
        "total_urls": len(entries)
    }


def parse_urlset(url, root, content):
    """Parse a standard urlset sitemap."""
    entries = []
    namespaces = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1",
        "video": "http://www.google.com/schemas/sitemap-video/1.1",
        "news": "http://www.google.com/schemas/sitemap-news/0.9",
    }

    for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url") or root.findall(".//url"):
        entry = {}

        # Location (required)
        loc_elem = url_elem.find("loc") or url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc_elem is None:
            continue
        entry["loc"] = loc_elem.text.strip() if loc_elem.text else ""

        # Lastmod
        lastmod_elem = url_elem.find("lastmod") or url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        if lastmod_elem is not None and lastmod_elem.text:
            entry["lastmod"] = lastmod_elem.text.strip()

        # Priority
        priority_elem = url_elem.find("priority") or url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
        if priority_elem is not None and priority_elem.text:
            entry["priority"] = float(priority_elem.text)

        # Change frequency
        freq_elem = url_elem.find("changefreq") or url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
        if freq_elem is not None and freq_elem.text:
            entry["changefreq"] = freq_elem.text.strip()

        # Look for image entries
        image_elems = url_elem.findall(".//{http://www.google.com/schemas/sitemap-image/1.1}loc") or url_elem.findall(".//image:loc", namespaces)
        if image_elems:
            entry["images"] = [img.text for img in image_elems if img.text]

        # Look for video entries
        video_elems = url_elem.findall(".//{http://www.google.com/schemas/sitemap-video/1.1}loc") or url_elem.findall(".//video:loc", namespaces)
        if video_elems:
            entry["videos"] = [vid.text for vid in video_elems if vid.text]

        entries.append(entry)

    return {
        "url": url,
        "type": "urlset",
        "entries": entries,
        "total_urls": len(entries)
    }


def parse_simple_sitemap(url, content, depth, visited):
    """Parse a simple newline-separated URL list."""
    entries = []

    for line in content.split("\n"):
        line = line.strip()
        if line and not line.startswith(("#")):
            if line.startswith("http"):
                entries.append({"loc": line})

    return {
        "url": url,
        "type": "simple",
        "entries": entries,
        "total_urls": len(entries)
    }


def discover_sitemaps(base_url):
    """Auto-discover sitemaps from a domain."""
    discovered = []
    parsed = urllib.parse.urlparse(base_url)

    if not parsed.scheme:
        base_url = f"https://{base_url}"
        parsed = urllib.parse.urlparse(base_url)

    base = f"{parsed.scheme}://{parsed.netloc}"

    for sitemap_path in DEFAULT_SITEMAPS:
        test_url = base + sitemap_path
        try:
            req = urllib.request.Request(test_url, method="HEAD", headers={
                "User-Agent": "TopRank/1.0"
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    discovered.append(test_url)
        except Exception:
            pass

    # Also check robots.txt
    robots_sitemap = get_sitemap_from_robots(base_url)
    if robots_sitemap and robots_sitemap not in discovered:
        discovered.append(robots_sitemap)

    return discovered


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and parse XML sitemaps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --url https://example.com/sitemap.xml
  %(prog)s --url https://example.com --discover
  %(prog)s --url https://example.com --output sitemap.json
        '''
    )
    parser.add_argument("--url", required=True, help="Sitemap URL or domain to discover")
    parser.add_argument("--discover", action="store_true", help="Auto-discover sitemaps")
    parser.add_argument("--output", "-o", help="Output file (JSON)")
    parser.add_argument("--follow-index", action="store_true", default=True,
                        help="Follow sitemap index (default: True)")

    args = parser.parse_args()

    url = args.url.strip()

    # Parse as URL
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"

    results = {"base_url": url, "sitemaps": [], "all_urls": [], "discovered": []}

    if args.discover:
        # Auto-discover sitemaps
        results["discovered"] = discover_sitemaps(url)
        base = f"{urllib.parse.urlparse(url).scheme}://{urllib.parse.urlparse(url).netloc}"

        for sm_url in results["discovered"]:
            result = fetch_sitemap(sm_url)
            if result.get("entries"):
                results["sitemaps"].append(result)
                results["all_urls"].extend([e["loc"] for e in result["entries"]])

    else:
        # Fetch specific sitemap
        result = fetch_sitemap(url)
        results["sitemaps"].append(result)
        if result.get("entries"):
            results["all_urls"] = [e["loc"] for e in result["entries"]]

    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for u in results["all_urls"]:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    results["all_urls"] = unique_urls
    results["total_urls"] = len(unique_urls)

    output = json.dumps(results, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Sitemap data written to {args.output}", file=sys.stderr)
        print(f"Total URLs found: {results['total_urls']}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())