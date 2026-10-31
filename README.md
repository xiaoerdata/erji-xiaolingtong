# 二级小灵通

给 Agent 的二级市场分析技能。用小二 MCP 或自己的 CSV/JSON，把基金比较、行情复盘、股票量价、融资与披露持仓、期货及跨资产问题做成有数据日期和来源的分析。

**标准版以小二 Core 可用读取能力为上限。** 不包含 VIP 专属调用、公司账户数据、内部模型、真实用户资料或凭据。MCP 的权限、产品范围、字段脱敏和额度仍由服务端执行；安装技能不会增加权限。私募参考净值与原始净值分开，脱敏名称不还原。

## 下载 v1.0.0

- [二级小灵通.skill](https://github.com/xiaoerdata/erji-xiaolingtong/releases/download/v1.0.0/erji-xiaolingtong.skill)：标准技能包，ZIP 内容，适用于支持该格式的宿主。
- [标准 ZIP](https://github.com/xiaoerdata/erji-xiaolingtong/releases/download/v1.0.0/erji-xiaolingtong.zip)：解压后按客户端方式安装文件夹。
- [WorkBuddy ZIP](https://github.com/xiaoerdata/erji-xiaolingtong/releases/download/v1.0.0/erji-xiaolingtong-workbuddy.zip)：同一套内容，补充 WorkBuddy 官方格式要求的双语展示、版本和作者字段。
- [SHA256SUMS](https://github.com/xiaoerdata/erji-xiaolingtong/releases/download/v1.0.0/SHA256SUMS)：校验下载文件。
- [平台 MCP 接入指引](https://www.xiaoerdata.site/#/mcp/overview)：另有技能包下载入口。

## 安装和使用

### 支持文件夹技能的 Agent

解压标准 ZIP，保留整个 `erji-xiaolingtong/` 文件夹及子目录，放进客户端文档要求的技能目录，再重新加载。需要终端/Python 才能运行附带的计算脚本；纯对话客户端仍可阅读场景和方法，不能因此声称已经执行计算。

发给 Agent：

> 用二级小灵通，比较我关注的几只基金最近半年的收益和回撤。先核对我的小二 MCP 权限、实际数据日期及复权口径；没有权限的数据不要尝试绕过。

或者直接给自己的文件：

> 用二级小灵通分析这个 CSV，先检查缺失、日期和单位，再按共同区间比较。它是我的数据，不代表平台提供这些字段。

### WorkBuddy

官方[技能说明](https://open.workbuddy.cn/docs/skill)定义了 `SKILL.md`、资源目录和 ZIP 提交格式；本仓库额外提供含其必填展示字段的 WorkBuddy ZIP。安装入口和是否允许本地 ZIP 以实际客户端版本为准；使用其支持的导入/本地技能方式。若版本只允许从市场安装，可用官方“添加技能 → 创建技能”流程，向 Agent 提供本仓库文件作为材料，或等待市场上架。

**GitHub 发布不等于 WorkBuddy 市场上架。** 本项目没有宣称完成市场审核、真实客户端导入或用户 OAuth 验收；不编造导入菜单或承诺所有客户端都能直接导入 `.skill`。

### 连接小二 MCP

MCP 服务：`https://www.xiaoerdata.site/mcp`（Streamable HTTP）。按[平台指引](https://www.xiaoerdata.site/#/mcp/overview)完成本人 OAuth 网页授权。密码只输入平台授权网页，不能发给 Skill。没有 MCP 也能使用自有数据模式。

## 内容

- `SKILL.md`：范围、路由、数据与交付约束。
- `references/`：接入、私募、公募/ETF、市场案例、数据口径与可复制提示词。
- `scripts/compare_nav.py`：纯本地共同日期净值比较，仅 Python 标准库，无网络。
- `assets/example-nav.csv`：合成示例，不是实际业绩。

脚本给出区间收益、至少一年区间的年化收益、共同观测点上的采样回撤。它不提供未经频率核对的夏普；Core 参考数据标为近似，缺失值不会补零。

## 开发与复核

```sh
python3 -m unittest discover -s tests
python3 tools/package_skill.py
```

产物在 `dist/`。标准 ZIP 与 `.skill` 字节一致；WorkBuddy ZIP 只改变入口元信息，不增加数据权限。案例工具候选经 Core 角色静态契约检查；这不替代各账号实际产品权限、当前部署状态及客户端实测。Skill 提供通用研究方法，不含收益承诺。

许可：MIT。软件和文档许可不授予任何数据源的数据再分发权。
