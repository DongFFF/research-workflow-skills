# 科研工作流 Skills

将论文写作和课题申报中反复使用的绘图、文献管理及图文设计方法整理成可安装的技能包。

[English](README.md)

## 包含内容

| 技能 | 适用任务 | 关键特点 |
| --- | --- | --- |
| `publication-chart-skill` | 研究框架图、机制图、技术路线、统计图与学术表格 | SVG 源文件、同类框等宽、框内居中、测量后适配文字、黑白打印检查 |
| `zotero-docx-reference-workflow` | 检索、核验、入库、引用插入、修订及文末列表维护 | Scholar 优先、DOI 二次核验、真实 Zotero 身份、Word 字段审计 |
| `grant-proposal-workflow` | 国社科、地方社科及校级课题等申报书的研究内容与配图 | 先读取当年模板，建立问题—任务—方法—数据—成果对应，再绘制总体图及子研究图 |

技能正文使用英文以便跨语言使用，示例请求和工作流说明提供中文。公开示例均为新编通用案例，未包含未发表论文、访谈材料、申报书正文或个人 Zotero 数据。

## 安装

下载或 clone 仓库后，在仓库目录运行：

```sh
python tools/install_skills.py --dry-run
python tools/install_skills.py
```

默认安装到 `$CODEX_HOME/skills`，未设置时为 `~/.codex/skills`。已存在的技能默认跳过；需要替换时加 `--replace`，旧目录会先移动到带时间戳的备份目录。可用 `--skill 技能名` 只安装一个技能；其他兼容 `SKILL.md` 的工具可用 `--dest` 指定安装位置。安装后重新加载技能列表。

```text
请使用 $publication-chart-skill，将这段研究内容绘制为黑白紧凑型 SVG，输出可编辑源图和预览图。
请使用 $zotero-docx-reference-workflow，检查正文引用字段、隐藏多文献引用和参考文献列表是否一致。
请使用 $grant-proposal-workflow，梳理各子研究的输入输出和方法数据对应关系，再设计配图。
```

## 本地工具

Python 3.10+。审计 DOCX、安装技能和访问本地 Zotero Connector 只依赖标准库。SVG 生成需要 Pillow，可选 PNG 渲染需要 CairoSVG 及本机 Cairo。

```sh
python -m pip install -r requirements-figures.txt
python skills/publication-chart-skill/scripts/make_framework.py skills/publication-chart-skill/examples/framework.json --out-dir build/framework
python skills/zotero-docx-reference-workflow/scripts/inspect_zotero_docx.py manuscript.docx --out-dir build/audit
python skills/zotero-docx-reference-workflow/scripts/zotero_connector.py ping
```

绘图可用 `--font` 指定字体文件，中文需使用支持中文的字体。加 `--png` 输出位图预览。生成后还需在实际插入宽度下检查文字、连接线及分页。

## Zotero 流程中的证据边界

- 检索页面可访问，不等于找到了目标论文；记录候选匹配及来源。
- DOI 跳转成功，不等于元数据完全对应；还需核对作者、题名、年份及卷期页码。
- Connector 返回成功，不等于已进入指定文献分类；需读回条目和分类确认。
- DOCX 中存在 `ZOTERO_ITEM`，不等于可以刷新；还需真实条目身份、文档偏好及 Word/Zotero 验证。
- 宏无报错返回，只能证明命令已调用；完成刷新及其结果另行核验。
- `[1]` 是引用格式中的编号，Zotero 内部数字 ID 或 URI 是条目身份，二者不能混用。

默认采用 Scholar 优先检索，目标期刊未指定时首次插入可采用 IEEE。代理、CSL 文件和库身份均从当前环境取得，不写死端口或账号。用户要求的 MCP 或特定路线不可用时，明确报告阻塞点，遵循用户对替代路线的授权。

## 测试与扩展

```sh
python tools/validate_repo.py
python -m unittest discover -s tests -v
```

参见 [跨项目工作流经验](docs/workflow-patterns.md) 和 [整理范围与来源说明](docs/scope-and-provenance.md)。Visio 原有技能暂作为本地可选工具，未复制其来源尚未核实的文件；本仓库不打包第三方运行时、商业模板或 CSL 样式文件。

本仓库原创内容采用 MIT 许可。Zotero、Word、pubfig、pubtab、浏览器和 MCP 服务需另行安装或配置。
