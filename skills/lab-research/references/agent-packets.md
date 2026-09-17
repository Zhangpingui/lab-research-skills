# Agent 交接数据协议

子 Agent 之间不依赖消息相邻顺序；每个角色输出一个 UTF-8 JSON 对象。

## 顶层字段

```json
{
  "schema_version": "lab-research-agent-packet-v1",
  "paper_sha256": "64位小写十六进制",
  "role": "mechanism",
  "read_scope": {
    "pdf_pages": [1, 2, 3],
    "visual_pages": [2]
  },
  "findings": [],
  "open_questions": []
}
```

`role` 允许：`mechanism`、`evidence`、`domain`、`idea`、`falsifier`、`feasibility`。finding ID 前缀固定为 `M`、`E`、`D`、`I`、`R`、`X`，避免跨包合并时冲突。`visual_pages` 必须是 `pdf_pages` 的子集，只记录实际看过页面图像的页码。

## Finding 字段

```json
{
  "finding_id": "E01",
  "kind": "author_claim",
  "statement": "作者在三个数据集的消融中报告动态分组优于各固定组设置。",
  "locators": [
    {"pdf_page": 11, "anchor": "Table VII"}
  ],
  "evidence_status": "supports",
  "confidence": "high",
  "depends_on": []
}
```

`kind` 允许：`source_fact`、`author_claim`、`interpretation`、`critique`、`hypothesis`、`idea`、`experiment`。前四类必须有 `locators`，且页码位于 `read_scope.pdf_pages`；涉及视觉内容但未查看页面时应使用 `unresolved`，不要把文本抽取当成视觉核对。

`evidence_status` 允许：`supports`、`partial`、`contradicts`、`unresolved`、`not_applicable`。`confidence` 允许：`low`、`medium`、`high`。

`hypothesis`、`idea` 和 `experiment` 必须用 `depends_on` 引用至少一个主 Agent 分配的 `Cxx` 主张，避免从无证据的自由联想直接生成实验。

## 验证

```bash
python scripts/validate_agent_packet.py mechanism.json evidence.json
python scripts/validate_agent_packet.py --claims claims.json idea.json falsifier.json feasibility.json
```

提供 `--claims` 时，校验器还会拒绝不存在的 `Cxx` 依赖。退出码 0 只表示结构和基本定位约束通过；它不验证页码上的原文是否真的支持 statement，也不判断科学新颖性。
