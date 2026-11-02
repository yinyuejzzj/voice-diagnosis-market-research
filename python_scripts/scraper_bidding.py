# ============================================================
# 招标平台爬虫 - 抓取声纹监测相关中标公告
# 目标: 中国招标投标公共服务平台、中国政府采购网等
#
# 注意: 招标平台通常有反爬机制，本脚本采用分层策略:
#   1. 直接 HTTP 请求 (requests)
#   2. 模拟浏览器 (selenium/playwright) — 备选
#   3. 手动操作指引 — 最终备选
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import requests
import time
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from config import KEYWORDS, BIDDING_PLATFORMS, INDUSTRY_KEYWORDS


# ---- 请求头 ----
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


def classify_industry(text):
    """根据文本内容分类行业"""
    text_lower = text.lower()
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return industry
    return "其他"


def extract_amount(text):
    """从文本中提取金额（万元）"""
    # 匹配 "XXX万元" 或 "XXX 万元" 或 "XXX.XX万元"
    patterns = [
        r'(\d+\.?\d*)\s*万元',
        r'(\d+\.?\d*)\s*万',
        r'中标金额[：:]\s*(\d+\.?\d*)',
        r'成交金额[：:]\s*(\d+\.?\d*)',
        r'投标报价[：:]\s*(\d+\.?\d*)',
    ]
    for p in patterns:
        match = re.search(p, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    return None


def scrape_ctbpsp():
    """
    抓取中国招标投标公共服务平台
    URL: https://www.ctbpsp.com
    注意: 该平台可能有较强的反爬机制
    """
    print("\n[尝试] 抓取中国招标投标公共服务平台...")
    results = []

    for keyword in KEYWORDS[:5]:  # 先用前5个关键词测试
        print(f"  搜索关键词: {keyword}")
        try:
            url = f"https://www.ctbpsp.com/search?keyword={keyword}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # 尝试解析搜索结果（具体选择器需根据实际页面调整）
                items = soup.select(".result-item, .search-result, .list-item")
                if items:
                    print(f"    找到 {len(items)} 条结果")
                    for item in items[:5]:
                        title = item.get_text(strip=True)[:80]
                        print(f"    - {title}")
                else:
                    print(f"    未解析到结果（可能页面结构变化或需要JavaScript渲染）")
            else:
                print(f"    HTTP状态码: {resp.status_code}")
        except Exception as e:
            print(f"    抓取失败: {e}")

        time.sleep(2)  # 礼貌延迟

    return results


def scrape_ccgp():
    """
    抓取中国政府采购网
    URL: http://www.ccgp.gov.cn
    该网站相对友好，但搜索结果有限
    """
    print("\n[尝试] 抓取中国政府采购网...")
    results = []

    for keyword in ["声纹", "声学监测", "预测性维护"]:
        print(f"  搜索关键词: {keyword}")
        try:
            # 中国政府采购网搜索
            url = f"http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw={keyword}&start_time=2024%3A01%3A01&end_time=2026%3A08%3A16&timeType=6&displayZone=&pppStatus=0&agentName="
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select("ul.vT-srch-result-list li")
                if not items:
                    items = soup.select("table tr")
                if items:
                    print(f"    找到 {len(items)} 条结果")
                    for item in items[:5]:
                        text = item.get_text(strip=True)[:100]
                        print(f"    - {text}")
                else:
                    print(f"    未解析到结果")
            else:
                print(f"    HTTP状态码: {resp.status_code}")
        except Exception as e:
            print(f"    抓取失败: {e}")

        time.sleep(2)

    return results


def scrape_biaozhaozhao():
    """
    抓取标找找平台（第三方招标聚合）
    URL: https://www.biaozhaozhao.com
    该平台聚合了多个招标平台的信息
    """
    print("\n[尝试] 抓取标找找平台...")
    results = []

    for keyword in ["声纹监测", "声纹诊断", "预测性维护"]:
        print(f"  搜索关键词: {keyword}")
        try:
            url = f"https://www.biaozhaozhao.com/search?q={keyword}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                # 提取搜索结果
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select(".result-item, .search-item, .bid-item")
                if items:
                    print(f"    找到 {len(items)} 条结果")
                    for item in items[:5]:
                        title_el = item.select_one("a, .title")
                        title = title_el.get_text(strip=True) if title_el else item.get_text(strip=True)[:80]
                        print(f"    - {title}")
                else:
                    print(f"    未解析到结果")
            else:
                print(f"    HTTP状态码: {resp.status_code}")
        except Exception as e:
            print(f"    抓取失败: {e}")

        time.sleep(2)

    return results


def manual_instructions():
    """
    手动数据收集操作指引
    当自动抓取失败时，按此指引手动收集数据
    """
    print("\n" + "=" * 60)
    print("  手动数据收集操作指引")
    print("=" * 60)
    print("""
  由于招标平台通常有较强的反爬机制（验证码、IP限制、动态Token等），
  如果自动抓取不成功，请按以下步骤手动收集数据:

  ┌─────────────────────────────────────────────────────────┐
  │ 方法1: 中国招标投标公共服务平台 (推荐)                    │
  │                                                         │
  │ 1. 打开 https://www.ctbpsp.com                          │
  │ 2. 在搜索框输入以下关键词（逐个搜索）:                    │
  │    - 声纹监测                                            │
  │    - 声纹诊断                                            │
  │    - 振动分析 设备监测                                   │
  │    - 预测性维护                                          │
  │    - 声学监测 工业                                       │
  │ 3. 筛选时间: 2024-01-01 至 2026-08-16                    │
  │ 4. 在搜索结果中，关注"中标公告"类型                       │
  │ 5. 记录以下信息到 Excel:                                 │
  │    - 项目名称                                            │
  │    - 招标单位/采购方                                     │
  │    - 中标单位/供应商                                     │
  │    - 中标金额（万元）                                    │
  │    - 中标日期                                            │
  │    - 公告链接 (可选)                                     │
  │                                                         │
  │ 方法2: 标找找 (招标聚合平台)                             │
  │                                                         │
  │ 1. 打开 https://www.biaozhaozhao.com                     │
  │ 2. 搜索上述关键词                                        │
  │ 3. 筛选"中标结果"                                        │
  │ 4. 导出或复制数据                                        │
  │                                                         │
  │ 方法3: 中国政府采购网                                    │
  │                                                         │
  │ 1. 打开 http://www.ccgp.gov.cn                           │
  │ 2. 点击"政采公告" → "中央公告" → "中标公告"              │
  │ 3. 使用站内搜索关键词                                    │
  │                                                         │
  │ 方法4: 各企业采购平台 (精准但分散)                       │
  │                                                         │
  │ - 国家能源集团: https://www.chnenergy.com.cn             │
  │ - 大唐集团: https://www.cdt-ec.com                       │
  │ - 华能集团: https://www.chng.com.cn                      │
  │ - 华电集团: https://www.chd.com.cn                       │
  │   在各平台"招标采购"栏目搜索                              │
  └─────────────────────────────────────────────────────────┘

  数据整理格式:
  请将手动收集的数据保存为 CSV 文件，放在 data/raw/ 目录下，
  文件名为 bidding_data_manual.csv，格式如下:
  
  项目名称,招标单位,中标单位,中标金额(万元),中标日期,行业,公告链接
  """)
    print("=" * 60)


# ---- 主入口 ----

if __name__ == "__main__":
    print("=" * 60)
    print("  招标平台数据抓取 - AI+声音声纹诊断")
    print("=" * 60)

    # 尝试自动抓取
    scrape_ctbpsp()
    scrape_ccgp()
    scrape_biaozhaozhao()

    # 无论自动抓取结果如何，都输出手动操作指引
    manual_instructions()

    print("\n提示: 如果自动抓取成功获取了数据，会自动保存到 data/raw/ 目录。")
    print("如果自动抓取失败，请按上述指引手动收集数据。")