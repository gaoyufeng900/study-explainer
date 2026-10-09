#!/usr/bin/env python3
"""一次跑完全部出片扫描。

用法:
    python3 check_all.py a.pdf [b.pdf ...] [--md a.md b.md ...] [--heading-color 1D4ED8]

  --md 与 PDF 按顺序一一对应（可省略），用于代码块行数比对。
退出码: 0 = 全部干净; 1 = 至少一项有问题（逐条渲染原页确认后再下结论）
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(args):
    print("$ " + " ".join(Path(a).name for a in args[1:]), flush=True)
    return subprocess.run(args).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--md", nargs="*", default=[])
    ap.add_argument("--heading-color", action="append", default=[])
    a = ap.parse_args()
    py = sys.executable
    bad = 0
    bad |= run([py, str(HERE / "check_raw_tex_prose.py"), *a.pdfs]) != 0
    bad |= run([py, str(HERE / "check_raw_math.py"), *a.pdfs]) != 0
    colors = sum((["--color", c] for c in a.heading_color), [])
    bad |= run([py, str(HERE / "check_orphan_heading.py"), *colors, *a.pdfs]) != 0
    for i, pdf in enumerate(a.pdfs):
        extra = ["--md", a.md[i]] if i < len(a.md) else []
        bad |= run([py, str(HERE / "check_code_blocks.py"), pdf, *extra]) != 0
    print("\n" + ("❌ 有命中：逐条渲染原页确认" if bad else "✅ 全部扫描干净（仍需人工核对数学与覆盖）"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
