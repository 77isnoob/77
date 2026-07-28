#!/usr/bin/env python3
"""
中国政府采购网 - 人力相关招标极简巡检脚本
每天凌晨低峰跑一次，仅拉首页公告列表，去重保存。

用法: python3 ccgp_hr_scraper.py [--all]
数据输出: output/ccgp_hr/YYYY-MM-DD.json
日志输出: output/ccgp_hr/last_run.log
"""

import json
import os
import re
import time
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

# ── 配置 ──
SEARCH_URL = "http://search.ccgp.gov.cn/bxsearch"
DATA_DIR = "output/ccgp_hr"
DUPE_FILE = "output/ccgp_hr/seen_urls.json"
DAYS_BACK = 3
MAX_PAGES = 2
REQUEST_DELAY = 5  # 低频友好，每次请求间隔5秒

# 人力相关搜索关键词（服务器端搜索用）
SEARCH_KEYWORDS = [
    "人力资源", "劳务派遣", "人事外包", "人力外包",
    "招聘服务", "人才服务", "用工服务", "劳务外包",
    "人力资源服务", "人事代理", "岗位外包",
]

# 补充过滤词（中标公告也值得关注——看谁中标了）
SUPPLEMENTARY_KEYWORDS = [
    "物业", "保洁", "安保", "食堂", "后勤", "客服",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "http://www.ccgp.gov.cn/",
}


def load_seen():
    if os.path.exists(DUPE_FILE):
        with open(DUPE_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(DUPE_FILE, "w") as f:
        json.dump(sorted(seen), f, ensure_ascii=False, indent=2)


def fetch_page(keyword, page=1):
    """用关键字搜索一页"""
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")

    params = {
        "searchtype": "1",
        "page_index": str(page),
        "start_time": start,
        "end_time": end,
        "kw": keyword,
    }

    try:
        resp = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        if "频繁访问" in resp.text:
            return None, "rate_limited"
        return resp.text, None
    except Exception as e:
        return None, str(e)


def parse_page(html, keyword):
    """解析一页结果"""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    total_text = soup.get_text()
    total_match = re.search(r"共找到\s*(\d+)\s*条", total_text)
    total = int(total_match.group(1)) if total_match else 0

    for a_tag in soup.find_all("a", href=re.compile(r"ccgp\.gov\.cn/cggg/")):
        title = a_tag.get_text(strip=True)
        url = a_tag.get("href", "")
        if not title or not url:
            continue

        parent_li = a_tag.find_parent("li")
        li_text = parent_li.get_text() if parent_li else ""

        date_match = re.search(r"(\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2})", li_text)
        pub_date = date_match.group(1) if date_match else ""

        purch_match = re.search(r"采购人[：:]\s*([^\n|]+)", li_text)
        purchaser = purch_match.group(1).strip() if purch_match else ""

        agent_match = re.search(r"代理机构[：:]\s*([^\n|]+)", li_text)
        agent = agent_match.group(1).strip() if agent_match else ""

        # 判断公告类型
        notice_type = ""
        for t in ["公开招标", "竞争性磋商", "竞争性谈判", "中标公告", "成交公告",
                   "更正公告", "终止公告", "其他公告", "询价公告", "单一来源"]:
            if t in li_text:
                notice_type = t
                break

        items.append({
            "title": title,
            "url": url,
            "publish_date": pub_date,
            "purchaser": purchaser,
            "agent": agent,
            "notice_type": notice_type,
            "search_keyword": keyword,
        })

    return items, total


def run(all_mode=False):
    keywords = SEARCH_KEYWORDS + SUPPLEMENTARY_KEYWORDS if all_mode else SEARCH_KEYWORDS
    mode_label = "全量(含补充)" if all_mode else "核心人力"

    print(f"🔍 CCGP 人力招标巡检  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   模式: {mode_label}")
    print(f"   范围: 最近{DAYS_BACK}天, 每个关键词最多{MAX_PAGES}页")
    print(f"   请求间隔: {REQUEST_DELAY}秒")
    print()

    seen = load_seen()
    all_new = []

    for kw in keywords:
        kw_results = 0
        for page in range(1, MAX_PAGES + 1):
            html, err = fetch_page(kw, page)

            if err == "rate_limited":
                print(f"  ⚠️  触发反爬，等待10秒后重试...")
                time.sleep(10)
                html, err = fetch_page(kw, page)
                if err:
                    print(f"  ❌ 仍失败({err})，跳过关键词「{kw}」")
                    break

            if not html:
                break

            items, total = parse_page(html, kw)
            if not items:
                break

            if page == 1:
                print(f"  📌 「{kw}」: 约 {total} 条结果")

            for item in items:
                if item["url"] not in seen:
                    seen.add(item["url"])
                    all_new.append(item)
                    kw_results += 1

            if page < MAX_PAGES:
                time.sleep(REQUEST_DELAY)

        if kw_results > 0:
            print(f"    → 新增 {kw_results} 条")

    print(f"\n✅ 巡检完成，共新增 {len(all_new)} 条人力相关招标")

    if all_new:
        os.makedirs(DATA_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        outfile = f"{DATA_DIR}/{today}.json"

        existing = []
        if os.path.exists(outfile):
            with open(outfile) as f:
                existing = json.load(f)

        existing_urls = {item["url"] for item in existing}
        combined = existing + [i for i in all_new if i["url"] not in existing_urls]

        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)

        save_seen(seen)

        # 打印摘要
        print()
        for i, item in enumerate(all_new):
            tag = "🟢" if item["notice_type"] in ["公开招标", "竞争性磋商", "竞争性谈判"] else "🟡"
            print(f"  {tag} [{item['notice_type']}] {item['title'][:60]}")
            print(f"      采购人: {item['purchaser']}  |  {item['publish_date']}")
            print(f"      → {item['url']}")
            print()
    else:
        print("   本次无新增")

    return all_new


if __name__ == "__main__":
    import sys
    all_mode = "--all" in sys.argv
    run(all_mode=all_mode)
