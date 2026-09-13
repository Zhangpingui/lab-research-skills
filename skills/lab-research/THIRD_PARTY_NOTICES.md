# 开源来源与许可

本技能 v0.1.0 对下列 MIT 许可项目的科研工作流进行了选取、中文改编和重组。不是原作者发布的版本，也不代表原作者认可本项目。检索与取样日期：2026-09-13。

## 改编来源

| 来源与固定版本 | 取样文件 | 本项目改动 |
|---|---|---|
| [ChineseResearchLaTeX](https://github.com/huangwb8/ChineseResearchLaTeX/tree/117b95fc0a19d797f22a2f7d0b4e882f04979108) | `skills/research-literature-interpretation/SKILL.md`；`skills/nsfc-justification-writer/SKILL.md`；`skills/nsfc-research-content-writer/SKILL.md`；`skills/nsfc-ref-alignment/SKILL.md` | 将问题、方法、证据、边界与申请书论证检查改编为本组参考文件；取消固定 LaTeX 路径、固定三年计划和专用运行框架依赖 |
| [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/c1ed16d97dd61ff50a3bd46dd353e4a55fd77f34) | `skills/research-grants/SKILL.md`；`skills/scientific-critical-thinking/SKILL.md`；`skills/hypothesis-generation/SKILL.md` | 保留研究目标、方法、验证和可行性的一致性思路；重写为本组申请场景，区分假设、竞争解释和证据；未引入其 PDF/DOCX 等特殊许可目录 |
| [BESSER-PEARL research-agent-skills](https://github.com/BESSER-PEARL/research-agent-skills/tree/03d3c49ac1698c9d29cc4c0f5e8eeca17210bd51) | `research-paper-review/SKILL.md` | 改编按论文类型调整评价标准、核对数值与提出可执行反馈的流程；增加雷达/SAR 口径，取消固定十条建议与接收/拒稿结论 |

`scripts/read_pdf.py` 和测试是本项目新写的实现，未复制上述项目代码。其运行依赖 pdfplumber 单独按自身许可分发；本技能包不捆绑该库。

research-hound、Docling、MATLAB toolkit 等出现在调研文档中；v0.1 未复制其文件，也未将其设为运行依赖。

## 上游版权声明

以下三个声明分别来自上游许可文件，保留于此：

- ChineseResearchLaTeX：Copyright © 2024 Weibin Huang。原文见 [license.txt](https://github.com/huangwb8/ChineseResearchLaTeX/blob/117b95fc0a19d797f22a2f7d0b4e882f04979108/license.txt)。
- K-Dense：Copyright (c) 2025 K-Dense Inc.。原文见 [LICENSE.md](https://github.com/K-Dense-AI/scientific-agent-skills/blob/c1ed16d97dd61ff50a3bd46dd353e4a55fd77f34/LICENSE.md)。
- BESSER-PEARL：Copyright (c) 2026 BESSER-PEARL。原文见 [LICENSE](https://github.com/BESSER-PEARL/research-agent-skills/blob/03d3c49ac1698c9d29cc4c0f5e8eeca17210bd51/LICENSE)。

上述改编部分均适用以下 MIT 许可正文。再分发本技能时保留本文件及许可。

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
