# Appendix Claude Bot

PubMed から虫垂（appendix）関連の新着論文を自動取得し、**Claude Sonnet** で日本語解説を生成して Discord に投稿する bot です。

- **実行基盤**: GitHub Actions（cron 実行）
- **API**: PubMed E-utilities（無料）+ Anthropic Claude Sonnet 4.5
- **想定コスト**: 約 **$2〜5 / 月**（5 論文/日の場合）

---

## ⚠️ 重要：既存の Gemini 版 bot との混同に注意

既に `Appendix` リポジトリで Gemini 版の appendix bot を運用している場合、**そのリポジトリに本プロジェクトのファイルを追加しないでください**。以下の点で設計が異なり、同じリポジトリに混ぜるとワークフローが壊れます:

| 項目 | Gemini 版（既存） | Claude 版（本プロジェクト） |
|---|---|---|
| メインファイル | `appendix_bot.py` など（ルート直下） | `src/main.py` |
| Webhook 変数名 | `DISCORD_WEBHOOK_APPENDIX` など | `DISCORD_WEBHOOK_URL` |
| 使用 API | Gemini | Anthropic (Claude) |
| PMID 記録先 | `/tmp/appendix_seen.json` | `data/posted_pmids.json` |

**必ず新規リポジトリとして作成してください**（後述）。既存の Gemini 版は壊さず、並行運用や比較が可能です。

---

## 構成

```
appendix-claude-bot/
├── .github/
│   └── workflows/
│       └── daily_digest.yml     # GitHub Actions: 毎朝 JST 08:00 に実行
├── src/
│   ├── main.py                  # エントリポイント
│   ├── config.py                # 設定・検索クエリ
│   ├── pubmed_client.py         # PubMed API
│   ├── claude_client.py         # Claude Sonnet API
│   └── discord_client.py        # Discord Webhook 投稿
├── data/
│   └── posted_pmids.json        # 投稿済み PMID 管理
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 導入手順

### 1. Discord Webhook の作成

1. Discord で投稿先のサーバー／チャンネルを開く
2. チャンネル右の歯車アイコン（チャンネル編集）→ **連携サービス** → **ウェブフック**
3. **新しいウェブフック** をクリック → 名前を設定（例: `Appendix Claude`）
4. **ウェブフック URL をコピー** ボタンで URL を控える

> 💡 Gemini 版と投稿を混ぜたくない場合は、**専用チャンネルを別途作成**することをおすすめします。

### 2. Anthropic API キーの取得

1. <https://console.anthropic.com/> にログイン
2. **API Keys** → **Create Key** でキーを発行（`sk-ant-...`）
3. **Billing** で支払い方法を登録し、$5〜20 をチャージ
4. **Usage limits** で月額上限を $20 に設定（暴発防止）

### 3. PubMed API キー（任意・推奨）

1. <https://account.ncbi.nlm.nih.gov/> にログイン
2. **Account Settings** → **API Key Management** で発行
3. なくても動作するが、ある方がレート制限が緩和される（3req/s → 10req/s）

### 4. ★★★ 新規 GitHub リポジトリの作成（既存とは別物として）

**既存の `Appendix` リポジトリとは別**に、新しいリポジトリを作成してください:

1. <https://github.com/> にログイン
2. 右上の **「+」** → **「New repository」**
3. 入力:
   - **Repository name**: `appendix-claude-bot`（既存と被らない名前）
   - **Public** を選択（GitHub Actions 無料のため）
   - **Add a README file** は **チェックしない**
4. **「Create repository」** をクリック

作成後、本プロジェクトの zip を解凍して中身をアップロード:

- **方法 A（ブラウザでアップロード）**:
  - 空リポジトリに表示される「uploading an existing file」をクリック
  - 解凍した `appendix-claude-bot` フォルダの**中身**（`.github`、`src`、`data`、各ファイル）をすべてドラッグ&ドロップ
  - 隠しフォルダ `.github` を忘れずに（Mac: `⌘+Shift+.` で表示）
  - 「Commit changes」

- **方法 B（GitHub Desktop）**: <https://desktop.github.com/> を使えば GUI で完結

### 5. GitHub Secrets の登録

リポジトリの **Settings → Secrets and variables → Actions → New repository secret** で以下を登録:

| Secret 名 | 値 | 必須 |
|---|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | ✅ |
| `DISCORD_WEBHOOK_URL` | `https://discord.com/api/webhooks/...` | ✅ |
| `PUBMED_API_KEY` | NCBI で発行したキー | 任意 |
| `PUBMED_EMAIL` | 自分のメールアドレス | 任意 |

> ⚠️ 既存の Gemini 版で `DISCORD_WEBHOOK_APPENDIX` などを登録していても、それとは別に本リポジトリには **`DISCORD_WEBHOOK_URL`** という名前で登録する必要があります（Secret はリポジトリごとに独立）。

### 6. Workflow permissions の確認

**Settings → Actions → General** まで進み、**Workflow permissions** セクションで:

- ☑ **Read and write permissions** を選択
- **Save** をクリック

これを忘れると、`data/posted_pmids.json` の自動 commit が失敗します。

### 7. 初回実行テスト

1. リポジトリの **Actions** タブへ移動
2. 左メニューから **Daily Appendix Paper Digest** を選択
3. **Run workflow** → 緑の **Run workflow** ボタンで手動実行
4. 1〜2 分待ち、Discord に論文解説が流れてくれば成功 🎉

---

## ローカル動作確認（任意）

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env を編集して API キー等を記入

python src/main.py
```

---

## カスタマイズ

### 検索クエリの変更

`src/config.py` の `PUBMED_QUERY` を編集します。

- **UC–虫垂関連だけ絞り込みたい**:
  ```python
  PUBMED_QUERY = (
      '("appendix"[MeSH] OR "appendectomy"[MeSH]) AND '
      '("ulcerative colitis"[MeSH] OR "inflammatory bowel diseases"[MeSH])'
  )
  ```
- **虫垂腫瘍限定**:
  ```python
  PUBMED_QUERY = '"appendiceal neoplasms"[MeSH Terms]'
  ```
- **レビューのみ**: 末尾に `AND (review[PT] OR systematic review[PT])` を追加

### 実行頻度の変更

`.github/workflows/daily_digest.yml` の `cron` を編集:

| 用途 | cron 式 (UTC) | JST |
|---|---|---|
| 毎朝 8 時（デフォルト） | `0 23 * * *` | 毎日 08:00 |
| 週1（月曜朝） | `0 23 * * 1` | 月曜 08:00 |
| 平日のみ | `0 23 * * 1-5` | 平日 08:00 |

### 処理本数の変更

`src/config.py` の `MAX_PAPERS_PER_RUN` を変更。5 → 10 でも月 $5 以内。

---

## コスト試算

Claude Sonnet 4.5（$3/Mtok input, $15/Mtok output）:

| 項目 | 使用量/日 | 月額 |
|---|---|---|
| 入力トークン（5 論文/日） | ~5,000 tok | ~$0.45 |
| 出力トークン（5 論文/日） | ~4,000 tok | ~$1.80 |
| **合計** | | **~$2.25/月** |

$20 予算の 1/10 程度です。

---

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `No such file or directory: 'appendix_bot.py'` | **これは古い（Gemini 版の）ワークフローが残っている証拠**。本プロジェクト用に新規リポジトリを作ってアップロードし直してください |
| Actions で `Missing ANTHROPIC_API_KEY` エラー | Secrets が正しく登録されているか確認 |
| Discord に何も投稿されない | Webhook URL が正しいか、チャンネル権限を確認 |
| `posted_pmids.json` が commit されない | Settings → Actions → General → Workflow permissions で **Read and write permissions** を有効化 |
| 論文が全部既読判定される | `data/posted_pmids.json` を空配列 `[]` にリセット |
| PubMed から 429 エラー | `PUBMED_API_KEY` を設定するか、実行頻度を下げる |
| `.github` フォルダがアップロードされていない | 隠しフォルダの表示設定を確認してから再アップロード |

---

## 既存 Gemini 版との比較運用のすすめ

並行運用すると、同じ論文に対して Gemini と Claude の解説を比較できます。好みや精度を評価した上で、将来的にどちらか一方に統一する判断材料になります。

Discord 上で:
- `#appendix-gemini` チャンネル → 既存の Gemini 版
- `#appendix-claude` チャンネル → 本プロジェクト

のように分けておくと比較しやすいです。

---

## ライセンス

MIT（必要に応じて変更してください）
