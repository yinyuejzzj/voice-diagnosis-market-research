# AI 工业声纹诊断项目 · 可复用 Python 脚本

## 脚本分工

| 脚本 | 作用 |
|---|---|
| `config.py` | 配置中心：关键词、招标平台、行业映射、竞品、评分维度 |
| `scraper_bidding.py` | 招标平台数据爬虫，自动读取 config 的关键词和平台 |
| `analyzer.py` | 数据分析：行业评分计算、竞品对比、客户画像识别 |

## 复用方式（换项目只改 `config.py`）

- `KEYWORDS`：搜索关键词
- `BIDDING_PLATFORMS`：目标招标平台
- `INDUSTRY_KEYWORDS`：行业映射规则
- `COMPETITORS`：竞品信息
- `INDUSTRY_SCORES` / `SCORING_DIMENSIONS`：评分维度和权重

其他脚本自动随配置更新，无需改动。

## 运行命令

```bash
# 建议放至项目根的 scripts/ 目录下运行
python scraper_bidding.py    # 采集招标数据
python analyzer.py           # 输出分析结果到控制台
```

## 数据来源

- 中国招标投标公共服务平台（ctbpsp.com）
- 中国政府采购网（ccgp.gov.cn）
- 国家能源招标网、CPEM 全国电力设备管理网、地方公共资源交易中心等公开渠道
- 已采集 27 条真实中标公告（2024-2026），每条均附来源链接可溯源验证
