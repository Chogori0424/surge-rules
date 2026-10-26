#!/usr/bin/env python3
"""Build Surge rule lists from v2fly/domain-list-community.

Each output in sources.json lists v2fly data files to include (resolving
nested `include:`) and optionally files to exclude. `"exclude_outputs": "*"`
drops every rule already present in another output, which keeps a catch-all
list from overlapping the per-service ones. Rules in custom/<Name>.list are
appended as-is. Output goes to rules/<Name>.list.
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/"

_cache = {}


def fetch(name):
    if name not in _cache:
        with urllib.request.urlopen(UPSTREAM + name, timeout=30) as resp:
            _cache[name] = resp.read().decode("utf-8")
    return _cache[name]


def attrs_ok(attrs, want):
    for a in want:
        if a.startswith("-"):
            if a[1:] in attrs:
                return False
        elif a not in attrs:
            return False
    return True


def parse(name, want=(), seen=None):
    """Yield (type, value) entries of a v2fly list, following includes."""
    seen = set() if seen is None else seen
    if name in seen:
        return
    seen.add(name)
    for raw in fetch(name).splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        entry, attrs = parts[0], {p[1:] for p in parts[1:] if p.startswith("@")}
        if entry.startswith("include:"):
            sub = entry[len("include:"):]
            sub_want = [p[1:] for p in parts[1:] if p.startswith("@")]
            yield from parse(sub, sub_want, seen)
            continue
        if not attrs_ok(attrs, want):
            continue
        kind, _, value = entry.rpartition(":")
        yield (kind or "domain", value)


def to_surge(kind, value):
    if kind == "domain":
        return f"DOMAIN-SUFFIX,{value}"
    if kind == "full":
        return f"DOMAIN,{value}"
    if kind == "keyword":
        return f"DOMAIN-KEYWORD,{value}"
    if kind == "regexp":
        # Surge has no domain regex; translate the simple `\S+` / `\d+` cases to a wildcard.
        m = re.fullmatch(r"\^?(.*?)\$?", value)
        wild = re.sub(r"\\[Sd][+*]", "*", m.group(1)).replace("\\.", ".")
        if re.fullmatch(r"[A-Za-z0-9.*-]+", wild):
            return f"DOMAIN-WILDCARD,{wild}"
        print(f"skip regexp: {value}", file=sys.stderr)
    return None


def collect(name, spec):
    excluded = set()
    for ex in spec.get("exclude", []):
        excluded.update(parse(ex))
    rules = []
    for inc in spec["include"]:
        for entry in parse(inc):
            if entry in excluded:
                continue
            rule = to_surge(*entry)
            if rule and rule not in rules:
                rules.append(rule)
    custom = ROOT / "custom" / f"{name}.list"
    if custom.exists():
        for line in custom.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and line not in rules:
                rules.append(line)
    return rules


def render(name, spec, rules):
    order = {"DOMAIN": 0, "DOMAIN-SUFFIX": 1, "DOMAIN-WILDCARD": 2, "DOMAIN-KEYWORD": 3}
    rules.sort(key=lambda r: (order.get(r.split(",")[0], 9), r))
    header = [
        f"# NAME: {name}",
        f"# SOURCE: v2fly/domain-list-community ({', '.join(spec['include'])})",
        f"# UPDATED: {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC",
        f"# TOTAL: {len(rules)}",
    ]
    return "\n".join(header + rules) + "\n"


def main():
    sources = json.loads((ROOT / "sources.json").read_text())
    out_dir = ROOT / "rules"
    out_dir.mkdir(exist_ok=True)
    collected = {n: collect(n, s) for n, s in sources.items()}
    for name, spec in sources.items():
        if spec.get("exclude_outputs") == "*":
            others = {r for n, rs in collected.items() if n != name and sources[n].get("exclude_outputs") != "*" for r in rs}
            collected[name] = [r for r in collected[name] if r not in others]
    for name, spec in sources.items():
        text = render(name, spec, collected[name])
        path = out_dir / f"{name}.list"
        old = path.read_text() if path.exists() else ""
        # Ignore the timestamp line so unchanged lists don't produce commits.
        strip = lambda t: [l for l in t.splitlines() if not l.startswith("# UPDATED")]
        if strip(old) != strip(text):
            path.write_text(text)
            print(f"updated {path.name}: {text.count(chr(10)) - 4} rules")
        else:
            print(f"unchanged {path.name}")


if __name__ == "__main__":
    main()
