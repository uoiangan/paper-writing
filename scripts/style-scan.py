#!/usr/bin/env python3
"""统计中文稿件的行文指标，供人工复核。

用法：python style-scan.py <file.tex|.md|.txt>
输出人读的指标表；阈值仅作线索，需结合通读判断。
"""

from pathlib import Path
import re
import statistics
import sys

HANZI = re.compile(r"[\u4e00-\u9fff]")

CONNECTORS = [
    "首先", "其次", "最后", "此外", "然而", "因此", "综上所述", "总而言之",
    "值得注意的是", "与此同时", "不仅如此", "另一方面", "进一步", "从而",
    "由此可见", "换言之", "毋庸置疑", "在此基础上", "需要指出的是", "不难发现",
]
ABSTRACT_WORDS = [
    "重要性", "有效性", "鲁棒性", "优越性", "可靠性", "必要性", "合理性",
    "显著性", "普适性", "先进性",
]
HOLLOW_ADJ = [
    "完整的", "详细的", "全面的", "系统的", "深入的", "精确的", "有效的",
    "显著的", "重要的", "关键的", "核心的", "主要的", "基本的", "必要的",
    "充分的", "丰富的", "有力的", "有益的", "有意义的", "有价值的",
    "有创新性的", "有突破性的",
]
PLACEHOLDERS = [
    "具有重要意义", "提供新思路", "奠定理论基础", "填补了空白", "填补空白",
    "某企业", "某系统", "相关研究表明", "众所周知", "不言而喻",
]
EMPTY_PHRASES = [
    "显著提升", "显著提高", "极大提高", "有效解决", "充分证明", "全面优化",
    "有效提升", "大幅提升",
]
UNCERTAINTY = [
    "可能", "也许", "大概", "大致", "基本上", "在一定程度上", "似乎", "倾向于", "有待",
]
PERSONAL = [
    "我们倾向于", "我们认为", "在我们看来", "我们建议", "我们选择", "笔者",
    "本文认为", "本文倾向于",
]
SUMMARY_START = re.compile(r"^\s*(?:因此|总之|综上所述|可见|由此可见|综上)[，,：:]")
MIN_DENSITY_SAMPLE = 100

TEMPLATE_VERB = re.compile(r"进行[\u4e00-\u9fff]{2}")
HIGH_PRECISION = re.compile(r"\d+\.\d{3,}")


def strip_latex(text):
    text = "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())
    document = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", text, flags=re.S)
    if document:
        text = document[1]
    for env in (
        "equation", "equation*", "align", "align*", "tabular", "table", "table*",
        "figure", "figure*", "thebibliography", "verbatim", "lstlisting",
    ):
        text = re.sub(
            r"\\begin\{" + re.escape(env) + r"\}.*?\\end\{" + re.escape(env) + r"\}",
            " ", text, flags=re.S,
        )
    text = re.sub(r"\\par(?![A-Za-z])", "\n\n", text)
    text = re.sub(r"\\(?:section|subsection|subsubsection|chapter|paragraph)\*?\{[^{}]*\}", " ", text)
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\(?:cite|ref|label|includegraphics|url|href)\*?(?:\[[^\]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", text)
    return text.replace("{", " ").replace("}", " ").replace("~", " ")


def paragraphs_of(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if len(HANZI.findall(p)) >= 5]


def sentences_of(paragraph):
    return [s for s in re.split(r"[。！？!?]+", paragraph) if len(HANZI.findall(s)) >= 2]


def count_occurrences(text, words):
    total = 0
    hits = {}
    for w in words:
        n = text.count(w)
        if n:
            hits[w] = n
            total += n
    return total, hits


def fmt(x):
    return f"{x:.1f}"


def per(text, n, unit, base):
    return (n / base * unit) if base else 0


def scan(path):
    source = Path(path)
    if source.suffix.lower() not in {".tex", ".md", ".txt"}:
        print("不适用：请提供 UTF-8 的 .tex、.md 或 .txt 正文。")
        return 2
    try:
        raw = source.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        print(f"无法读取输入：{error}", file=sys.stderr)
        return 2

    text = strip_latex(raw) if source.suffix.lower() == ".tex" else raw
    hanzi_total = len(HANZI.findall(text))
    if not hanzi_total:
        print("不适用：输入没有可统计的汉字，请人工复核对应语言。")
        return 2
    paragraphs = paragraphs_of(text)
    sentences_by_paragraph = [sentences_of(p) for p in paragraphs]
    sentences = [sentence for group in sentences_by_paragraph for sentence in group]

    para_lens = [len(HANZI.findall(p)) for p in paragraphs]
    sent_lens = [len(HANZI.findall(s)) for s in sentences]

    para_mean = statistics.fmean(para_lens) if para_lens else 0
    para_sd = statistics.pstdev(para_lens) if len(para_lens) >= 2 else 0
    para_cv = para_sd / para_mean if para_mean else 0
    para_min = min(para_lens) if para_lens else 0
    para_max = max(para_lens) if para_lens else 0

    sent_mean = statistics.fmean(sent_lens) if sent_lens else 0
    sent_sd = statistics.pstdev(sent_lens) if len(sent_lens) >= 2 else 0
    long_ratio = sum(1 for n in sent_lens if n > 50) / len(sent_lens) if sent_lens else 0

    connector_total, connector_hits = count_occurrences(text, CONNECTORS)
    abstract_total, abstract_hits = count_occurrences(text, ABSTRACT_WORDS)
    hollow_total, hollow_hits = count_occurrences(text, HOLLOW_ADJ)
    placeholder_total, placeholder_hits = count_occurrences(text, PLACEHOLDERS)
    empty_total, empty_hits = count_occurrences(text, EMPTY_PHRASES)
    uncertainty_total, uncertainty_hits = count_occurrences(text, UNCERTAINTY)
    personal_total, personal_hits = count_occurrences(text, PERSONAL)

    template_verb_hits = TEMPLATE_VERB.findall(text)
    precision_hits = HIGH_PRECISION.findall(text)
    question_count = text.count("？") + text.count("?")

    de_density = per(text, text.count("的"), 100, hanzi_total)
    sentences_per_connector = (len(sentences) / connector_total) if connector_total else float("inf")

    ending_summaries = sum(
        1 for group in sentences_by_paragraph if group and SUMMARY_START.match(group[-1])
    )
    ending_ratio = ending_summaries / len(paragraphs) if paragraphs else 0

    print(f"文件：{path}")
    print(f"汉字数：{hanzi_total}　段落：{len(paragraphs)}　句：{len(sentences)}　问句：{question_count}")
    print()

    print("【节奏】")
    print(f"  段落长度：均值 {fmt(para_mean)}，标准差 {fmt(para_sd)}，CV {para_cv:.2f}，"
          f"最短 {para_min}，最长 {para_max}")
    print(f"  句长：均值 {fmt(sent_mean)}，标准差 {fmt(sent_sd)}；长句（>50 字）占比 {long_ratio:.0%}")
    print()

    print("【词汇】")
    print(f"  连接词：{connector_total} 处（{per(text, connector_total, 100, hanzi_total):.1f}/100 字）  {connector_hits or ''}")
    print(f"  抽象评价词：{abstract_total} 处（{per(text, abstract_total, 100, hanzi_total):.1f}/100 字）  {abstract_hits or ''}")
    print(f"  空洞形容词：{hollow_total} 处（{per(text, hollow_total, 1000, hanzi_total):.1f}/千字）  {hollow_hits or ''}")
    print(f"  “的”字密度：{de_density:.1f}%")
    print(f"  进行+动词：{len(template_verb_hits)} 处  {template_verb_hits or ''}")
    print()

    print("【表达】")
    print(f"  段末总结句：{ending_summaries}/{len(paragraphs)}（{ending_ratio:.2f}）")
    print(f"  不确定性表达：{uncertainty_total} 处（{per(text, uncertainty_total, 1000, hanzi_total):.1f}/千字）  {uncertainty_hits or ''}")
    print(f"  个人判断：{personal_total} 处（{per(text, personal_total, 1000, hanzi_total):.1f}/千字）  {personal_hits or ''}")
    print(f"  占位空话：{placeholder_total} 处  {placeholder_hits or ''}")
    print(f"  空泛动词短语：{empty_total} 处  {empty_hits or ''}")
    print(f"  3 位以上小数：{len(precision_hits)} 处  {precision_hits[:8] or ''}")
    print()

    if hanzi_total < MIN_DENSITY_SAMPLE:
        print(f"样本较短（少于 {MIN_DENSITY_SAMPLE} 个汉字），仅提供统计。")
        return 0

    flags = []
    hints = []
    if len(sentences) >= 20 and sent_sd < 8:
        flags.append(f"句长标准差 {fmt(sent_sd)} < 8：可复核句式节奏")
    if long_ratio > 0.2 and len(sentences) >= 10:
        flags.append(f"长句占比 {long_ratio:.0%} > 20%：可复核长句是否影响理解")
    if len(paragraphs) >= 8 and para_cv < 0.25:
        flags.append(f"段落长度 CV {para_cv:.2f} < 0.25：可复核段落组织")
    if len(paragraphs) >= 8 and para_min > 50:
        flags.append(f"最短段落 {para_min} 字 > 50：可复核段落是否过长")
    if per(text, connector_total, 100, hanzi_total) > 2.0:
        flags.append(f"连接词密度 {per(text, connector_total, 100, hanzi_total):.1f}/100 字 > 2.0：可复核连接词是否重复")
    elif connector_total and sentences_per_connector < 5:
        flags.append(f"平均每 {sentences_per_connector:.1f} 句一个连接词：可复核过渡是否自然")
    if de_density > 6:
        flags.append(f"“的”字密度 {de_density:.1f}% > 6%：可复核定语是否难读")
    if len(template_verb_hits) >= 3:
        flags.append(f"“进行+动词” {len(template_verb_hits)} 处 ≥ 3：可复核动词是否冗余")
    if per(text, abstract_total, 100, hanzi_total) > 1.2:
        flags.append(f"抽象评价词密度 {per(text, abstract_total, 100, hanzi_total):.1f}/100 字 > 1.2：可复核评价是否有具体依据")
    if per(text, hollow_total, 1000, hanzi_total) > 3:
        flags.append(f"空洞形容词密度 {per(text, hollow_total, 1000, hanzi_total):.1f}/千字 > 3：可复核修饰语是否必要")
    if ending_ratio > 0.4:
        flags.append(f"段末总结句比例 {ending_ratio:.2f} > 0.40：可复核段末总结是否重复")
    if hanzi_total >= 1000 and per(text, uncertainty_total, 1000, hanzi_total) < 1:
        flags.append(f"不确定性表达密度 {per(text, uncertainty_total, 1000, hanzi_total):.1f}/千字 < 1：结合论断检查是否明确说明适用条件")
    if placeholder_total:
        hints.append(f"占位空话 {placeholder_total} 处：逐个改写或删除")
    if len(precision_hits) > 0:
        hints.append(f"存在 3 位以上小数 {len(precision_hits)} 处：核对精度是否合理，必要时补误差范围")

    if flags:
        print("警示：")
        for f in flags:
            print(f"  - {f}")
    else:
        print("警示：无（仅表示未触发阈值，仍需通读）")
    for h in hints:
        print(f"提示：{h}")

    return 0


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 2
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    return scan(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
