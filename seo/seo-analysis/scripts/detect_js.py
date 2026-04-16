#!/usr/bin/env python3
"""
Detect if a page requires JavaScript rendering (SPA/SSR).
Analyzes HTML and response headers to determine rendering needs.
Supports MCP-based fetching for client-side rendered content analysis.
"""

import argparse
import json
import re
import subprocess
import sys


def detect_js_rendering(html_content, headers=None):
    """
    Detect if page likely requires JS rendering.
    
    Returns:
        dict: {
            'requires_js': bool,
            'indicators': list of detected indicators,
            'confidence': 'high' | 'medium' | 'low',
            'framework': str (detected framework name)
        }
    """
    indicators = []
    framework = None
    
    if not html_content:
        return {
            'requires_js': False,
            'indicators': [],
            'confidence': 'low',
            'framework': None
        }
    
    spa_patterns = [
        (r'webpack', 'Uses webpack bundler', None),
        (r'react-dom', 'Uses React', 'React'),
        (r'react\.production\.min', 'Uses React', 'React'),
        (r'vue\.js', 'Uses Vue.js', 'Vue.js'),
        (r'vue\.min\.js', 'Uses Vue.js', 'Vue.js'),
        (r'angular\.js', 'Uses Angular', 'AngularJS'),
        (r'angular\.min\.js', 'Uses Angular', 'AngularJS'),
        (r'ng-app', 'AngularJS app', 'AngularJS'),
        (r'data-reactroot', 'React rendered (SSR)', 'React'),
        (r'id="__next"', 'Next.js app', 'Next.js'),
        (r'id="__nuxt"', 'Nuxt app', 'Nuxt'),
        (r'gatsby-', 'Gatsby site', 'Gatsby'),
        (r'ember', 'Ember.js', 'Ember.js'),
        (r'svelte', 'Svelte app', 'Svelte'),
        (r'backbone', 'Backbone.js app', 'Backbone.js'),
        (r'knockout', 'Knockout.js app', 'Knockout.js'),
        (r'dojo', 'Dojo toolkit', 'Dojo'),
        (r'mootools', 'MooTools', 'MooTools'),
        (r'preact', 'Uses Preact', 'Preact'),
        (r'alpine\.js', 'Alpine.js', 'Alpine.js'),
    ]
    
    for pattern, desc, fw in spa_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            indicators.append(desc)
            if fw and not framework:
                framework = fw
    
    spa_html_patterns = [
        (r'<div id="app">', 'Single-page app div#app', None),
        (r'<div id="root">', 'Single-page app div#root', None),
        (r'<app-root', 'Angular app-root component', 'Angular'),
        (r'<router-outlet', 'Angular router', 'Angular'),
    ]
    
    for pattern, desc, fw in spa_html_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            indicators.append(desc)
            if fw and not framework:
                framework = fw
    
    ssr_patterns = [
        (r'<html[^>]*ng-version', 'Angular SSR', 'Angular'),
        (r'<!--.*server-rendered', 'Server-rendered comment', None),
        (r'__NEXT_DATA__', 'Next.js SSR data', 'Next.js'),
        (r'__NUXT__', 'Nuxt SSR data', 'Nuxt'),
    ]
    
    for pattern, desc, fw in ssr_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            indicators.append(desc)
            if fw and not framework:
                framework = fw
    
    if headers:
        if headers.get('x-sveltekit-page'):
            indicators.append('SvelteKit page')
            if not framework:
                framework = 'SvelteKit'
        if headers.get('x-nextjs-cache'):
            indicators.append('Next.js server-rendered')
            if not framework:
                framework = 'Next.js'
        if headers.get('x-astro'):
            indicators.append('Astro page')
            if not framework:
                framework = 'Astro'
        if headers.get('content-type') and 'application/json' in headers.get('content-type', ''):
            indicators.append('JSON API response')
    
    js_patterns = [
        (r'type="module"', 'ES modules used'),
        (r'type="text/babel"', 'Babel transpilation'),
        (r'type="application/ld\+json"', 'JSON-LD structured data (likely SSR)'),
    ]
    
    for pattern, desc in js_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            indicators.append(desc)
    
    hydration_patterns = [
        (r'data-hydrated', 'Hydrated component'),
        (r'ng-server-bundle', 'Angular server bundle'),
    ]
    
    for pattern, desc in hydration_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            indicators.append(desc)
    
    if len(indicators) >= 3:
        confidence = 'high'
    elif len(indicators) >= 1:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    requires_js = confidence in ('high', 'medium')
    
    return {
        'requires_js': requires_js,
        'indicators': indicators,
        'confidence': confidence,
        'framework': framework
    }


def check_mcp_available():
    """Check if MCP Chrome DevTools server is available."""
    try:
        result = subprocess.run(
            ['npx', '@modelcontextprotocol/server-chrome-devtools', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def fetch_via_mcp(url):
    """
    Fetch page HTML using MCP CDP tools.
    Returns rendered HTML for client-side analysis.
    """
    try:
        cmd = [
            'npx', '-y', '@modelcontextprotocol/server-chrome-devtools',
            'navigate-page', url,
            '--wait-for', 'networkidle',
            '--timeout', '30000'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout:
            return result.stdout
        
        return None
        
    except Exception:
        return None


def fetch_via_requests(url):
    """Fetch page HTML using requests (static fetch fallback)."""
    try:
        import requests
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Detect SPA/SSR rendering needs - identify JavaScript frameworks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --html "<html><div id=app></div></html>"
  %(prog)s --file page.html
  %(prog)s --file page.html --output result.json
  %(prog)s --use-mcp --url https://example.com
  %(prog)s --use-mcp --url https://example.com --output result.json
        '''
    )
    parser.add_argument('--html', help='HTML content to analyze')
    parser.add_argument('--file', '-f', help='File containing HTML')
    parser.add_argument('--url', help='URL to fetch and analyze')
    parser.add_argument('--use-mcp', action='store_true', help='Use MCP CDP for page fetching (recommended for SPA/SSR)')
    parser.add_argument('--output', '-o', help='Output JSON file')
    
    args = parser.parse_args()
    
    html_content = args.html
    
    if not html_content and args.url:
        if args.use_mcp:
            html_content = fetch_via_mcp(args.url)
            method = 'mcp-cdp'
        else:
            html_content = fetch_via_requests(args.url)
            method = 'requests-static'
    elif not html_content and args.file:
        try:
            with open(args.file) as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    
    if not html_content:
        print("Error: Provide --html, --file, or --url", file=sys.stderr)
        return 1
    
    result = detect_js_rendering(html_content)
    
    if args.use_mcp and args.url:
        result['method'] = 'mcp-cdp'
    elif args.url:
        result['method'] = 'requests-static'
    else:
        result['method'] = 'static-analysis'
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results written to: {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())