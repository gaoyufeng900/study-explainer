#!/usr/bin/env python3
"""未渲染数学扫描器 —— 出片验收用。

写于 2026-09-08，起因：F19R2 修孤悬标题时，Codex 新补的两条阅读导语里
把行内数学写成了裸括号 `(L^p)` 而不是 `\\(L^p\\)`，于是 PDF 里直接印出一个
脱字符「(L^p)」，和同一页正常排版的 L^p 上标并排出现。

现有的出片后检查抓不到它：裸 quad / 裸 TeX 两条正则都只找反斜杠命令，
而 `(L^p)` 一个反斜杠都没有；XeLaTeX 日志更是全零——对引擎来说这就是普通文字。
它也不是孤悬标题，check_orphan_heading.py 同样查不出。三者互相正交。

判定依据：XeLaTeX 排出的上标是抬高的字形，**正文字体的文本层里绝不会留下字面的 `^`**。
所以正文字体中出现 `^` 即为「数学没进数学模式」。

⚠️ 代码块与 verbatim 必须排除：数值分析卡里 `print("(1+2^-53)-1")` 和讲 Markdown
语法时引用的 `$x^2$` 都是正确内容。判别用**字体**——构建器把代码排成等宽
（Menlo / LMMono），正文是 LMRoman。初版没做这个区分，24 份成品里误报了 2 份。

分两级：
  ERROR（退出码 1）  正文字体中的字面 `^`。
  WARN （不影响退出码）裸 TeX 词（ell/infty/alpha…）与 `x_{...}` 花括号下标。
      这两类可能是正常内容——符号表的读法列就写着“ell p”“phi 一”——所以只提示。

用法:
    python3 check_raw_math.py <a.pdf> [b.pdf ...]
    python3 check_raw_math.py --strict <a.pdf>    # WARN 也算失败

退出码: 0 = 干净; 1 = 发现 ERROR; 2 = 用法错误

校准（2026-09-08，本项目 2_每周学习包 下全部 24 份成品）：
  20 份干净、4 份命中共 9 处，逐条原尺寸目检**全部为真缺陷，无误报**：
    泛函_D001_新版 p7 `(L^1)(L^∞)`、p8 `(ell^p)(ell^∞)`
    泛函_D010 p3 `(L^p)`×2｜泛函_D011 p12 `(L^p)`｜泛函_第01周包 p25 `^p\\{})`、p29
  三处等宽字体命中已正确排除，它们都是正确内容：
    数值_第01-02周包 p18 的 Python 输出、数值_02_上机课1 p11 讲 Markdown 语法时
    引用的 `$x^2$`、泛函_00 p2 作者刻意用行内代码写的 `C^1`/`c_{00}`。
  初版没做等宽区分，前两者被误报——**这条排除规则是校准出来的，不要删。**
"""
import re
import sys

MONO_HINTS = ("mono", "menlo", "courier", "consol", "typewriter", "tt")
TEX_WORD = re.compile(r"(?<![A-Za-z])(?:ell|infty|alpha|beta|gamma|delta|Delta|varepsilon|"
                      r"lambda|mu|sigma|chi|phi|psi|omega|Omega|rightarrow|Rightarrow|"
                      r"leq|geq|neq|subseteq|forall|exists|mathbb|mathcal|operatorname)"
                      r"(?![A-Za-z])")
BRACE_SUB = re.compile(r"[A-Za-z0-9]_\{")


def is_monospace(font_name):
    lowered = font_name.lower()
    return any(hint in lowered for hint in MONO_HINTS)


def scan(path):
    """返回 (页数, errors, warns)；元素为 (页码, 命中文本, 所在 span 文本)。"""
    import fitz
    doc = fitz.open(path)
    errors, warns = [], []
    for i, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    if not text.strip():
                        continue
                    if is_monospace(span["font"]):        # 代码块 / verbatim
                        continue
                    if "^" in text:
                        errors.append((i + 1, "^", text.strip()))
                    for pattern in (TEX_WORD, BRACE_SUB):
                        match = pattern.search(text)
                        if match:
                            warns.append((i + 1, match.group(0), text.strip()))
                            break
    pages = doc.page_count
    doc.close()
    return pages, errors, warns


def main(argv):
    paths = [a for a in argv[1:] if not a.startswith("--")]
    strict = "--strict" in argv
    if not paths:
        print(__doc__)
        return 2
    bad = 0
    for path in paths:
        pages, errors, warns = scan(path)
        name = path.rsplit("/", 1)[-1]
        if errors:
            bad = 1
            print(f"❌ {name}: {pages} 页，未渲染数学 {len(errors)} 处")
            for page_number, hit, text in errors:
                print(f"     p{page_number}  {hit!r}  {text[:78]}")
        else:
            print(f"✅ {name}: {pages} 页，正文无字面 ^")
        if warns:
            if strict:
                bad = 1
            print(f"   ⚠️  疑似裸 TeX 词/下标 {len(warns)} 处（需人工过目，符号表读法列属正常）")
            for page_number, hit, text in warns[:6]:
                print(f"     p{page_number}  {hit!r}  {text[:78]}")
            if len(warns) > 6:
                print(f"     …另有 {len(warns) - 6} 处")
    return bad


if __name__ == "__main__":
    sys.exit(main(sys.argv))
