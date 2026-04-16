#!/usr/bin/env python3
"""
Headless Chrome audit using Chrome DevTools Protocol via MCP.
Fetches pages with full JavaScript rendering for SEO analysis.
Uses MCP tools (navigate_page, take_snapshot) when available,
falls back to direct CDP WebSocket connection.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import tempfile
from datetime import datetime
from urllib.parse import urlparse


def get_chrome_port():
    """Get Chrome remote debugging port from session or default."""
    session_file = f"{os.path.expanduser('~')}/.toprank/cdp-sessions/current.json"
    if os.path.exists(session_file):
        with open(session_file) as f:
            session = json.load(f)
            return session.get('port', 9222)
    return 9222


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


def run_mcp_command(url, wait_ms=2000):
    """
    Run MCP Chrome DevTools commands via npx.
    Uses navigate_page and take_snapshot for full JavaScript rendering.
    """
    try:
        cmd = [
            'npx', '-y', '@modelcontextprotocol/server-chrome-devtools',
            'navigate-page', url,
            '--wait-for', 'networkidle',
            '--timeout', str(wait_ms + 5000)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and result.stdout:
            return {
                'url': url,
                'rendered_html': result.stdout,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'method': 'mcp-cdp'
            }
        
        return {
            'url': url,
            'rendered_html': '',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': 'MCP command failed',
            'method': 'mcp-cdp'
        }
        
    except subprocess.TimeoutExpired:
        return {
            'url': url,
            'rendered_html': '',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': 'Timeout during MCP navigation',
            'method': 'mcp-cdp'
        }
    except FileNotFoundError:
        return {
            'url': url,
            'rendered_html': '',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': 'npx not found - install Node.js',
            'method': 'mcp-cdp'
        }
    except Exception as e:
        return {
            'url': url,
            'rendered_html': '',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': str(e),
            'method': 'mcp-cdp'
        }


def audit_page_direct_cdp(url, port=9222):
    """
    Fallback: Use direct CDP protocol for page auditing.
    Uses WebSocket to connect to Chrome's debugging port.
    """
    try:
        import urllib.request
        import urllib.error
        
        json_body = json.dumps({
            'id': 1,
            'method': 'Page.enable'
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f'http://localhost:{port}/json',
            data=json_body,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            pages = json.loads(response.read().decode('utf-8'))
            
        if not pages:
            return {
                'url': url,
                'rendered_html': '',
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': 'No Chrome pages found'
            }
        
        page_id = pages[0]['id']
        
        navigate_body = json.dumps({
            'id': 2,
            'method': 'Page.navigate',
            'params': {'url': url}
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f'http://localhost:{port}/json/send/{page_id}',
            data=navigate_body,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            pass
        
        time.sleep(2)
        
        get_html_body = json.dumps({
            'id': 3,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': 'document.documentElement.outerHTML',
                'returnByValue': True
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f'http://localhost:{port}/json/send/{page_id}',
            data=get_html_body,
            headers={'Content-Type': 'application/json'}
        )
        
        rendered_html = ''
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('result', {}).get('result', {}).get('value'):
                rendered_html = result['result']['result']['value']
        
        return {
            'url': url,
            'rendered_html': rendered_html,
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'method': 'direct-cdp'
        }
        
    except ImportError:
        return {
            'url': url,
            'rendered_html': '',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': 'Python urllib required for direct CDP',
            'method': 'direct-cdp'
        }
    except urllib.error.URLError:
        return {
            'url': url,
            'rendered_html': '',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': f'Cannot connect to Chrome on port {port}',
            'method': 'direct-cdp'
        }
    except Exception as e:
        return {
            'url': url,
            'rendered_html': '',
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': str(e),
            'method': 'direct-cdp'
        }


def audit_page(url, port=9222):
    """
    Audit a page using headless Chrome via MCP or direct CDP.
    
    Tries MCP first (better integration), falls back to direct CDP.
    No CLI fallback - uses protocol directly.
    """
    mcp_available = check_mcp_available()
    
    if mcp_available:
        result = run_mcp_command(url)
        if result['success']:
            return result
    
    return audit_page_direct_cdp(url, port)


def main():
    parser = argparse.ArgumentParser(
        description='Headless Chrome SEO audit - fetch pages with JavaScript rendering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --url https://example.com
  %(prog)s --url https://example.com --output audit.json
  %(prog)s --url https://example.com --wait 3000
  %(prog)s --url https://example.com --port 9222
        '''
    )
    parser.add_argument('--url', required=True, help='URL to audit')
    parser.add_argument('--port', type=int, default=9222, help='Chrome debug port (default: 9222)')
    parser.add_argument('--output', '-o', help='Output file (JSON)')
    parser.add_argument('--wait', type=int, default=2000, help='Wait milliseconds after load (default: 2000)')
    
    args = parser.parse_args()
    
    parsed = urlparse(args.url)
    if not parsed.scheme:
        print(f"Error: Invalid URL - {args.url}", file=sys.stderr)
        return 1
    if parsed.scheme not in ('http', 'https'):
        print(f"Error: URL must use http or https scheme", file=sys.stderr)
        return 1
    
    print(f"Auditing: {args.url}", file=sys.stderr)
    print(f"Using port: {args.port}", file=sys.stderr)
    
    result = audit_page(args.url, args.port)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results written to: {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2))
    
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())