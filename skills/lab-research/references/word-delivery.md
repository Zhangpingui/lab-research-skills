# 科研材料 Word 交付

用户要求 Word 时，优先在用户模板副本上写作；没有模板时使用简洁、可编辑的 DOCX，不臆造申报单位格式。正式产物与渲染中间件分开保存。

## 论文解读双交付

正式论文解读默认同时交付 `paper-notes.md` 和 `paper-notes.docx`。先完成 Markdown 主笔记和 `paper-notes-assets/` 中的核心图表，再运行：

```bash
python scripts/build_paper_notes_docx.py paper-notes.md paper-notes.docx \
  --report paper-notes.qa.json
```

Word 必须从 Markdown 派生，不另写一份相似但不一致的正文。转换器会嵌入 Markdown 引用的本地图片，并在图片缺失、使用远程 URL 或路径逃出任务目录时失败。每次修改 Markdown 或图表后重新构建并重新渲染 Word。

## 生成路径

1. 将通过证据审查的正文整理为 `lab-research-document-v1` JSON；示例见 `assets/material-package.example.json`。
2. 运行：

```bash
python scripts/build_research_docx.py material.json output.docx --report output.qa.json
```

3. 若内容仍有 `[[待补]]` 一类占位符，仅在用户明确需要工作稿时使用 `--allow-placeholders`，并在文件名标记 `draft`。正式版不允许占位符。
4. 若用户提供 DOCX 模板，使用宿主文档编辑能力把内容写入模板副本；不要假设通用构建器能保留复杂样式、域、页眉页脚和内容控件。

构建器把正文中的 `[@R01]` 转成按参考文献列表排序的 `[1]`，并拒绝不存在的引用 ID。它只负责结构化排版，不验证文献是否真实、是否支持对应句，也不更新 Word 域。

## 视觉验收

每次实质性修改后把最终 DOCX 渲染为逐页 PNG，并检查每一页：

- 标题、正文、表格和参考文献没有截断、重叠或异常换行；
- 中文与公式字体可读，没有缺字或错误替换；
- 页边距、分页、标题层级和编号稳定；
- 表格没有超出页面，图题/表题与对象相邻；
- 论文解读中的核心图表已出现、没有拉伸或裁切，图注和来源紧邻图片；
- 正文没有内部主张 ID、工具标记、未解析引用或意外占位符。

优先使用宿主提供的文档渲染工具。宿主没有渲染能力时，可以交付 DOCX，但必须标明“结构检查完成，视觉渲染未验证”，不能宣称版式通过。

## 文件与版本

推荐输出：

- `paper-notes.md` 与 `paper-notes.docx`：正式论文解读的同源双交付；
- `paper-notes.qa.json`：Markdown 指纹、图表数量和 DOCX 指纹；
- `<任务名>-draft-v01.docx`：允许显式待补项的工作稿；
- `<任务名>-review-v01.docx`：供作者审阅的完整版本；
- `<任务名>-final-v01.docx`：无占位符且已完成视觉验收；
- `<任务名>-final-v01.qa.json`：构建指纹、章节数、参考文献数和占位符状态。

除非用户明确要求覆盖，始终另存新版本。不要把未公开材料、解析缓存、页面 PNG 或 QA 临时目录提交到技能仓库。
