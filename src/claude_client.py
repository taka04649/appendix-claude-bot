"""Claude Sonnet API クライアント（論文要約・解説）。"""
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """あなたは消化器内科・消化器外科領域に精通した医学論文解説者です。
虫垂（appendix）に関する論文を、日本の臨床医（専攻医〜スタッフレベル）向けに解説してください。

出力形式:
【一行サマリー】1文で研究の結論
【背景】2-3文で先行研究との位置づけ
【方法】研究デザイン・対象・主要評価項目を簡潔に
【結果】主要な数値（OR, HR, 95%CI, p値など）を含めて3-4文で
【臨床的含意】日常臨床への影響を2-3文で
【Limitation】論文内で言及されている、あるいは明らかな限界点

重要な注意:
- Abstract のみから解説するため、推測による内容追加はしない
- 数値は abstract に記載されたものだけを記載し、創作しない
- UC・IBDとの関連、虫垂腫瘍、急性虫垂炎の保存的治療など臨床的に関心の高いトピックは特に丁寧に
- 専門用語は日本語＋英語併記（例: 粘液嚢胞腺癌（mucinous cystadenocarcinoma））
- 全体で800-1000字程度"""


def summarize_paper(paper: dict) -> str:
    """論文を日本語で解説する。"""
    user_msg = f"""以下の論文を解説してください。

タイトル: {paper['title']}
著者: {paper['authors']}
雑誌: {paper['journal']} ({paper['year']})
PMID: {paper['pmid']}

Abstract:
{paper['abstract']}"""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text
