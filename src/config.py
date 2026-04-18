"""設定ファイル。環境変数と検索クエリを一元管理。"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# PubMed 検索クエリ（虫垂関連）
# ------------------------------------------------------------
# 必要に応じて編集してください。
# 代替クエリ例:
#   - UC–虫垂関連に絞る:
#       '("appendix"[MeSH] OR "appendectomy"[MeSH]) AND '
#       '("ulcerative colitis"[MeSH] OR "inflammatory bowel diseases"[MeSH])'
#   - 虫垂腫瘍限定:
#       '"appendiceal neoplasms"[MeSH Terms]'
#   - レビューのみ:
#       末尾に ' AND (review[PT] OR systematic review[PT])' を追加
# ============================================================
PUBMED_QUERY = (
    '('
    '"appendix"[MeSH Terms] OR "appendicitis"[MeSH Terms] '
    'OR "appendiceal neoplasms"[MeSH Terms] '
    'OR "appendix"[Title/Abstract] OR "appendiceal"[Title/Abstract] '
    'OR "appendicitis"[Title/Abstract]'
    ') '
    'AND ("last 7 days"[PDat]) '
    'AND (English[Language] OR Japanese[Language])'
)

# 1回の実行で処理する最大論文数（コスト制御）
MAX_PAPERS_PER_RUN = 5

# ============================================================
# API 設定
# ============================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "")

# Claude モデル（最新の Sonnet）
CLAUDE_MODEL = "claude-sonnet-4-5"

# 投稿済み PMID を記録するファイル
POSTED_PMIDS_FILE = "data/posted_pmids.json"


def validate() -> None:
    """必須環境変数のチェック"""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not DISCORD_WEBHOOK_URL:
        missing.append("DISCORD_WEBHOOK_URL")
    if missing:
        raise RuntimeError(
            f"必須の環境変数が設定されていません: {', '.join(missing)}\n"
            f".env ファイルまたは GitHub Secrets を確認してください。"
        )
