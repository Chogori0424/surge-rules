# surge-rules

Chogori 的 Surge 规则与模块，Mac / iOS 通过远程地址拉取。

## AI 分流规则

按服务拆分，数据来自 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)，GitHub Actions 每天北京时间 04:00 自动同步。

| 文件 | 内容 | v2fly 来源 |
| --- | --- | --- |
| `rules/OpenAI.list` | ChatGPT、Sora、OpenAI API | `openai` |
| `rules/Claude.list` | Claude、Anthropic | `anthropic` |
| `rules/Gemini.list` | Gemini、AI Studio、NotebookLM、Antigravity、Jules | `google-deepmind` |
| `rules/Grok.list` | Grok、xAI | `xai` |
| `rules/Perplexity.list` | Perplexity | `perplexity` |
| `rules/Copilot.list` | GitHub Copilot、Microsoft Copilot | `github-copilot` + `custom/Copilot.list` |
| `rules/AI-Other.list` | 长尾：Cursor、Mistral、OpenRouter、Hugging Face、Poe 等 | `category-ai-!cn` 去掉以上所有 |

```ini
RULE-SET,https://raw.githubusercontent.com/Chogori0424/surge-rules/main/rules/OpenAI.list,ChatGPT,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Chogori0424/surge-rules/main/rules/Claude.list,Claude,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Chogori0424/surge-rules/main/rules/Gemini.list,Gemini,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Chogori0424/surge-rules/main/rules/Grok.list,Grok,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Chogori0424/surge-rules/main/rules/Perplexity.list,Perplexity,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Chogori0424/surge-rules/main/rules/Copilot.list,Copilot,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/Chogori0424/surge-rules/main/rules/AI-Other.list,美国节点,update-interval=86400
```

维护：

- 上游没有的域名写到 `custom/<名称>.list`，推送后 Action 会重新生成。
- 新增一个服务拆分：在 `sources.json` 里加一项。
- 本地生成：`python3 scripts/build.py`

## 模块

| 模块 | 说明 | 订阅地址 |
| --- | --- | --- |
| 社区广告精简 | 按实际在用 App 筛选的广告规则，详见 [modules/startup-ads](modules/startup-ads/README.md) | `https://raw.githubusercontent.com/Chogori0424/surge-rules/main/modules/startup-ads/StartupAds-Lite.sgmodule` |

## 许可

`modules/startup-ads/` 派生自 fmz200/wool_scripts，按 GPL-3.0 分发，见该目录下的 `NOTICE.md` 与 `licenses/`。仓库其余内容（AI 规则生成脚本等）不受此影响。

## 安全

本仓库是公开的：不放节点、订阅链接、token 或任何凭据。
