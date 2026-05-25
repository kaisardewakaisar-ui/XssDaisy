#!/usr/bin/env python3
# XssDaisy - Payload Manager
# Author: KaisarYetiandi | github.com/KaisarYetiandi | t.me/Darkness_Lock

import os, json
from optparse import OptionParser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

class Adder:
    def __init__(self):
        self.dangerous_characters = ['>', "'", '"', '<', '/', ';']
        self.payload_file = os.path.join(os.path.dirname(__file__), 'payloads.json')

    def _load(self):
        with open(self.payload_file, 'r') as f:
            return json.load(f)

    def _save(self, data):
        with open(self.payload_file, 'w') as f:
            json.dump(data, f, indent=4)

    def _build_entry(self, payload, waf=None):
        payload = payload.strip()
        attrs = list({c for c in payload if c in self.dangerous_characters})
        return {"Payload": payload, "Attribute": attrs, "count": 0, "waf": waf}

    def add_payload(self, payload=None, filename=None, waf=None):
        if waf:
            waf = waf.lower()
        data = self._load()
        added = 0

        if filename:
            with open(filename, 'r') as f:
                lines = [l.strip() for l in f if l.strip()]
            for line in lines:
                entry = self._build_entry(line, waf)
                # Avoid duplicates
                if not any(d['Payload'].strip() == entry['Payload'] for d in data):
                    data.append(entry)
                    added += 1
        elif payload:
            entry = self._build_entry(payload, waf)
            if not any(d['Payload'].strip() == entry['Payload'] for d in data):
                data.append(entry)
                added = 1
            else:
                console.print("[yellow][[!]][/yellow] Payload already exists — skipped.")
                return

        self._save(data)
        console.print(f"[bold #39ff14][[+]][/bold #39ff14] [bold white]{added}[/bold white] payload(s) added successfully.")

    def list_payloads(self, waf_filter=None):
        data = self._load()
        tbl = Table(
            title="[bold #b060ff]XssDaisy Payload Library[/bold #b060ff]",
            box=box.SIMPLE_HEAVY,
            border_style="#6e40c9",
            header_style="bold #b060ff"
        )
        tbl.add_column("#",        width=4,  style="dim")
        tbl.add_column("Payload",  style="bold green", max_width=60)
        tbl.add_column("Chars",    style="yellow")
        tbl.add_column("WAF",      style="cyan")

        shown = 0
        for i, p in enumerate(data, 1):
            w = p.get('waf') or 'generic'
            if waf_filter and w != waf_filter.lower():
                continue
            tbl.add_row(str(i), p['Payload'][:58], ', '.join(p['Attribute']), w)
            shown += 1

        console.print(tbl)
        console.print(f"[dim]Total: {shown} payloads shown[/dim]")

    def remove_payload(self, index):
        data = self._load()
        if index < 1 or index > len(data):
            console.print("[red][[!]] Invalid index.[/red]")
            return
        removed = data.pop(index - 1)
        self._save(data)
        console.print(f"[bold #39ff14][[+]][/bold #39ff14] Removed: [dim]{removed['Payload'][:60]}[/dim]")

    def reset_counts(self):
        data = self._load()
        for p in data:
            p['count'] = 0
        self._save(data)
        console.print("[bold #39ff14][[+]][/bold #39ff14] Payload hit-counts reset.")


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel(
        "[bold #b060ff]XssDaisy[/bold #b060ff] — Payload Manager\n"
        "[dim]Author: KaisarYetiandi | github.com/KaisarYetiandi[/dim]",
        border_style="#6e40c9"
    ))

    parser = OptionParser()
    parser.add_option("-p", dest="payload",  help="Single payload string")
    parser.add_option("-f", dest="filename", help="File with payloads (one per line)")
    parser.add_option("-w", dest="waf",      help="Associate with WAF (e.g. cloudflare)")
    parser.add_option("-l", dest="list",     action="store_true", help="List all payloads")
    parser.add_option("--waf-filter", dest="waf_filter", help="Filter list by WAF name")
    parser.add_option("--remove", dest="remove", type="int", help="Remove payload by index number")
    parser.add_option("--reset",  dest="reset",  action="store_true", help="Reset all hit counters")

    val, _ = parser.parse_args()
    adder = Adder()

    if val.list:
        adder.list_payloads(val.waf_filter)
    elif val.remove:
        adder.remove_payload(val.remove)
    elif val.reset:
        adder.reset_counts()
    elif val.payload or val.filename:
        adder.add_payload(payload=val.payload, filename=val.filename, waf=val.waf)
    else:
        parser.print_help()
