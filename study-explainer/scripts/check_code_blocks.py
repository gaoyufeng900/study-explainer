#!/usr/bin/env python3
"""代码块被压扁检查 —— 出片验收用。

起因（2026-09-29）：一批上机卡 25 个 ``` 代码块在 PDF 里全部变成普通段落
（`python`/`text` 语言标记漏出来、换行缩进丢失）。执行方自报「逐页目检通过」，
其余扫描器也查不出——根因是用了不处理代码围栏的构建器。

两项检查：
  1. PDF 文字层里不得有以 "python "/"text "/"bash " 开头的行（语言标记漏出）。
  2. 给了 --md 时：md 里代码块的总行数，应 ≈ PDF 等宽字体的行数（少于 80% 视为被压扁）。

用法:
    python3 check_code_blocks.py 成品.pdf [--md 源码.md]
退出码: 0 = 干净; 1 = 有问题
"""
import argparse
import re
import sys

import fitz

LEAK = re.compile(r"^(python|text|bash|py|sh)\s+\S")
CODE_FONTS = ("Menlo", "Mono", "mono", "Courier")


def pdf_stats(path):
    leaks, mono_lines = [], 0
    for pno, page in enumerate(fitz.open(path), 1):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = "".join(s["text"] for s in line["spans"]).strip()
                if LEAK.match(text) and not any(k in spans[0]["font"] for k in CODE_FONTS):
                    leaks.append((pno, text[:60]))
                if all(any(k in s["font"] for k in CODE_FONTS) for s in spans):
                    mono_lines += 1
    return leaks, mono_lines


def md_code_lines(path):
    n, inside = 0, False
    for line in open(path, encoding="utf-8"):
        if line.lstrip().startswith("```"):
            inside = not inside
            continue
        if inside and line.strip():
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--md")
    a = ap.parse_args()
    leaks, mono = pdf_stats(a.pdf)
    bad = False
    name = a.pdf.rsplit("/", 1)[-1]
    if leaks:
        bad = True
        print(f"❌ {name}: 语言标记漏出 {len(leaks)} 处（代码块被当成普通段落）")
        for p, t in leaks[:10]:
            print(f"     p{p}  「{t}」")
    if a.md:
        want = md_code_lines(a.md)
        if want and mono < 0.8 * want:
            bad = True
            print(f"❌ {name}: md 代码 {want} 行，PDF 等宽字体只有 {mono} 行 —— 代码块被压扁")
    if not bad:
        print(f"✅ {name}: 代码块正常（等宽 {mono} 行）")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
