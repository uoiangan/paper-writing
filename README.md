# Paper Writing

面向 Codex 和 Claude Code 的论文写作技能，适用于课程论文、实验报告、文献综述和投稿稿件。它规定如何执行写作、修订、排版和核验。编译、文档渲染与联网检索由运行代理的环境提供。

## 安装技能

可以直接克隆本仓库，或从 GitHub 下载 ZIP 并解压。将整个目录命名为 `paper-writing`，保留 `SKILL.md`、`references/`、`assets/` 和 `scripts/` 的相对位置。

| 客户端 | 当前项目 | 当前用户 |
| --- | --- | --- |
| Codex | `.agents/skills/paper-writing/` | `~/.agents/skills/paper-writing/` |
| Claude Code | `.claude/skills/paper-writing/` | `~/.claude/skills/paper-writing/` |

在 Windows 上，`~` 指当前用户目录。同时使用两个客户端时，可以保留一份技能目录，另一个客户端通过目录链接访问。重新打开会话后，在 Codex 中输入 `$paper-writing`，或在 Claude Code 中运行 `/paper-writing`，再说明任务。详细的技能发现规则见 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills) 和 [Claude Code 技能文档](https://code.claude.com/docs/en/skills)。

## 按任务配置环境

先确认代理能读取课程或投稿要求、模板和原始资料，能写入论文项目目录，并能调用本次需要的命令。远程运行时，工具和字体也要安装在远程环境里。

| 要做的事 | 需要配置 |
| --- | --- |
| 只写或改 Markdown / 纯文本 | 能读写文件的代理与 UTF-8 文本环境。 |
| LaTeX 成稿 | [TeX Live](https://ctan.org/pkg/texlive) 或 [MiKTeX](https://miktex.org/download)，含 `xelatex`、`ctex` 及所用模板的宏包。默认模板另需 `biblatex`、`biber` 和 [`biblatex-gb7714-2015`](https://ctan.org/pkg/biblatex-gb7714-2015)。 |
| Word 成稿 | 能编辑 DOCX 的工具。模板依赖原生公式、题注、交叉引用或精确分页时，优先使用桌面 Word 打开、更新受影响的域并导出 PDF。只有其他渲染器时，核对字体、行距、页码和分页，并说明最终用哪一个渲染。[Word 导出 PDF 说明](https://support.microsoft.com/en-us/office/collab-files/save-or-convert-to-pdf-or-xps-in-office-desktop-apps) |
| PDF 目检 | [Poppler](https://poppler.freedesktop.org/) 的 `pdftoppm` 用来逐页渲染，`pdffonts` 检查字体嵌入，`pdftohtml` 可辅助抽查字号。也可使用能覆盖相同检查的 PDF 工具。 |
| 可选的中文行文扫描 | [Python 3.8+](https://www.python.org/downloads/)，脚本只用标准库。需要从 DOCX 提取纯文本时，可用 [Pandoc](https://pandoc.org/installing.html) 或手工提取正文。 |
| 摘要和文献的独立核验 | 配置可委派独立只读子代理的客户端，以及能访问出版方、DOI、文献数据库或项目原件的工具。学校订阅资料须有相应访问权限。 |
| 读取扫描件、手写要求或截图 | 配置能读图或做 OCR 的工具。规则中提到的 `adaptive-vision-skill`、DOCX 和 PDF 技能需另行提供，也可使用客户端已有的等效能力。 |

中英文字体按用户要求或目标模板配置。字体缺失时，渲染结果可能自动替换字体，改变分页或出现缺字。终端找不到工具时，把**当前机器**的安装目录加入 `PATH`，再从代理使用的终端验证。仓库不需要专用 API 密钥；联网检索可用客户端自带工具或可访问的文献服务。子代理不可用时仍可逐项核对，但应说明哪些内容未经过独立复核。细则见 [文献与摘要核验](references/verification.md)。

## 安装后自检

在代理使用的终端里，只检查你选择的工具。Windows 上如果 Python 通过启动器提供，可将 `python` 换成 `py -3`。

```text
xelatex --version
biber --version
pdftoppm -v
pdffonts -v
python --version
pandoc --version
```

TeX Live 用户可用 `kpsewhich ctexart.cls` 和 `kpsewhich gb7714-2015.bbx` 检查宏包。MiKTeX 用户可在 MiKTeX Console 的 Packages 页面检查 `ctex` 和 `biblatex-gb7714-2015`。

### LaTeX 模板试编译

在空白项目目录中，将 [模板](assets/template-ctexart.tex) 复制为 `main.tex`，将 [示例文献库](assets/refs-sample.bib) 复制为 `refs.bib`。文件名要与模板内的引用配置对应。然后在该目录运行：

```sh
xelatex -interaction=nonstopmode -halt-on-error main.tex
biber main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
pdftoppm -png -r 110 main.pdf page
pdffonts main.pdf
```

检查 PDF 是否生成、中文和引文是否正常，日志里是否有未解析的引用或缺字，再逐页查看分页。无文献或手写 `thebibliography` 的稿件可跳过 Biber，并运行两遍 XeLaTeX。示例参考文献只用于试编译，交付前请换成实际经过核验的来源。更多检查见 [编译与目检](references/build-check.md)。

### Word 与中文扫描试运行

用一份小型 DOCX 测试打开、保存和导出 PDF。如果正文需要原生公式、编号或交叉引用，顺便验证这些对象仍能在 Word 中编辑，且导出的页码与图表正确。仅在需要行文扫描时，将中文正文保存为 UTF-8 的 `body.txt`，在技能目录中运行：

```sh
python scripts/style-scan.py body.txt
```

由 DOCX 转写时可先运行 `pandoc report.docx -t plain -o body.txt`，再从文本中去掉封面、题注与文献列表。脚本只提供中文行文统计和编辑线索。[行文自查说明](references/ai-check.md)

## 开始第一项任务

告诉代理这是新写、局部修改还是纯排版，提供目标模板、交付格式和可用证据。示例：

> 用 Paper Writing 按我提供的模板写实验报告。实测图保留在对应分析旁边，报告只依据附件和指导书，交可编辑 DOCX 与 PDF。没有的实验参数标成待补。

任务入口见 [SKILL.md](SKILL.md)。

## 许可证

本仓库采用 [MIT 许可证](LICENSE)。
