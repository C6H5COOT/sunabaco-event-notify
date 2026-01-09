import re
from datetime import date
from typing import List, Tuple, Optional

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtparser


EVENT_LIST_URL = "https://sunabaco.com/event/"
PRINT_LIMIT = 12  # ログに出す件数


def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=20, headers={"User-Agent": "event-notify-bot/0.1"})
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def parse_date_from_text(s: str) -> Optional[date]:
    """
    一覧のリンクテキストに「開催日:YYYY-MM-DD」っぽいのがある前提で拾う。
    例: "〇〇 開催日:2026–01–29"
    """
    s = s.replace("–", "-").replace("—", "-")
    m = re.search(r"開催日[:：]\s*([0-9]{4}[-/][0-9]{2}[-/][0-9]{2})", s)
    if not m:
        return None
    raw = m.group(1).replace("/", "-")
    try:
        return dtparser.parse(raw).date()
    except Exception:
        return None


def extract_event_links(list_html: str) -> List[Tuple[str, Optional[date], str]]:
    """
    戻り値: (url, date_or_none, link_text)
    """
    soup = BeautifulSoup(list_html, "html.parser")
    items: List[Tuple[str, Optional[date], str]] = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/event/" not in href:
            continue

        url = href if href.startswith("http") else ("https://sunabaco.com" + href)
        text = a.get_text(" ", strip=True)

        d = parse_date_from_text(text)
        items.append((url, d, text))

    # URLで重複除去
    seen = set()
    uniq = []
    for url, d, text in items:
        if url in seen:
            continue
        seen.add(url)
        uniq.append((url, d, text))
    return uniq


def main() -> None:
    print("=== SUNABACO Event List Fetch Test ===")
    print("URL:", EVENT_LIST_URL)

    html = fetch_html(EVENT_LIST_URL)
    links = extract_event_links(html)

    # 日付が取れるものを優先して、近い順に並べる（Noneは後ろ）
    links_sorted = sorted(links, key=lambda x: (x[1] is None, x[1] or date.max))

    print(f"抽出したイベントURL数: {len(links_sorted)}")
    print("")
    print("---- 開催日が近い順（上位） ----")

    for i, (url, d, text) in enumerate(links_sorted[:PRINT_LIMIT], start=1):
        ds = d.isoformat() if d else "????-??-??"
        print(f"{i:02d}. {ds} | {url}")
        # テキストも参考に出す（長いのでちょい短縮）
        short = text[:120] + ("..." if len(text) > 120 else "")
        print(f"    text: {short}")

    print("")
    print("✅ 一覧取得＆ソート表示 完了")


if __name__ == "__main__":
    main()
