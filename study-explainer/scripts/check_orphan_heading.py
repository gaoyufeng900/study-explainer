#!/usr/bin/env python3
"""孤悬标题扫描器 —— 出片验收用。

写于 2026-09-08，起因：F19 的 FA-D011 交付时 p12 底部留了一个孤悬的一级标题
「16. p22-p23 Proposition：L^p 空间之间的关系」，正文全部落在 p13。
Codex 声称已逐页目检但漏了；XeLaTeX 日志七类警报也查不出这种问题
（它不是 overfull，排版引擎认为完全合法）。只能靠位置关系判定。

判定依据：构建器把各级标题排成彩色（默认认 0x1D4ED8 / 0x475569 两种标题色，
以及旧模板的 0x173A5E），正文为黑色。换模板就用 --color 传新标题色（十六进制）。
若某页除页眉、页码外的**最后一行**全部是标题色，则该页以标题结尾、正文在下一页
—— 即孤悬标题。

用法:
    python3 check_orphan_heading.py [--color 1D4ED8 ...] <a.pdf> [b.pdf ...]

退出码: 0 = 干净; 1 = 发现孤悬标题; 2 = 用法错误
"""
import sys

HEADING_COLORS = {0x1D4ED8, 0x475569, 0x173A5E}   # 构建器的标题色
HEADER_ZONE   = 70        # 顶部页眉带高度(pt)
FOOTER_ZONE   = 40        # 底部页码带高度(pt)
SAME_LINE_TOL = 2.0       # 同一行的 y 容差(pt)


def scan(path):
    import fitz
    doc = fitz.open(path)
    hits = []
    for i, page in enumerate(doc):
        height = page.rect.height
        items = []
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    y = span["bbox"][3]
                    if y < HEADER_ZONE:                          # 页眉
                        continue
                    if y > height - FOOTER_ZONE and text.isdigit():  # 页码
                        continue
                    items.append((y, span["size"], span["color"], text))
        if not items:
            continue
        items.sort(key=lambda it: it[0])
        y_last = items[-1][0]
        tail = [it for it in items if it[0] >= y_last - SAME_LINE_TOL]
        if all(it[2] in HEADING_COLORS for it in tail):
            title = "".join(it[3] for it in tail)
            size = max(it[1] for it in tail)
            hits.append((i + 1, round(size, 1), title))
    return doc.page_count, hits


def main(argv):
    global HEADING_COLORS
    custom = set()
    while len(argv) > 2 and argv[1] == "--color":
        custom.add(int(argv[2].lstrip("#"), 16))
        argv = [argv[0]] + argv[3:]
    if custom:
        HEADING_COLORS = custom
    if len(argv) < 2:
        print(__doc__)
        return 2
    bad = 0
    for path in argv[1:]:
        pages, hits = scan(path)
        name = path.rsplit("/", 1)[-1]
        if hits:
            bad = 1
            print(f"❌ {name}: {pages} 页，孤悬标题 {len(hits)} 处")
            for pn, size, title in hits:
                print(f"     p{pn}  size={size}  「{title}」")
        else:
            print(f"✅ {name}: {pages} 页，无孤悬标题")
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv))
