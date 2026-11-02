# ============================================================
# 竞品分析 + 客户打分卡模型
# 基于 config.py 中的真实调研数据进行分析
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from config import COMPETITORS, INDUSTRY_SCORES, SCORING_DIMENSIONS, INDUSTRY_KEYWORDS

# ---- 1. 竞品行业分布分析 ----

def analyze_competitor_industries():
    """统计竞品覆盖的行业分布"""
    industry_count = {}
    for comp in COMPETITORS:
        for ind in comp["industries"]:
            industry_count[ind] = industry_count.get(ind, 0) + 1

    print("\n===== 竞品行业分布 =====")
    sorted_industries = sorted(industry_count.items(), key=lambda x: x[1], reverse=True)
    for ind, count in sorted_industries:
        companies = [c["name"] for c in COMPETITORS if ind in c["industries"]]
        print(f"  {ind}: {count}家 ({', '.join(companies)})")

    return industry_count


# ---- 2. 竞品对比表 ----

def generate_competitor_comparison():
    """生成竞品优劣势对比数据"""
    print("\n===== 竞品对比表 =====")

    rows = []
    for comp in COMPETITORS:
        row = {
            "公司名称": comp["name"],
            "成立年份": comp.get("founded", "N/A"),
            "核心团队/背景": comp.get("team", comp.get("full_name", "")),
            "融资/规模": comp.get("funding", comp.get("market_share", "")),
            "核心技术": comp["core_tech"],
            "主要客户": "、".join(comp["key_clients"][:3]),
            "覆盖行业": "、".join(comp["industries"]),
            "算法岗占比": comp.get("algo_team_ratio", "N/A"),
            "销售岗占比": comp.get("sales_team_ratio", "N/A"),
            "核心优势": "\n".join([f"  + {s}" for s in comp["strengths"]]),
            "主要劣势": "\n".join([f"  - {s}" for s in comp["weaknesses"]]),
            "数据来源": comp.get("data_source", "网络调研"),
        }
        rows.append(row)
        print(f"  {comp['name']}: 算法岗{comp.get('algo_team_ratio','?')} | 销售岗{comp.get('sales_team_ratio','?')}")

    return rows


# ---- 3. 算法岗 vs 销售岗对比 ----

def analyze_team_structure():
    """分析竞品算法岗与销售岗比例"""
    print("\n===== 算法岗 vs 销售岗 对比 =====")
    print(f"  {'公司':<12} {'算法岗占比':<12} {'销售岗占比':<12} {'类型'}")
    print(f"  {'-'*50}")

    for comp in COMPETITORS:
        algo = comp.get("algo_team_ratio", "N/A")
        sales = comp.get("sales_team_ratio", "N/A")
        # 判断公司类型
        if "约70%" in algo or "约65%" in algo:
            comp_type = "技术驱动型"
        elif "约55%" in algo or "约60%" in algo:
            comp_type = "技术+市场均衡型"
        else:
            comp_type = "市场导向型"

        print(f"  {comp['name']:<12} {algo:<12} {sales:<12} {comp_type}")

    # 结论
    print("\n  结论: 行业整体以技术驱动为主，头部公司算法岗占比普遍在50%-70%")
    print("  说明声纹诊断行业仍处于技术壁垒建设期，算法能力是核心竞争力。")


# ---- 4. 客户决策打分卡模型 ----

def calculate_industry_scores():
    """计算各行业综合得分并排名"""
    print("\n===== 客户决策打分卡 =====")

    weights = {k: v["weight"] for k, v in SCORING_DIMENSIONS.items()}

    results = []
    for industry, scores in INDUSTRY_SCORES.items():
        # 加权计算
        total = (
            scores["停机损失"] * weights["设备单次停机损失金额"]
            + scores["自动化"] * weights["产线自动化程度"]
            + scores["AI接受度"] * weights["管理层对AI接受度"]
            + scores["设备价值"] * weights["设备价值集中度"]
            + scores["合规压力"] * weights["安全/环保合规压力"]
        )
        results.append({
            "行业": industry,
            "停机损失": scores["停机损失"],
            "自动化": scores["自动化"],
            "AI接受度": scores["AI接受度"],
            "设备价值": scores["设备价值"],
            "合规压力": scores["合规压力"],
            "加权总分": round(total, 2),
            "备注": scores.get("note", ""),
        })

    # 按总分排序
    results.sort(key=lambda x: x["加权总分"], reverse=True)

    print(f"  {'行业':<16} {'停机损失':<10} {'自动化':<8} {'AI接受':<8} {'设备价值':<8} {'合规':<8} {'加权总分':<10}")
    print(f"  {'-'*70}")
    for r in results:
        print(f"  {r['行业']:<16} {r['停机损失']:<10} {r['自动化']:<8} {r['AI接受度']:<8} {r['设备价值']:<8} {r['合规压力']:<8} {r['加权总分']:<10}")

    return results


def find_best_customer_profile(results):
    """找出最容易成交的客户画像"""
    print("\n===== 最容易成交的客户画像 =====")

    # 取总分最高的前3个行业
    top3 = results[:3]

    print(f"  推荐优先拓展行业: {', '.join([r['行业'] for r in top3])}")
    print()
    print("  客户画像特征:")
    print("  ┌─────────────────────────────────────────┐")

    # 高度概括
    high_score_dims = []
    for r in top3:
        dims = []
        if r["停机损失"] >= 5: dims.append("停机损失巨大")
        if r["自动化"] >= 4: dims.append("高度自动化")
        if r["AI接受度"] >= 4: dims.append("AI接受度高")
        if r["设备价值"] >= 4: dims.append("设备价值高")
        if r["合规压力"] >= 5: dims.append("合规压力大")
        print(f"  │ {r['行业']}: {', '.join(dims)}")

    print("  ├─────────────────────────────────────────┤")
    print("  │ 核心画像:                                │")
    print("  │  - 单台设备价值 > 500万元                 │")
    print("  │  - 24小时连续生产，停机即损失             │")
    print("  │  - 已有AI/数字化项目落地经验              │")
    print("  │  - 行业有强制安全监管要求                 │")
    print("  │  - 央企/大型国企为主（预算充足）          │")
    print("  └─────────────────────────────────────────┘")

    return top3


# ---- 5. 市场数据汇总 ----

def market_summary():
    """汇总行业市场规模数据"""
    print("\n===== 市场规模数据 =====")
    market_data = [
        ("工业声学监测服务", "CR5=63.4%（2025年）", "博研咨询 2026"),
        ("工业故障听诊器", "43.8亿元（2025年），同比+18.6%", "博研咨询 2026"),
        ("全球声纹监测系统", "36.87亿元（2025年），预计2032年达78.59亿元", "鼎和创新科技"),
        ("基于声学技术的设备监测", "超3500亿元（蓝海市场）", "中商产业研究院"),
        ("工业声纹识别(中国)", "28.6亿元（2025年），CAGR 29.8%", "博研咨询"),
    ]
    for name, size, source in market_data:
        print(f"  {name}: {size}  [{source}]")
    return market_data


# ---- 主入口 ----

if __name__ == "__main__":
    print("=" * 60)
    print("  AI+声音声纹诊断 — 行业竞品分析 & 客户画像模型")
    print("=" * 60)

    # 1. 竞品行业分布
    industry_dist = analyze_competitor_industries()

    # 2. 竞品对比表
    comp_table = generate_competitor_comparison()

    # 3. 算法岗 vs 销售岗
    analyze_team_structure()

    # 4. 市场规模
    market_data = market_summary()

    # 5. 打分卡
    scores = calculate_industry_scores()

    # 6. 客户画像
    top_profiles = find_best_customer_profile(scores)

    print("\n" + "=" * 60)
    print("  分析完成。数据可用于生成 Excel 和 PPT。")
    print("=" * 60)