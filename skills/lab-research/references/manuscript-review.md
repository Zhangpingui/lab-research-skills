# 学术论文模拟审稿与重构

本模式用于整篇论文、投稿前稿件或大修稿的证据和结构审查。局部语言润色不需要多 Agent；全文审查可在主 Agent 准备共享材料后，由结构、证据和领域三个角色独立检查。

## 审查输入

先确认稿件版本、目标期刊/会议或读者、用户希望审查的范围、关联的图表/补充材料、已核验文献和真实实验记录。若只有 PDF，记录实际读取页和视觉核对页；若有源稿，以源稿为正文基准，PDF 用于版式与图表核对。

审查不自动授权修改原稿。用户只要求审查时交付报告；用户要求修改时另存版本。

## 九个审查维度

| 维度 | 核心问题 |
|---|---|
| 相关性 | 是否符合目标范围和读者关心的问题？ |
| 新颖性 | 新问题、新方法、新认识或新边界是什么？是否有最近邻对照？ |
| 贡献 | 贡献是否重要，还是常规应用、简单组合或工作量陈述？ |
| 正确性 | 推导、实现、统计、符号和结论是否一致？ |
| 证据 | 实验是否充分、公平、可复现，并真正支持主张？ |
| 边界 | 是否说明局限、代价、失败条件和不能外推的场景？ |
| 文献 | 关键、经典和最新工作是否覆盖，引用是否支持对应句？ |
| 表达 | 标题、摘要、结构、段落、语言、图表和符号是否清楚一致？ |
| 影响 | 结果带来的知识、方法或工程增量是否被准确说明？ |

优先报告会改变接收判断、核心结论或复现性的少量问题；不要为了数量罗列同义问题。

## 三个独立审查角色

全文复杂且宿主支持子 Agent 时，可以并行执行：

1. `structure-reviewer`：只检查中心命题、标题/摘要/引言的一致性、章节职责、段落逻辑、重复和缺失；
2. `evidence-reviewer`：核对贡献声明、数字、表格、图、引用、统计口径、竞争解释和结论强度；
3. `domain-reviewer`：按 [领域要点](domain-radar.md) 检查雷达/SAR 模型、数据、指标、基线、复现和外推边界。

角色彼此不先看结论，只提交问题单，不重写全文。主 Agent 回查冲突，合并重复问题，并决定是否修改；不按多数投票。

每个角色返回 UTF-8 JSON：

```json
{
  "schema_version": "manuscript-review-packet-v1",
  "role": "evidence-reviewer",
  "manuscript_id": "文件哈希或稳定版本标识",
  "read_scope": ["Abstract", "Fig. 3", "Table 2", "Section IV"],
  "issues": [
    {
      "issue_id": "E01",
      "priority": "major",
      "category": "evidence_gap",
      "location": "Section IV-B, Fig. 3",
      "problem": "一句话说明问题",
      "evidence": "稿件中的定位、数字或冲突",
      "impact": "为何影响结论或读者判断",
      "action": "最小可执行修改",
      "claim_ids": ["C03"]
    }
  ],
  "open_questions": []
}
```

`priority` 使用 `critical / major / minor`；`category` 使用 `factual_error / evidence_gap / novelty_risk / logic / reproducibility / domain_boundary / citation / presentation / ethics`。没有证据的问题不要伪装成确定错误，可写为待核对风险。

可运行结构校验：

```bash
python scripts/validate_manuscript_review_packet.py \
  --claims claims.json \
  review-packets/structure.json \
  review-packets/evidence.json \
  review-packets/domain.json
```

校验通过只表示角色、字段和 `Cxx` 依赖满足协议，不表示审稿意见正确。

## 主 Agent 的合并与重构

合并报告时：

- 同一根因导致的多处症状合并为一项，列出代表位置；
- 区分事实错误、证据缺口、结构问题和表达建议；
- 对图表、公式和参考文献争议回查原始材料；
- 先修中心命题和证据，再修章节顺序和段落，最后修语言；
- 修改不得把 `hypothesis`、`planned_work` 或 `unknown` 升级为已证实结果。

推荐报告格式：

`位置 → 问题 → 证据 → 对结论的影响 → 修改动作 → 优先级`

如果用户要求重构，先交付修改后的 `paper-story.md` 和 `manuscript-outline.md`，确认主线稳定后再改连续正文。

## 学术规范检查

- 复述他人观点时既保留原意又重新组织表达，并给出正确引用；
- 不把只改少量词语、句型或段落顺序视为合格改写；
- 不伪造、篡改或选择性隐瞒会改变结论的数据；
- 不一稿多投；会议扩展期刊稿的新增内容和披露按当前期刊政策核验；
- 作者贡献、数据/代码可用性、伦理审批和利益冲突按目标期刊与机构要求处理；
- 不把语言模型生成的引用、结果或实验描述当成已核验事实。

## 输出与停止条件

- `manuscript-review.md`：合并后的主要问题、次要问题和优先修改顺序；
- `review-packets/`：仅在实际使用独立角色时保留各角色 JSON；
- `revision-map.md`：用户要求修改时，记录问题与改动位置；
- 更新后的 `manuscript-draft-vNN.md` 或模板副本。

关键图表、公式或引用无法取得时可以完成结构审查，但证据审查保留 `unresolved`。只有当缺失材料不会改变判断时才继续到细节润色；否则停止并列出需要补充的最小材料。
