# 出片工程

## 1. 现行管线

markdown（`markdown+raw_tex`，`$…$` 和 `\(…\)` 两种行内公式都认）→ pandoc → xelatex，文档类 `ctexart`（`fontset=none`，字体在 header 里指定）。

```bash
python3 scripts/build_pdf.py 源码.md -o 成品.pdf \
  --head-left "课程 · 主题" --head-right "本册名" [--resource-path 图片目录]
```

- `assets/header.tex`：标题蓝色，页眉文字和中文字体由 `build_pdf.py` 按参数和操作系统填进去，三种提示命令 `\intuition{}` `\keypoint{}` `\warning{}`，①–⑤ 圆圈数字映射。
- 需要 pandoc 和 xelatex。macOS：`brew install pandoc`，TeX 装 MacTeX 或 `brew install --cask basictex`（basictex 缺包时 `sudo tlmgr install ctex fancyhdr titlesec needspace`）。Windows：pandoc 官网安装包 + TeX Live 或 MiKTeX。脚本会在 PATH 和常见安装位置里找。
- **没有 pandoc 的机器**：只能走自写的 md→LaTeX 转换脚本，记得它要处理代码围栏（用 Verbatim），否则代码块会被压扁。

## 2. 常见坑

- **emoji 不能进 LaTeX**（没有彩色 emoji 字体，报 Missing character）。md 里可以留，出片前替换成文字或彩色竖条。
- 字体：脚本按系统自动选（macOS 宋体/华文黑体，Windows SimSun/SimHei，Linux Noto CJK）。报找不到字体时用环境变量指定：`CJK_MAIN="字体名" CJK_SANS="字体名" python3 build_pdf.py …`（`fc-list :lang=zh` 能列出可用中文字体）。
- **iCloud 路径有空格和中文**：图片引用会让 xelatex 出错，构建时把图拷到 `tmp/build/` 用 ASCII 名，或用 `--resource-path`。
- 写 md 时用编辑工具直接改文件，不要经 shell heredoc / Python 字符串转写——反斜杠会被吃掉，`\(x_k\)` 变成 `(x_k)`。
- 编译后看日志：不得有 Missing character、严重 Overfull；连编两遍稳定交叉引用。
- 中间件放 `_系统/tmp/build/`，不要混进源码目录；成品目录只放 PDF。

## 3. 源图嵌入

图是内容不是装饰：题图、物理受力图/电路图、几何构型、围道等必须嵌原图。
- 渲染：PyMuPDF `page.get_pixmap(dpi=220)` 或 `gs -sDEVICE=png16m -r220`，Pillow 按区域裁剪；有效分辨率 ≥150 dpi；不带入相邻题干、页码。
- 资产放 `_系统/源码md/<课程>/figs/<产物名>/`，md 里相对引用；图注写来源页（`图：源《第10章》p.12`）。
- 原图太糟可用 TikZ/matplotlib 忠实重绘，图注标「重绘」，不得增删信息。
- 自己画的直觉图（现行写法要求「能画就画」）：要简单，一图只说一件事。

## 4. 渲染抽查

```python
import fitz
doc = fitz.open("成品.pdf")
for i in [0, 5, 12]:
    doc[i].get_pixmap(dpi=110).save(f"p{i+1}.png")
```
多页可拼成联系图（contact sheet）一次看完。PyMuPDF 没装就 `pip install pymupdf`。

## 5. notebook 作业转 PDF（交作业用）

`jupyter nbconvert --to html` → headless Chrome `--print-to-pdf --virtual-time-budget=20000`（等 MathJax 渲染完，否则公式显示成 `$` 源码）。
