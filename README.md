# 课题组科研助手 · v0.3

面向雷达、相控阵天线、SAR 图像与小目标检测的科研 skill。支持论文多 Agent 精读与创新点设计，也支持多源文献检索、证据驱动的科研材料写作和 Word 交付。

本版采用“AI 辅助、研究者人工修改定稿”的工作方式。v0.2 的两阶段多 Agent 论文精读继续保留；v0.3 新增“查询矩阵—文献去重—主张证据账本—论证骨架—章节写作—DOCX 构建与渲染验收”链路。申请书年度、项目类型和学校模板由具体任务提供；横向、其他纵向项目提供通用入口。

- [调研与二次开发方案](docs/调研与二次开发方案.md)：候选仓库、许可证、取舍、开发范围与验收标准。
- [Skill 入口](skills/lab-research/SKILL.md)：完整使用流程。
- [开源来源与许可](skills/lab-research/THIRD_PARTY_NOTICES.md)：改编来源、固定版本和 MIT 声明。

## 立即使用

当前是仓库开发版，未安装到全局技能目录。可直接让支持读取本地文件的 AI 助手执行：

```text
请读取 skills/lab-research/SKILL.md 并按它工作。
解读这篇 SAR 小目标检测论文：先解释核心意思，再核查实验依据，
最后提出适合我们课题组验证的改进思路。论文路径：<你的 PDF 路径>。
```

```text
请读取 skills/lab-research/SKILL.md 并按它工作。
基于我的研究设想、已有结果和参考文献，辅助起草国自然立项依据。
先检索并核验关键文献，区分已知事实、拟研究内容和待补材料，
最后交付可编辑 Word 和引用证据表。
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

## 文献检索与 Word 输出

文献检索按任务建立查询矩阵，优先 Crossref、arXiv、出版方和作者官方页面，再用聚合或手工数据库补漏。输出保留查询式、检索日期、去重规则和实际读取等级；只拿到元数据或摘要时不会写成全文证据。

没有指定 Word 模板时，可从示例包生成 DOCX：

```bash
python skills/lab-research/scripts/build_research_docx.py \
  skills/lab-research/assets/material-package.example.json \
  material-example.docx --report material-example.qa.json
```

生成成功只代表结构和文件有效。正式交付前还要通过宿主文档工具渲染为逐页 PNG，并检查全部页面；用户提供模板时优先编辑模板副本。

## 验证

```bash
python -m pip install reportlab
python -m unittest discover -s tests -v
```

人工验收案例见方案文档。v0.2 已使用一篇 DenoDet SAR 目标检测论文与一份识别/跟踪概要设计完成首轮端到端试运行；该次验证检查工作流是否产生互补证据与可执行实验，不代表论文结论已复现。
