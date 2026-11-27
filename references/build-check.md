# 编译与目检

## 一、LaTeX（默认路径）

### 编译

默认路径是 biblatex + biber + GB/T 7714-2015，按下面顺序编译，缺一步都会出现 `??` 或编号错乱：

```bash
xelatex -interaction=nonstopmode main.tex
biber main
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

- biber 后运行两遍 XeLaTeX，确认引用、目录和页码已稳定。
- 手写 `thebibliography` 或无参考文献时，运行 XeLaTeX 两遍。
- BibTeX 旧模板先 XeLaTeX 生成辅助文件，再 `bibtex main`，最后 XeLaTeX 两遍。

Windows PowerShell 中找不到 `xelatex` 时，MiKTeX 用户级默认安装可以临时加入当前会话的 `PATH`：

```powershell
$miktexBin = Join-Path $env:LOCALAPPDATA 'Programs\MiKTeX\miktex\bin\x64'
if (Test-Path -LiteralPath (Join-Path $miktexBin 'xelatex.exe') -PathType Leaf) {
    $env:Path = "$miktexBin;$env:Path"
}
```

如果是系统级、自定义安装或使用 TeX Live，请将实际包含 `xelatex` 的目录加入 `PATH`，再用 `xelatex --version` 确认。

### 查错

- `.log` 里搜 `^!`：任何一条都是错误，必须修。
- 搜 `Overfull \hbox`：超过 5pt 的都要看；表格和公式最常见。
- 搜 `undefined references`、`Citation ... undefined`：交叉引用没解析，通常是少跑一遍或拼写错误。
- 搜 `Missing character`：字体缺字，中文常见于生僻字或特殊符号。

### 目检

把 PDF 转成图片，逐页看版式（本机无浏览器时这是唯一可靠办法）：

```bash
pdftoppm -png -r 110 main.pdf page
```

检查：分页是否合理、图表是否错位、公式是否溢出、页眉页脚是否正常、中文字体是否嵌入。

```bash
pdffonts main.pdf
```

字体列表里不应出现 `Type 3` 或大量 `no` 嵌入。

### 参考文献与 .bbl

生成 PDF 后不要只看 `refs.bib`，要检查 biber 实际输出的 `main.bbl`：

- **publisher / 机构名含 `and` 必须加双大括号**：

  ```bibtex
  publisher = {{Society for Industrial and Applied Mathematics}}
  ```

  否则 BibTeX 把 `and` 当人名分隔，PDF 只剩 “Society for Industrial”。
- 检查截断：`grep -o "publisher{[^}]*}" main.bbl`，逐条确认完整。
- 检查未引用条目：biber 的 `WARN - I didn't find a database entry for` 与正文 `\cite` 对照；未被引用的条目要么删，要么补引。
- 文献类型标识及 DOI 著录按实际来源与所选体例判断。
- 最后一页只剩少量文献时，按页数上限和模板选择是否调整分页。整组另起一页只在适用时考虑，并重新核对页数。

### 字号与字体验证

用户指定了字号时，不能只看源码，要在 PDF 里量：

```bash
pdftohtml -xml -stdout main.pdf | grep -o '<fontspec[^>]*>' | sort -u
```

`size` 是 pdftohtml 的缩放单位（默认 1.5 倍），除以 1.5 得到 pt。例如 `size=16` 约为 10.7pt，对应五号。逐个核对摘要、正文、参考文献、题注。

- `TU/SimHei(0)/b/n`、`TU/SimSun(1)/b/n` 的 `Font shape ... undefined` 警告：SimHei/SimSun 没有粗体字形，`\bfseries` 使用伪粗体。显示正常，属预期；要消除可换思源黑体/宋体。

## 二、DOCX

### 新建和修改

- 新建 DOCX 时，优先使用现有模板的命名样式；需要新建样式时集中设置。
- 新建且需要编辑的公式用原生 OMML，核对交付文件能继续编辑。局部修改或纯排版保留既有公式对象。

局部修改或纯排版保留既有模板、段落和字段结构。仅更新本次受影响的字段，并核对更新后的编号与分页。

### 样式映射

| 元素 | Word 样式名 | 默认取值 |
|---|---|---|
| 正文 | 正文 / Normal | 宋体 + Times New Roman，小四（12pt），行距固定值 22pt，首行缩进 2 字符 |
| 一级标题 | Heading 1 | 黑体，小三（15pt），段前 12pt、段后 6pt |
| 二级标题 | Heading 2 | 黑体，四号（14pt），段前 6pt、段后 3pt |
| 图表题注 | Caption | 宋体，五号（10.5pt），居中 |
| 参考文献 | 自定义「参考文献」 | 宋体 + Times New Roman，五号，悬挂缩进 2 字符 |

- 中文字体和西文字体要分别设置（Word「字体」对话框的「中文/西文」两栏），否则数字和英文会跟着宋体走。
- 行距优先用「固定值」；不同 Word 版本的 1.5 倍行距渲染不一致，页数会对不上。
- 全部样式改在「样式」面板里改，不要在正文里选中文字单独改——后者会在粘贴、重排时被覆盖。

### 题注与交叉引用

- 新增题注和交叉引用时优先使用 Word 字段，沿用模板的编号方式。
- 表题在表上方、图题在图下方，与 `aesthetics.md` 一致。
- 表格用三线表：只保留顶线、表头线、底线，用「边框和底纹」手动设，不套 Word 内置彩色表格样式。
- 表格跨页时勾选「允许跨页断行」，并把表头行设为「重复标题行」。

### 目录与分节

- 仅在模板规定或稿件需要时设置封面、目录与分节；页码体例按模板或现有文档。
- 新建目录使用 Word 的目录字段。有目录且本轮影响页码时更新该字段，再对照正文核对。

### 参考文献

- 首选 Word 的引文域（配合 EndNote / Zotero 插件）；没有插件时手工维护编号，但必须保证正文编号与文末条目一一对应。
- 不要用 Word 的自动编号列表维护参考文献：插入或删除条目会重排，正文里的数字不会跟着变。
- 条目风格按项目确定的引用体例；GB/T 7714 顺序编码制下，正文用方括号编号或上标，全篇统一一种。

### 检查

- 转成 PDF 后数实际页数，不能按字数估算。
- 检查：目录页码、图表编号连续、页眉页脚、分节、样式是否被粘贴内容覆盖（选中段落看样式名是否仍是「正文」）。
- 用「查找 → 格式 → 字体」抽查有无混入 Calibri、等线等默认字体。
- 导出 PDF 时勾选「符合 ISO 19005-1 (PDF/A)」可强制嵌入字体，再用 `pdffonts` 复核。
- 打开 PDF 逐页目检：分页、孤行、图与图题是否分离、表格是否跨页错位。

## 三、Markdown / 其他

按用户指定格式输出；若要 PDF，用 pandoc + XeLaTeX 或对应模板，仍按上面的查错与目检流程。

## 四、常见错误对照表

| 现象 | 原因 | 处理 |
|---|---|---|
| 引用显示 `??` | 只跑了一遍 / 标签拼错 | 再跑一遍；检查 `\label` `\ref` |
| 中文变方框 | 字体未设置或未嵌入 | 确认 ctex + XeLaTeX；检查 `pdffonts` |
| 表格超出页宽 | 列太多 / 未用 `tabularx` | 缩小字号、用 `tabularx` 或横排 |
| 图片找不到 | 路径含空格或中文 | 用相对路径；文件名避免空格 |
| `ctex` 与 `fontspec` 冲突 | 重复设置字体 | 只保留 ctex 的字体设置 |
| 参考文献不显示 | 没跑 bibtex/biber | 按上面顺序补跑 |
| PDF 参考文献出版社被截断 | publisher 含 `and` 未加双大括号 | 改为 `{{...}}`，重跑 biber |
| 最后一页只剩一条参考文献 | 分页位置不巧 | `\printbibliography` 前加 `\clearpage` |
| 目录页码错 | 少跑一遍 | 再跑一遍 XeLaTeX |
| 公式编号重复 | 手写编号 | 全部交给 `equation`/`align` 环境 |

## 五、编译通过不等于排版正确

XML/日志合法只说明语法没问题。必须看渲染后的页面：分页、孤行、图表位置、公式对齐，都要肉眼确认。
