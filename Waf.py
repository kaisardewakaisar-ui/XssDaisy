#!/usr/bin/env python3
# XssDaisy - WAF Detection Module
# Author: KaisarYetiandi | github.com/KaisarYetiandi | t.me/Darkness_Lock

import os
from wafw00f.main import WAFW00F
from rich.console import Console

console = Console()

class Waf_Detect:
    def __init__(self, url):
        self.url = url
        self.waf_file = os.path.join(os.path.dirname(__file__), 'waf_list.txt')

    def waf_detect(self):
        try:
            wafw00f = WAFW00F(self.url)
            result = wafw00f.identwaf()
            if not result:
                return None
            result_str = result[0].lower()
        except Exception as e:
            console.print(f"[yellow][[!]] WAF detection error: {e}[/yellow]")
            return None

        for waf in self.fetch_names():
            if waf in result_str:
                return waf
        return None

    def fetch_names(self):
        try:
            with open(self.waf_file, 'r') as f:
                return [line.strip().lower() for line in f if line.strip()]
        except FileNotFoundError:
            return []


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else 'http://testphp.vulnweb.com/'
    detected = Waf_Detect(target).waf_detect()
    if detected:
        console.print(f"[bold red][[+]] WAF Detected: {detected.upper()}[/bold red]")
    else:
        console.print("[bold green][[+]] No WAF detected[/bold green]")
