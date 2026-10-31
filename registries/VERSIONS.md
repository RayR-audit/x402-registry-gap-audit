# x402 Registry / 口径版本记录（v0.1 · 2026-09-27）

> 红队必修项：护城河=口径版本，不是时间。任何数据产出口径变更必须 bump 版本+记录差异。

## v0.1（2026-09-27）

- **注册表**：base_facilitators.csv = 105 条地址→facilitator 名映射。来源：Tektonic 派生注册表（frozen 2026-09-13 批次）。
- **收录标准**：Tektonic 上游归档（Base 表）中出现过的 facilitator 合约地址；未做主动补录。
- **标签 gate**：无（v0.1 不含行为标签，只有地址→名单映射）。
- **已知边界**：上游 Tektonic 停更于 2026-04-14（131 天窗口 as-of）；2026-04-14 之后新出现的 facilitator 不在表内——这是本表最重要的口径限制，所有引用必须带这句。
- **缺口表（registry_gap/）判定口径**：
  - Type A = 402 challenge 结算层地址 ∉ 注册表（待主动探测数据）
  - Type B = 自报 x402 但公开文档零链上地址
  - 判定只针对结算路径归属，不作服务质量/诚信判断
- **备选数据源（未接入）**：Dune curated `payments.agentic_payments`（x402+MPP，Base/Polygon/Solana，带 facilitator_name）——接入前不得用于口径变更。
- **变更纪律**：任何字段增删/收录标准变化 → bump 版本 + 差异说明 + 影响的下游产物清单。

## 待办

- [ ] Dune 备选源自跑通一次（接入前验证）
- [ ] Type A 探测脚本（402 challenge 提取 facilitator 地址，限速）
