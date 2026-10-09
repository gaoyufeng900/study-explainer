#!/usr/bin/env python3
"""扫描 PDF 正文（排除代码等宽字体）里未渲染的 TeX 生码。

用法：python3 check_raw_tex_prose.py a.pdf [b.pdf ...]
退出码：有命中则 1。

背景（2026-09-29）：Codex 写 md 时多次丢掉行内公式的反斜杠，
`\\(x_k\\)` 变成 `(x_k)`，PDF 里直接显示生码。只搜 `_{` 会漏掉
`(x_k)`、`(a\\leftarrow c)`、`(1,0)^T` 这类写法；代码字体（Menlo 等）里的
`x_new`、`A_neg` 是合法变量名，必须排除，否则误报成百上千。
"""
import re
import sys

import fitz

PATTERN = re.compile(
    r"[_^]\{"                      # x_{k+1}  s^{2}
    r"|\\[a-zA-Z]{2,}"             # \lambda  \leftarrow
    r"|\)\^T|\^\("                 # (1,0)^T  x^(k)
    r"|(?<![A-Za-z0-9_`])[a-zA-Z]_[a-zA-Z0-9](?![A-Za-z0-9_])"  # x_k  a_j
)
CODE_FONTS = ("Menlo", "Mono", "mono", "Courier")


def scan(path):
    hits = []
    for page_no, page in enumerate(fitz.open(path), 1):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if any(k in span["font"] for k in CODE_FONTS):
                        continue
                    text = span["text"]
                    for m in PATTERN.finditer(text):
                        hits.append((page_no, text[max(0, m.start() - 12): m.end() + 10]))
    return hits


def main(paths):
    bad = 0
    for path in paths:
        hits = scan(path)
        name = path.rsplit("/", 1)[-1]
        if hits:
            bad += 1
            print(f"❌ {name}: {len(hits)} 处正文 TeX 生码")
            for page_no, ctx in hits[:8]:
                print(f"     p{page_no}  {ctx!r}")
        else:
            print(f"✅ {name}: 正文无 TeX 生码")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
