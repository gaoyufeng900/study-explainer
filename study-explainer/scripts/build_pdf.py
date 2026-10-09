#!/usr/bin/env python3
"""把讲解 markdown 编译成 iPad 友好的 PDF（pandoc + xelatex + ctexart）。

用法:
    python3 build_pdf.py 源码.md -o 成品.pdf [--head-left 文字] [--head-right 文字]
                         [--resource-path 目录1:目录2] [--header 自定义header.tex]

- markdown 支持 $...$ / \\(...\\) 数学、raw LaTeX、![图注](相对路径) 图片、``` 代码块。
- 中文字体按操作系统自动选（macOS 宋体/黑体，Windows 宋体/黑体，Linux Noto CJK），
  也可用环境变量 CJK_MAIN / CJK_SANS 指定字体名。
- 依赖：pandoc、xelatex（TeX Live / MacTeX）。找不到时会提示怎么装。
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_HEADER = HERE.parent / "assets" / "header.tex"

EXTRA_BIN = ["/opt/homebrew/bin", "/usr/local/bin", "/Library/TeX/texbin"]


def find(tool):
    path = shutil.which(tool)
    if path:
        return path
    for d in EXTRA_BIN:
        p = Path(d) / tool
        if p.exists():
            return str(p)
    return None


def cjk_fonts():
    main, sans = os.environ.get("CJK_MAIN"), os.environ.get("CJK_SANS")
    if main:
        return (f"\\setCJKmainfont[AutoFakeBold=2.2]{{{main}}}\n"
                f"\\setCJKsansfont[AutoFakeBold=2.2]{{{sans or main}}}")
    system = platform.system()
    if system == "Darwin":
        return ("\\setCJKmainfont[Path=/System/Library/Fonts/Supplemental/,AutoFakeBold=2.2]{Songti.ttc}\n"
                "\\setCJKsansfont[Path=/System/Library/Fonts/,AutoFakeBold=2.2]{STHeiti Medium.ttc}")
    if system == "Windows":
        return ("\\setCJKmainfont[AutoFakeBold=2.2]{SimSun}\n"
                "\\setCJKsansfont[AutoFakeBold=2.2]{SimHei}")
    return ("\\setCJKmainfont[AutoFakeBold=2.2]{Noto Serif CJK SC}\n"
            "\\setCJKsansfont[AutoFakeBold=2.2]{Noto Sans CJK SC}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("md")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--head-left", default="")
    ap.add_argument("--head-right", default="")
    ap.add_argument("--resource-path", default="")
    ap.add_argument("--header", default=str(DEFAULT_HEADER))
    args = ap.parse_args()

    pandoc, xelatex = find("pandoc"), find("xelatex")
    if not pandoc or not xelatex:
        print("缺少工具：" + "、".join(n for n, p in [("pandoc", pandoc), ("xelatex", xelatex)] if not p))
        print("macOS：brew install pandoc；xelatex 装 MacTeX（https://tug.org/mactex/）或 brew install --cask basictex")
        print("Windows：装 pandoc（https://pandoc.org/installing.html）和 TeX Live / MiKTeX")
        return 2

    md = Path(args.md).resolve()
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    header_src = Path(args.header).read_text(encoding="utf-8")
    header_src = (header_src.replace("__CJK_FONTS__", cjk_fonts())
                  .replace("__HEAD_L__", args.head_left)
                  .replace("__HEAD_R__", args.head_right))

    resource = [str(md.parent)] + [p for p in args.resource_path.split(os.pathsep) if p]
    with tempfile.TemporaryDirectory() as tmp:
        header = Path(tmp) / "header.tex"
        header.write_text(header_src, encoding="utf-8")
        env = dict(os.environ)
        env["PATH"] = os.pathsep.join([str(Path(xelatex).parent), env.get("PATH", "")])
        cmd = [
            pandoc, str(md), "--from=markdown+raw_tex+tex_math_single_backslash",
            f"--pdf-engine={xelatex}", "--standalone",
            "--include-in-header", str(header),
            "--resource-path", os.pathsep.join(resource),
            "-V", "documentclass=ctexart", "-V", "classoption=fontset=none",
            "-V", "classoption=11pt",
            "-V", "geometry:top=16mm", "-V", "geometry:bottom=16mm",
            "-V", "geometry:left=18mm", "-V", "geometry:right=18mm",
            "-V", "colorlinks=true", "-V", "linkcolor=navblue",
            "-o", str(out),
        ]
        r = subprocess.run(cmd, cwd=md.parent, env=env)
    if r.returncode != 0:
        print("❌ 编译失败。常见原因：md 里有 emoji、字体名不对、图片路径含空格找不到、反斜杠被吃掉。")
        return r.returncode
    print(f"OK {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
