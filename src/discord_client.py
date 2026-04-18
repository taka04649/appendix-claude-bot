"""Discord Webhook への投稿クライアント。"""
from datetime import datetime

import requests

# Discord embed の description は 4096 文字、全体で 6000 文字まで
MAX_DESC_LEN = 4000
MAX_TITLE_LEN = 250
MAX_FIELD_VALUE_LEN = 1024


def post_to_discord(webhook_url: str, paper: dict, summary: str) -> None:
    """1論文 = 1 embed として投稿する。"""
    title = (paper.get("title") or "Untitled")[:MAX_TITLE_LEN]
    desc = summary[:MAX_DESC_LEN]

    fields = [
        {
            "name": "Journal",
            "value": f"{paper.get('journal', 'N/A')} ({paper.get('year', 'N/A')})"[:MAX_FIELD_VALUE_LEN],
            "inline": True,
        },
        {
            "name": "Authors",
            "value": (paper.get("authors") or "N/A")[:MAX_FIELD_VALUE_LEN],
            "inline": True,
        },
        {
            "name": "PMID",
            "value": paper.get("pmid", "N/A"),
            "inline": True,
        },
    ]

    if paper.get("doi"):
        fields.append({
            "name": "DOI",
            "value": f"[{paper['doi']}](https://doi.org/{paper['doi']})",
            "inline": False,
        })

    embed = {
        "title": f"📄 {title}",
        "url": paper.get("url", ""),
        "description": desc,
        "color": 0x4A90E2,
        "fields": fields,
        "footer": {"text": "Appendix Claude Bot · via PubMed + Claude Sonnet"},
    }

    payload = {"embeds": [embed]}
    r = requests.post(webhook_url, json=payload, timeout=30)
    r.raise_for_status()


def post_header(webhook_url: str, n_papers: int) -> None:
    """その日のヘッダーメッセージを投稿する。"""
    today = datetime.now().strftime("%Y-%m-%d")
    content = (
        f"🩺 **Appendix Papers Daily Digest — {today}**\n"
        f"本日の新着論文: **{n_papers}本**"
    )
    r = requests.post(webhook_url, json={"content": content}, timeout=30)
    r.raise_for_status()
