# 小二 MCP 接入与 Core 边界

## 连接

- 平台：https://www.xiaoerdata.site
- 平台 MCP 指引：https://www.xiaoerdata.site/#/mcp/overview
- Streamable HTTP 服务：https://www.xiaoerdata.site/mcp
- 使用客户端的远程 MCP 设置与本人网页 OAuth 授权；授权页选择“小二平台”。当前客户端不支持时，按平台最新指引处理，不发明替代地址。
- 密码只填受信任的授权网页，Token 由客户端认证层保管。Skill、提示词、配置样例和报告都不放密码、Webhook 签名密钥或 Bearer Token。
- 安装 Skill 与连接 MCP 是两件事。工具列表、真实只读调用、重新授权分别验证；保存配置不等于接通。

## 发现和读取

若当前目录提供聚合入口：

1. `super66.mcp.service_center` 查看当前身份与能力；按实时 schema 选择需要的 sections。
2. `super66.mcp.search_tools` 按“公募净值比较”“股票量价”“私募筛选”等具体任务搜索。搜索目录的分页不是业务数据分页。
3. 读取搜索结果的完整 schema、权限、限制和 `execution`。聚合读取按返回的 `execution.read` 执行，参数形如：
   ```json
   {"tool":"<搜索返回的能力名>","arguments":{"<真实参数名>":"<实际值>"}}
   ```
   这是结构示意，尖括号不能原样执行。按当前契约逐层解包 `result`，不是固定假定只有一层。
4. 检查 JSON-RPC error、`isError` 和内部业务状态；HTTP 200 本身不能证明业务成功。

旧目录未返回 `execution` 时，仅调用当前会话实际列出的工具；不把搜索结果逐项注册为客户端工具。缺工具时刷新目录/重新连接，不能用旧名试探未授权入口。

## 标准版能力选择

以下是编写案例时核对过的 **Core 角色读取候选**，不是账号的永久授权清单。运行时仍以当前身份、实时目录、模式权限、数据范围和返回披露说明为准。

| 任务 | 搜索关键词 | 目录中的候选能力 |
| --- | --- | --- |
| 指数区间与跨资产 | 指数、全球资产 | `super66.market.indices.read`、`super66.market.global_assets.read` |
| A 股与行业 | 股票、行业、历史行情 | `super66.market.stocks.read` |
| 融资变化 | 融资融券 | `super66.market.margin.read` |
| 期货日频 | 期货、连续合约 | `super66.market.futures_daily.read` |
| 宏观时序 | 宏观指标 | `super66.macro.read` |
| 公募和 ETF | 公募、ETF、净值 | `super66.products.public.read`、`super66.products.workspace.read` |
| 公募经理及披露重仓 | 基金经理、公募持仓 | `dc66_get_active_equity_fund_bundle`、`super66.funds.holdings.read` |
| 私募筛选与参考走势 | 私募指标、私募净值 | `super66.products.private_metrics.read`、`dc66_get_private_product_nav` |

没有这些能力或某个模式被过滤时，不用另一个账号或接口补取。标准版不提供 VIP 专属原值、扩展历史和专属业务的调用教程。

## Core 私募案例的具体边界

- 名称可能脱敏；目录中返回的 `productId`/`managerId` 用于后续查询，不从展示名拼接完整名称，也不跨账号复用标识。
- 净值可能为近似、归一化参考序列；快照中的绝对净值、规模等字段可能为空。报告使用服务端实际披露口径，不要求原值或选择所谓“全量”参数。
- 需要精确到细小收益差、绝对估值或规模金额的任务，标准参考序列不足以支持时，明确说明；可请用户提供有权使用的原始数据。
- 分页/历史上限按实际返回处理；只在获准的区间内继续。不要通过分账户、多窗口或更换频率拼接来重建受限数据。
