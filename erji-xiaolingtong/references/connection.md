# 小二 MCP 接入与数据调用

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
3. 读取搜索结果的完整 schema、权限、限制和 `execution`。组合参数在 `oneOf/anyOf` 分支内；先选择 `mode`，按该分支和 `examples` 填参，不把不同模式的字段合成同时必填。不用空参数试探或连续猜值。聚合读取按返回的 `execution.read` 执行，参数形如：
   ```json
   {"tool":"<搜索返回的能力名>","arguments":{"<真实参数名>":"<实际值>"}}
   ```
   这是结构示意，尖括号不能原样执行。按当前契约逐层解包 `result`，不是固定假定只有一层。
4. 检查 JSON-RPC error、`isError` 和内部业务状态；HTTP 200 本身不能证明业务成功。

旧目录未返回 `execution` 时，仅调用当前会话实际列出的工具；不把搜索结果逐项注册为客户端工具。缺工具时刷新目录/重新连接，不能用旧名试探未授权入口。

## 按研究任务选择数据

以下能力名用于帮助搜索和定位数据，不替代当前工具目录。调用前核对实时 schema、可用模式、输入字段、日期范围和返回披露说明。

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

当前目录找不到相应能力时，注明本次缺失的数据。需要用户补充文件时，说明对象、日期、字段和单位；不要猜测接口名或参数。

## 私募数据的理解方式

- 名称可能脱敏；目录中返回的 `productId`/`managerId` 用于后续查询，不从展示名拼接完整名称，也不跨账号复用标识。
- 净值可能为近似、归一化参考序列；快照中的绝对净值、规模等字段可能为空。报告使用服务端实际披露口径，不要求原值或选择所谓“全量”参数。
- 需要精确到细小收益差、绝对估值或规模金额的任务，参考序列不足以支持时，明确说明；可由用户补充原始数据并注明来源。
- 分页/历史上限按实际返回处理；只在获准的区间内继续。不要通过分账户、多窗口或更换频率拼接来重建受限数据。

## 常见只读调用示例

下列是能力内的 `arguments`，通过当前返回的 `execution.read` 传入；日期和标的按任务调整，实时契约优先。

| 能力 | 参数示例 |
| --- | --- |
| `super66.market.margin.read` | `{"mode":"market","period":"1m"}` |
| `super66.market.indices.read` | `{"mode":"latest","indexNames":["沪深300","黄金"]}` |
| `super66.market.futures_daily.read` | 股指：`{"mode":"instrument","contractType":"IF","deliveryBucket":"当季","startDate":"2026-01-01"}`；商品连续：`{"mode":"continuous","symbols":["A0"],"limit":5000}` |

期货有股指分合约与商品连续两种来源，不能把商品连续代码传给 `contractType`。返回的覆盖区间和换月口径决定可用于何种分析，不代表全部期货品种都有数据。

## 可用性与恢复

- 技能包不授予权限；服务中心、实时目录与调用的当前校验共同决定可用能力。仅凭某个旧工具的名称前缀，不判断其平台归属；兼容名称按实时 `execution` 调用。
- 自选股只读本人已确认归属的记录；`PERSONAL_STOCK_OWNERSHIP_REVIEW_REQUIRED` 表示历史归属待平台核对，不是空列表。投资经理订阅与材料等业务能力还须具备对应准入和部署条件；普通数据权限不等于业务写权限。
- 参数错误先看 `issues` 中的分支、候选值与静态示例；仍不清楚时重新发现一次。权限拒绝、配额异常或结构未就绪交由平台处理，不换凭证绕过，不循环重试。报障保留工具名、脱敏参数、错误码、requestId 与北京时间，不附凭据。
