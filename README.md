# study-explainer

把老师发的讲义、课件、作业、上机题单，做成「零基础也能自学」的中文讲解 PDF 的工作流，打包成 AI 编程助手的 skill。

这里有两个版本：

| 目录 | 给谁 | 分工 | 语言 |
|---|---|---|---|
| [`study-explainer-codex/`](study-explainer-codex/) | 只用 Codex 的人 | Codex 一个人从整理材料做到出 PDF、自查、交付 | 全中文 |
| [`study-explainer/`](study-explainer/) | Claude Code + Codex 搭配用 | Claude 定规范、写任务书派活、验收；Codex 生成 | 中文 |

两个版本的脚本相同：

- `scripts/build_pdf.py`：markdown → PDF（pandoc + xelatex + ctexart，按操作系统自动选中文字体）
- `scripts/check_all.py`：一次跑完四项出片扫描——正文里的 TeX 生码、未渲染的 `^`、孤悬标题、被压扁的代码块。这些问题排版引擎不报警、肉眼翻页必漏。

## 在 Codex 里安装（全中文版）

在 Codex 对话框里直接说：

```text
用 skill-installer 安装这个 skill：https://github.com/gaoyufeng900/study-explainer/tree/main/study-explainer-codex
```

装完**重启 Codex**（或新开一个对话），之后说「帮我把这份作业做成讲解」之类的话就会自动用上；也可以在输入框打 `$study-explainer-codex` 点名使用。

手动安装（等价）：

```bash
git clone https://github.com/gaoyufeng900/study-explainer.git /tmp/study-explainer
mkdir -p ~/.codex/skills
cp -R /tmp/study-explainer/study-explainer-codex ~/.codex/skills/
```

出 PDF 需要 pandoc 和 xelatex（macOS：`brew install pandoc` + MacTeX）；第一次用时 Codex 会检查，缺了会告诉你怎么装。

## 在 Claude Code 里安装

```bash
git clone https://github.com/gaoyufeng900/study-explainer.git ~/src/study-explainer
ln -s ~/src/study-explainer/study-explainer ~/.claude/skills/study-explainer
```

## 更新

`git pull`（手动装的重新 `cp` 一次）；用 skill-installer 装的，先删掉 `~/.codex/skills/study-explainer-codex` 再装一次。

## 许可

MIT
