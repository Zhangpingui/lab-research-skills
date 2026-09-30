# 课题组科研助手 · v0.5

面向雷达、相控阵天线、SAR 图像与小目标检测的科研 skill。支持论文多 Agent 精读与创新点设计、多源文献检索、学术论文主线设计与模拟审稿，也支持证据驱动的科研材料写作和 Word 交付。

本版采用“AI 辅助、研究者人工修改定稿”的工作方式。v0.2 的两阶段多 Agent 论文精读、v0.3 的材料生产链和 v0.4 的论文写作/模拟审稿链继续保留。v0.5 将正式论文解读固定为同源双交付：先生成包含核心图表的 `paper-notes.md`，再由它生成带图的 `paper-notes.docx`；局部公式、段落和单图问答仍可直接在对话中完成。

- [调研与二次开发方案](docs/调研与二次开发方案.md)：候选仓库、许可证、取舍、开发范围与验收标准。
- [Skill 入口](skills/lab-research/SKILL.md)：完整使用流程。
- [开源来源与许可](skills/lab-research/THIRD_PARTY_NOTICES.md)：改编来源、固定版本和 MIT 声明。

## 立即使用

仓库中保存可审查、可版本管理的开发版；安装后也可以直接用 `$lab-research` 调用。未安装时，可让支持读取本地文件的 AI 助手执行：

```text
请读取 skills/lab-research/SKILL.md 并按它工作。
解读这篇 SAR 小目标检测论文：先解释核心意思，再核查实验依据，
最后提出适合我们课题组验证的改进思路。正式交付 paper-notes.md、
带核心图表的 paper-notes.docx 和图表资源。论文路径：<你的 PDF 路径>。
```

```text
请读取 skills/lab-research/SKILL.md 并按它工作。
基于我的研究设想、已有结果和参考文献，辅助起草国自然立项依据。
先检索并核验关键文献，区分已知事实、拟研究内容和待补材料，
最后交付可编辑 Word 和引用证据表。
```

```text
请读取 skills/lab-research/SKILL.md 并按它工作。
基于现有 paper-notes.md、claims.json、实验结果和参考文献，先建立论文主线卡，
再给出章节—主张—证据提纲和实验图表计划。不要把未完成实验写成结果。
```

```text
请读取 skills/lab-research/SKILL.md 并按它工作。
对这篇完整稿件进行投稿前模拟审稿：分别检查结构、证据和雷达/SAR领域边界，
最后按影响合并为“位置—证据—影响—修改动作”的问题单。
```

安装时把整个 `skills/lab-research` 文件夹复制到所用客户端支持的技能目录；技能被发现后可用 `$lab-research` 调用。文件夹内的说明与脚本自包含，不要求安装上游整个技能库。

## PDF 读取脚本

建议 Python 3.11+。仅脚本需要 `pdfplumber`，可使用宿主已有环境，或在自己的虚拟环境中安装：

```bash
python -m pip install -r skills/lab-research/scripts/requirements.txt
python skills/lab-research/scripts/read_pdf.py paper.pdf --pages 1-5
python skills/lab-research/scripts/read_pdf.py paper.pdf --pages 2,4-6 --tables
```

输出 JSON 到标准输出，包含文件指纹、物理页码、文本和提取质量提示。`--tables` 返回候选表格单元格，仍需对照原图；脚本不执行 OCR，不理解图像，不验证论文结论，也不联网。

全文 PDF 只提取文字并不等于读懂全文。图表和公式需用宿主 PDF 查看能力核对；扫描件需另行 OCR 或提供可读版本。

查看完整页面并确定归一化裁剪框后，可复现地保留核心科学图表：

```bash
python skills/lab-research/scripts/extract_pdf_region.py paper.pdf \
  --page 4 --box 0.08,0.28,0.92,0.62 \
  --output outputs/lab-research/task/paper-notes-assets/fig-4-page-4.png
```

正式笔记完成后，从同一份 Markdown 生成带图 Word：

```bash
python skills/lab-research/scripts/build_paper_notes_docx.py \
  outputs/lab-research/task/paper-notes.md \
  outputs/lab-research/task/paper-notes.docx \
  --report outputs/lab-research/task/paper-notes.qa.json
```

转换器支持标题、正文、列表、表格、代码块和本地相对图片；缺失图片会直接报错，不会生成一个悄悄丢图的 Word。DOCX 仍需逐页渲染并检查图表、图注和分页。

## 论文写作与模拟审稿

论文写作不会从空白页自由扩写。流程先从 `paper-notes.md`、`claims.json`、`idea-cards.md`、真实实验结果和文献账本建立 `paper-story.md`，再生成章节—段落—主张—证据提纲。实验和图表分别维护验证对象、公平基线、竞争解释、失败条件与一句话消息。

完整稿件可以由结构、证据和领域三个独立角色审查。角色只提交问题单，主 Agent 统一回查和修改，避免多 Agent 分别起草后直接拼接。角色 JSON 可用下列脚本校验：

```bash
python skills/lab-research/scripts/validate_manuscript_review_packet.py \
  --claims claims.json review-packets/*.json
```

## 文献检索与 Word 输出

文献检索按任务建立查询矩阵，优先 Crossref、arXiv、出版方和作者官方页面，再用聚合或手工数据库补漏。输出保留查询式、检索日期、去重规则和实际读取等级；只拿到元数据或摘要时不会写成全文证据。

没有指定 Word 模板时，可从示例包生成 DOCX：

```bash
python skills/lab-research/scripts/build_research_docx.py \
  skills/lab-research/assets/material-package.example.json \
  material-example.docx --report material-example.qa.json
```

生成成功只代表结构和文件有效。正式交付前还要通过宿主文档工具渲染为逐页 PNG，并检查全部页面；用户提供模板时优先编辑模板副本。论文笔记构建器能够嵌入核心科学图表，但不等同于期刊投稿排版；通用材料构建器仍不处理论文公式、作者单位和期刊模板。

## 验证

```bash
python -m pip install reportlab
python -m unittest discover -s tests -v
```

人工验收案例见方案文档。v0.2 已使用一篇 DenoDet SAR 目标检测论文与一份识别/跟踪概要设计完成首轮端到端试运行；该次验证检查工作流是否产生互补证据与可执行实验，不代表论文结论已复现。
