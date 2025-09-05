#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Beautiful terminal search (regex + folders)

Usage:
  python pretty_grep.py --dirs ./path1 ./path2 ./path3 \
                        --pattern ".*word_to_find.*" \
                        [--ignore-case] [--whole-word]
                        [--include "*.py;*.txt"] [--exclude "*.min.js;*.map"]

Notes:
- If 'rich' is installed, you'll get color + tables + progress bars.
- Without 'rich', it gracefully falls back to simple ANSI output.
"""

import os
import re
import fnmatch
import sys
import time
import argparse
from typing import Iterable, List, Tuple, Optional

# ---------- Config ----------
DIRS = ["verl/models", "verl/trainer"]
PATTERN = ".*llama.*"
DEFAULT_IGNORES = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache"}

# ---------- Optional Rich import ----------
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TimeElapsedColumn, TextColumn
    from rich.text import Text
    from rich.rule import Rule
    from rich.theme import Theme
    RICH = True
    console = Console(theme=Theme({
        "path": "cyan",
        "dim": "grey58",
        "match": "bold underline #ffaa00",
        "header": "bold white",
        "ok": "green",
        "warn": "bold red"
    }))
except Exception:
    RICH = False
    # minimal fallback console
    class _Mini:
        def print(self, *a, **k): print(*a)
    console = _Mini()

# ---------- Helpers ----------
def compile_regex(pattern: str, ignore_case: bool, whole_word: bool) -> re.Pattern:
    flags = re.IGNORECASE if ignore_case else 0
    if whole_word:
        pattern = rf"\b(?:{pattern})\b"
    return re.compile(pattern, flags)

def iter_files(base: str, includes: List[str], excludes: List[str]) -> Iterable[str]:
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORES]
        for name in files:
            if includes and not any(fnmatch.fnmatch(name, pat) for pat in includes):
                continue
            if excludes and any(fnmatch.fnmatch(name, pat) for pat in excludes):
                continue
            yield os.path.join(root, name)

def highlight_line(line: str, regex: re.Pattern):
    if not RICH:
        # crude ANSI fallback: bold yellow for matches
        def repl(m): return f"\033[1;33m{m.group(0)}\033[0m"
        return regex.sub(repl, line.rstrip("\n"))
    # Rich highlight with spans
    t = Text(line.rstrip("\n"))
    for m in regex.finditer(line):
        t.stylize("match", m.start(), m.end())
    return t

def scan_file(path: str, regex: re.Pattern) -> Iterable[Tuple[int, int, str]]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for ln, raw in enumerate(fh, 1):
                found = False
                for m in regex.finditer(raw):
                    if not found:
                        # only compute once per line; still report first column
                        found = True
                        first_col = m.start() + 1
                        yield (ln, first_col, raw)
                        break
    except (OSError, UnicodeDecodeError):
        return

def format_globs(s: Optional[str]) -> List[str]:
    if not s:
        return []
    return [p.strip() for p in s.split(";") if p.strip()]

# ---------- Pretty output blocks ----------
def section_header(title: str):
    if RICH:
        console.print(Panel.fit(f"[header]{title}[/header]", border_style="dim"))
    else:
        bar = "-" * 25
        console.print(f"\n {bar} {title} {bar}\n")

def print_result_row(table, file_path, line_no, col_no, preview, shorten: int = 120):
    if RICH:
        from rich.text import Text
        # shorten preview but keep styling
        if isinstance(preview, Text):
            pv = preview if len(preview) <= shorten else preview[:shorten].append(" …", style="dim")
        else:
            pv = (preview[:shorten] + " …") if len(preview) > shorten else preview
        table.add_row(file_path, str(line_no), str(col_no), pv)
    else:
        console.print(f"{file_path}:{line_no}:{col_no}: {preview}")

def print_summary(total_files_scanned: int, total_matches: int, elapsed: float):
    if RICH:
        console.print(Rule(style="dim"))
        console.print(f"[ok]Done[/ok] • files scanned: {total_files_scanned} • matches: {total_matches} • elapsed: {elapsed:.2f}s")
    else:
        console.print(f"\n*{'-'*25}\nScanned {total_files_scanned} files • Matches: {total_matches} • Elapsed: {elapsed:.2f}s\n")

# ---------- Main ----------
def main():
    parser = argparse.ArgumentParser(description="Beautiful terminal regex search")
    # parser.add_argument("--dirs", nargs="+", required=True, help="Directories to search")
    # parser.add_argument("--pattern", required=True, help="Regex pattern")
    parser.add_argument("--ignore-case", action="store_true", help="Case insensitive")
    parser.add_argument("--whole-word", action="store_true", help="Word boundary match")
    parser.add_argument("--include", help='Semicolon-separated include globs, e.g. "*.py;*.txt"')
    parser.add_argument("--exclude", help='Semicolon-separated exclude globs, e.g. "*.min.js;*.map"')
    args = parser.parse_args()
    args.dirs = DIRS
    args.pattern = PATTERN

    includes = format_globs(args.include) or ["*"]  # by default include everything
    excludes = format_globs(args.exclude)

    try:
        regex = compile_regex(args.pattern, args.ignore_case, args.whole_word)
    except re.error as e:
        if RICH:
            console.print(f"[warn]Invalid regex:[/warn] {e}")
        else:
            console.print(f"Invalid regex: {e}")
        sys.exit(2)

    total_files_scanned = 0
    total_matches = 0
    t0 = time.time()

    # Optional fancy progress if Rich is present
    if RICH:
        progress = Progress(
            TextColumn("[dim]Scanning[/dim]"),
            BarColumn(),
            TextColumn("{task.completed} files"),
            TimeElapsedColumn(),
            transient=True,
            console=console,
        )
        progress.start()
    else:
        progress = None

    for d in args.dirs:
        section_header(d)
        if RICH:
            table = Table(show_header=True, header_style="bold", expand=True, show_lines=False, border_style="dim")
            table.add_column("File", style="path", no_wrap=True)
            table.add_column("Line", justify="center")
            table.add_column("Col", justify="center")
            table.add_column("Preview", overflow="fold")
        else:
            table = None

        # gather files, then iterate
        files = list(iter_files(d, includes, excludes))
        if progress:
            task_id = progress.add_task("", total=len(files))
        for f in files:
            total_files_scanned += 1
            # update progress
            if progress:
                progress.advance(task_id)

            for (ln, col, raw) in scan_file(f, regex):
                total_matches += 1
                preview = highlight_line(raw, regex)
                if table:
                    print_result_row(table, f, ln, col, preview)
                else:
                    print_result_row(None, f, ln, col, preview if isinstance(preview, str) else preview.plain)

        if RICH and table.row_count > 0:
            console.print(table)
        elif RICH and table.row_count == 0:
            console.print("[dim]No matches in this folder.[/dim]")

    if progress:
        progress.stop()

    print_summary(total_files_scanned, total_matches, time.time() - t0)

if __name__ == "__main__":
    main()