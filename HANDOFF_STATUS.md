# HANDOFF_STATUS.md — オーナー向け最終 TODO

Evaporator Labs / Reaction Heat Energy Calculator — Microsoft Store 公開準備
作成日: 2026-04-22
作成者: Cowork セッション (COWORK_BRIEF.md §2 Todo 実行結果)
宛先: flying.rotavap@gmail.com

---

## A. Cowork が完了した作業 (このセッションの成果物)

| # | 作業 | 成果物 | 状態 |
|---|---|---|---|
| 1 | dist/ 再ビルドと内容検証 | `dist/` (3.6 MB) | PASS — 必須 9 ファイル揃い、開発ディレクトリ混入なし |
| 2 | git 状態確認と機密情報スキャン | 本ファイル §B の status サマリ | クリーン — AIza / sk- / password / PRIVATE KEY / .env いずれも未検出 |
| 3 | Store リスティング改善案 | `STORE_LISTING.review.md` | diff 形式で EN/JA 両方の推敲案を出力 |
| 4 | 価格決定案 | `PRICING_DECISION.md` | 5 項目の推奨値・理由・代替案差分を記載 |
| 5 | PWA ローカル監査 | `scripts/pwa_audit.py` + `PWA_AUDIT.md` | 33/33 PASS (ローカル HTTP 経由含む) |
| 6 | 本ハンドオフ文書 | `HANDOFF_STATUS.md` | (このファイル) |

### Cowork が **実行しなかった** 作業 (制約事項より)

- `git commit` — 明示依頼まで保留
- `git push` — 人間承認事項
- 原本 (`STORE_LISTING.md`, `PRICING_STRATEGY.md`) への直接書き込み
- Partner Center / PWABuilder / Cloudflare Pages への実操作 (UI 認証を要するため)

---

## B. git 現況サマリ (Step 2 結果)

現在ブランチ: `master`
コミット履歴: `dda1059 Initial commit: chemistry calculation platform` のみ

| 種別 | 件数 | 主な対象 |
|---|---|---|
| Modified (M) | 2 | `.gitignore`, `frontend/src/App.css` |
| Deleted (D) | 112 | `pfd-generator/` 配下, `ts_calculator/` 配下 (初期コミット分の削除) |
| Untracked (??) | 16 | Store 公開用ファイル (`index.html`, `manifest.json`, `service-worker.js`, `icons/`, `privacy/`, `_headers`, `_redirects`, `build.sh`, Store ドキュメント一式) |

### 機密情報スキャン結果

| パターン | 結果 |
|---|---|
| `AIza[0-9A-Za-z_-]{30,}` (Google API) | 未検出 |
| `sk-[A-Za-z0-9]{40,}` (OpenAI API) | 未検出 |
| `password = "..."` (平文) | 未検出 |
| `PRIVATE KEY` | `COWORK_BRIEF.md` 内のパターン記載のみ (偽陽性) |
| `.env*` ファイル | 存在せず |

---

## C. オーナー (人間) が実行すべきタスク (順序付き)

以下は Cowork が実行できない、または承認を要するため人間に残したタスクです。上から順に実施してください。

### C-1. リスティング改善の採否判断 (所要 15 分)

1. `STORE_LISTING.review.md` を読む
2. 採用する改善点を `STORE_LISTING.md` 原本に手動反映 (Cowork は原本を触っていない)
3. `PRICING_DECISION.md` は **オーナー確定版** として保管済 ($0.99 イントロ → $4.99 買い切り、パラメータ OSS 公開、Reddit 告知)

### C-2. 既存 GitHub リポジトリに remote 接続 (所要 5 分)

既存リポジトリ: **https://github.com/flyingevaporator-cmyk/reaction-heat-calculator**

ローカルに remote が未設定の場合のみ初回の紐付けが必要:

```bash
cd C:\Users\ko\claude\calc

# 既存 remote の確認
git remote -v

# origin が未設定なら追加
git remote add origin https://github.com/flyingevaporator-cmyk/reaction-heat-calculator.git

# 既に別 URL で origin が登録されている場合は上書き
# git remote set-url origin https://github.com/flyingevaporator-cmyk/reaction-heat-calculator.git
```

ブランチ名の整合:

```bash
# 現在 master の場合、Cloudflare Pages 既定の main に合わせる
git branch -m master main
```

### C-3. Git コミット & push (所要 10 分)

```bash
cd C:\Users\ko\claude\calc

# 何が対象か再確認
git status

# 既存リポに内容がある場合は先に取り込む (空リポならスキップ可)
git pull origin main --allow-unrelated-histories

# Store 公開に必要なファイル一式をステージ
git add .gitignore build.sh _headers _redirects robots.txt sitemap.xml 2>nul
git add index.html manifest.json service-worker.js
git add icons/ privacy/ scripts/
git add DEPLOY.md STORE_SUBMISSION.md STORE_LISTING.md PRICING_STRATEGY.md
git add STORE_LISTING.review.md PRICING_DECISION.md PWA_AUDIT.md HANDOFF_STATUS.md COWORK_BRIEF.md

# frontend/, backend/, pfd-generator/, ts_calculator/ の削除 or 変更は Store 公開とは無関係なので、別コミットにするか判断
# 今回の Store 提出に必要なものだけコミットする推奨:
git commit -m "Prepare Microsoft Store submission: PWA assets, docs, and audit"

# push (初回は -u で upstream 紐付け)
git push -u origin main
```

> 備考: 既存リポジトリに既にコンテンツがある場合 (README / LICENSE / .gitignore を GitHub 側で追加済など) は、`git pull --allow-unrelated-histories` でマージしてから push する。コンフリクトが出たら手動で解消。空リポなら pull 不要で直接 push 可能。

### C-4. Cloudflare Pages で本番デプロイ (所要 10 分)

1. https://dash.cloudflare.com/ → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
2. GitHub 連携を許可し `flyingevaporator-cmyk/reaction-heat-calculator` を選択
3. ビルド設定:

   | 項目 | 値 |
   |---|---|
   | Project name | `reaction-heat-calculator` |
   | Production branch | `main` |
   | Framework preset | **None** |
   | Build command | `bash build.sh` |
   | Build output directory | `dist` |
   | Root directory | (空) |

4. **Save and Deploy** → 1-2 分で本番 URL 発行 (予想: `https://reaction-heat-calculator.pages.dev`)

### C-5. 本番 URL で PWABuilder 検証 (所要 5 分)

1. https://www.pwabuilder.com/ を開く
2. 本番 URL を入力して **Start**
3. スコア 90+ を確認 (ローカル監査では 33/33 PASS なので本番も問題ないはず)
4. 低スコア項目があれば対応後に再デプロイ

補足: ローカルでの事前確認は以下で再実行可能:

```bash
cd C:\Users\ko\claude\calc
python scripts/pwa_audit.py --serve --port 8000
```

### C-6. Microsoft Partner Center 個人登録 (所要 30-60 分、書類待ちがあれば数日)

1. https://partner.microsoft.com/dashboard にアクセス
2. Microsoft アカウントでサインイン
3. **Microsoft Store と Xbox 開発者** プログラム
4. **Individual** を選択 (年会費 $19)
5. Publisher Display Name: `Evaporator Labs`
6. 本人確認 (電話 SMS + 住所確認)
7. **税務フォーム**: W-8BEN (米国外個人) を電子署名で提出。日本在住なら日米租税条約で ロイヤリティ 0% 指定可。

### C-7. アプリ名予約 (所要 5 分)

Partner Center → **Overview** → **Create a new app**

#### アプリ名候補 (優先順位つき 3 つ)

| 順位 | 名称 | 特徴 |
|---|---|---|
| 第 1 候補 | `Reaction Heat Calculator` | STORE_LISTING.md 既定。覚えやすく SEO 的に強い。 |
| 第 2 候補 | `Reaction Heat Energy Calculator` | `manifest.json` の `name` と一致。冗長だが一意性が高い。 |
| 第 3 候補 | `Evaporator Labs Reaction Heat` | 屋号プレフィックスを付けることで衝突回避。将来複数アプリを出すときにシリーズ化しやすい。 |

事前に https://apps.microsoft.com/ で検索して重複がないか確認 → 予約 → 3 日以内にサブミット着手が必要。

### C-8. PWABuilder で MSIX 生成 (所要 10 分)

1. https://www.pwabuilder.com/ に本番 URL を入れ、スコア確認後 **Package for Stores** → **Windows**
2. 入力値:

   | 項目 | 値 |
   |---|---|
   | Package ID | Partner Center 予約後に表示される ID (例: `1234EvaporatorLabs.ReactionHeatCalculator`) |
   | Publisher display name | `Evaporator Labs` |
   | Publisher ID | Partner Center > Account settings > Identity > Publisher ID |
   | App name | `Reaction Heat Calculator` |
   | App version (Modern) | `1.0.1.0` |
   | App version (Classic) | `1.0.0.0` |
   | URL | 本番 URL (Cloudflare Pages) |

3. **Generate Package** → 次の 2 ファイルをダウンロード:
   - `*.msixbundle` (Modern PWA, WebView2)
   - `*.classic.appxbundle` (Hosted Web App, 広い互換)

### C-9. Partner Center にパッケージアップロード (所要 15 分)

1. Partner Center → 予約済アプリ → **Start your submission**
2. **Packages** セクションに `.msixbundle` と `.classic.appxbundle` を両方アップロード
3. Device families: Windows 10 Desktop (1809+) を有効化、Xbox は外す

### C-10. Store リスティング入力 (所要 30 分)

`STORE_LISTING.md` (改善済みなら `STORE_LISTING.review.md` 反映後) から以下をコピペ:

- Short description (EN / JA) — §2
- Long description (EN / JA) — §3
- What's new in this version (EN / JA) — §4
- Search keywords — §5
- Features list — §6
- System requirements — §7
- IARC 質問票 — §8 の回答表に従う

プライバシー欄:

- Privacy policy URL: `https://reaction-heat-calculator.pages.dev/privacy/` (独自ドメイン使うなら差し替え)
- Support email: `flying.rotavap@gmail.com`

Pricing:

- 価格: **$0.99 (USD)** をローンチ時点の base price として設定 (`PRICING_DECISION.md` §1 のオーナー決定に従う)
- Markets: All markets (審査中に国別絞り込みの検討は後でも可)

> 14 日後に `$4.99` へ切り替える (C-13 参照)

### C-11. Submit for certification (所要 1 分、審査待ち 24-72 時間)

**Submit for certification** をクリック → Partner Center に審査進捗が出る。
審査通過 (承認) のメール通知が届いたら、その日を **公開日** として記録 (C-13 で使う)。

### C-12. 審査通過後の告知 (所要 30-60 分、公開当日〜翌週)

1. Store ページの共有 URL を取得 (`ms-windows-store://pdp/?ProductId=...`)
2. `STORE_LISTING.md` §11 の X / Reddit / Discord 告知原稿を、`STORE_LISTING.review.md` §9 の修正版 (ローンチ $0.99 価格を反映済) に差し替えて投稿
3. Reddit は以下の順序で 1 日 1 コミュニティ程度のペースで投稿 (spam 認定を避けるため同日複数投稿を避ける):
   - 1 日目: `r/chemistry` (ツール紹介 OK の大型サブレディット)
   - 3 日目: `r/chemhelp` (学生向け、宿題補助文脈で投稿)
   - 7 日目: `r/Chempros` (プロセスエンジニア層、熱収支の文脈で投稿)
4. `PRICING_STRATEGY.md` §5 の KPI を Partner Center > Analytics で追跡開始

### C-13. 公開 14 日後: 価格を $4.99 に引き上げ (所要 5 分)

**公開日カレンダーにリマインダを設定** しておくこと。

1. Partner Center → アプリ → **Pricing and availability**
2. Base price を `USD $0.99` → `USD $4.99` に変更
3. **Save** → 即日反映 (審査不要)
4. Reddit / X で「ローンチ特価終了、通常価格になりました」の軽いフォロー投稿 (任意)

目標: この時点でレビュー **10 本以上、★ 平均 4.0 以上**。未達なら $0.99 期間を 1 週間延長する判断もあり。

### C-14. GitHub パラメータリポジトリ公開 (所要 30 分、C-11 と並行可)

`PRICING_DECISION.md` §5 に従い、化学パラメータのみを別リポジトリで CC0 公開する。Store 本体の OSS 化ではなく、コミュニティ信頼構築の専用チャネル。

1. https://github.com/new を開く
2. リポジトリ名: **`flyingevaporator-cmyk/chemistry-thermo-params`** を推奨 (本体リポと同じ `flyingevaporator-cmyk` ユーザー配下で統一)。将来 `evaporator-labs` 組織を作る場合は transfer 可能。
3. 可視性: **Public**
4. License: **CC0 1.0 Universal** (GitHub の license テンプレートから選択)
5. 含める内容:
   - `bond-dissociation-energies.json` — `index.html` 内から抽出した結合解離エネルギー値
   - `benson-groups.json` — Benson 群加算パラメータ
   - `README.md` — 引用出典 (Cottrell 1958, CRC Handbook, NIST 互換セット)、Reaction Heat Calculator Store ページへの逆リンク、利用例
   - `CITATION.bib` — BibTeX 形式の引用情報
6. 公開後、Reddit 投稿 (C-12) および `privacy/index.html` の末尾にリポジトリへの参照を追加
7. Store 本体の OSS 化 (フルコード) は 1 年後に再検討 — それまで主要な告知チャネルとしてこのリポを育てる

### C-15. Google Play デベロッパ登録 (所要 30 分 + 本人確認待ち 1-2 週間、C-11 と並行可)

Microsoft Store 審査中に並行着手することで、全体スケジュールを短縮できる。

1. https://play.google.com/console/signup にアクセス
2. Google アカウントでサインイン (Evaporator Labs 用の Gmail 分離を推奨)
3. アカウント種別: **個人 (Individual)** を選択 (登録料 **$25 / 一度きり**)
4. Publisher name: `Evaporator Labs`
5. **本人確認書類**:
   - 政府発行 ID (運転免許証 / マイナンバーカード / パスポート)
   - 現住所の証明書類 (公共料金領収書など、3 ヶ月以内のもの)
   - 2024 年以降は個人アカウントの人手レビューが入るため **1-2 週間の待ち時間** を見込む
6. 税務フォーム (米国 W-8BEN) を提出 — Microsoft と同じ書類で可
7. 支払いプロファイル登録 (Google Payments Merchant アカウント自動開設)

### C-16. Android 用素材準備 (所要 2-3 時間、C-15 の承認待ち中に並行着手)

以下の素材を事前に用意しておくと提出がスムーズ。

1. **`.well-known/assetlinks.json`** (Digital Asset Links 認証ファイル)

   Cloudflare Pages で `https://<your-domain>/.well-known/assetlinks.json` として公開する。中身は C-17 の Bubblewrap 実行時に生成されるが、**先に空ディレクトリと `build.sh` への追記だけ**済ませておく:

   ```bash
   # build.sh の「Static directories」セクションに追加
   mkdir -p "$OUT/.well-known"
   [ -f .well-known/assetlinks.json ] && cp .well-known/assetlinks.json "$OUT/.well-known/" || true
   ```

2. **80 字短文原稿 (EN / JA)**: `STORE_LISTING.review.md` §12 に収録された案を使用
3. **4000 字長文原稿 (EN / JA)**: Microsoft 版から削除する箇所は `STORE_LISTING.review.md` §12 参照
4. **Feature Graphic 1024×500 PNG**: `STORE_LISTING.review.md` §12 の推奨コピーをデザインに起こす
5. **Android 用スクリーンショット**:
   - Phone 用: 1080×1920 縦向き 最低 2 枚 (既存 720×1280 を撮り直すのが望ましい)
   - Tablet 用 (任意): 1200×1920 縦向き 1 枚以上
   - `scripts/take_screenshots.py` にサイズ引数を追加して再撮影する案を推奨
6. **アプリアイコン 512×512 PNG**: `icons/icon_620x620.png` をリサイズして `icons/icon_512x512.png` として追加
7. **Data Safety フォーム回答**: `STORE_LISTING.review.md` §12 に全項目の回答例あり

### C-17. Bubblewrap で .aab 生成 → Google Play 提出 (所要 2-3 時間、Microsoft Store 公開後に実施)

Microsoft Store が公開され、本番 URL の安定動作が確認できた後に Android パッケージを生成する。

```bash
# Bubblewrap CLI のインストール (要 Node.js 18+ と Java 17+)
npm install -g @bubblewrap/cli

# プロジェクト初期化 (本番 manifest を指す)
cd C:\Users\ko\claude\calc
bubblewrap init --manifest https://<your-domain>/manifest.json

# Java SDK / Android SDK を聞かれたら手順に従ってインストール (初回のみ)
# パッケージ名例: com.evaporatorlabs.reactionheatcalculator

# ビルド (.aab 生成)
bubblewrap build

# 生成物:
# - app-release-bundle.aab (これをアップロード)
# - assetlinks.json (→ Cloudflare Pages に配置、C-16 のファイルと差し替え)
```

代替案: **PWABuilder** (https://www.pwabuilder.com/) の Android 出力でも同等の `.aab` が得られる。ローカルに SDK を入れたくない場合はこちら推奨。

提出フロー:

1. https://play.google.com/console を開く
2. **アプリを作成** → アプリ名 / デフォルト言語 / 無料 or 有料を選択 (ここで **有料** を選ぶ)
3. **アプリのセットアップ** セクションで以下を全て完了:
   - プライバシーポリシー URL: `https://<your-domain>/privacy/`
   - アプリへのアクセス: 制限なし
   - 広告: 含まない
   - コンテンツの規制レベル: IARC 質問票 (Microsoft と同じ回答)
   - ターゲット ユーザー層と子供向け設定: 13 歳以上
   - **Data Safety**: `STORE_LISTING.review.md` §12 の回答表に従う
4. **リリース** → 本番トラック → `.aab` をアップロード
5. ストアリスティング入力:
   - 短い説明 (80 字) / 詳細な説明 (4000 字)
   - スクリーンショット / Feature Graphic / アプリアイコン
6. **価格** を `USD 0.99` に設定 (ローンチ価格、C-18 で $4.99 に切替)
7. 対象国: 全世界 (または必要に応じて絞り込み)
8. **審査に送信** → 通常 3-7 日で結果。個人アカウント初回は 7 日超も珍しくない

> 注意: `.well-known/assetlinks.json` は **承認済みの正しい値**で本番ホストに配置されていないと、ストア公開後に「アドレスバーが消えず通常のブラウザ画面として表示される」不具合になる。提出前に `https://developers.google.com/digital-asset-links/tools/generator` で検証可能。

### C-18. Google Play 公開 14 日後: 価格を $4.99 に引き上げ (所要 5 分、Microsoft と独立)

Microsoft Store の値上げ (C-13) と **独立してカウント**する。つまり Google Play の公開日から 14 日を数える。

1. Google Play Console → アプリ → **収益化** → **製品** → **価格**
2. Base price を `USD $0.99` → `USD $4.99` に変更
3. **保存** → 即日反映 (審査不要)

Microsoft と Google の公開日がずれる前提なので、それぞれのカレンダーリマインダを別々に設定すること。目標 KPI は Microsoft と同じで **レビュー 10 本以上、★ 平均 4.0 以上**。Google Play の DL 規模は Microsoft より 10 倍以上期待できるが、レビュー率は 1-2% なので、10 本確保は $0.99 期間中の DL 500-1000 本がラインになる。

---

## D. 重要な URL / コマンド早見表

### URL

Microsoft Store 系:

| 用途 | URL |
|---|---|
| Partner Center | https://partner.microsoft.com/dashboard |
| Partner Center アカウント登録 | https://partner.microsoft.com/en-us/dashboard/registration/partner/selectaccounttype |
| Microsoft Store 検索 (重複確認) | https://apps.microsoft.com/ |
| PWABuilder | https://www.pwabuilder.com/ |
| PWABuilder スコアカード | https://www.pwabuilder.com/reportcard |

Google Play 系:

| 用途 | URL |
|---|---|
| Google Play Console | https://play.google.com/console |
| Google Play Console 登録 | https://play.google.com/console/signup |
| Google Play ストア (重複確認) | https://play.google.com/store/apps |
| Bubblewrap CLI (GitHub) | https://github.com/GoogleChromeLabs/bubblewrap |
| Digital Asset Links 検証ツール | https://developers.google.com/digital-asset-links/tools/generator |
| Data Safety フォーム ガイド | https://support.google.com/googleplay/android-developer/answer/10787469 |

共通インフラ / リポジトリ:

| 用途 | URL |
|---|---|
| Cloudflare Dashboard | https://dash.cloudflare.com/ |
| 本プロジェクト GitHub リポ | https://github.com/flyingevaporator-cmyk/reaction-heat-calculator |
| GitHub 新規リポジトリ (パラメータ用) | https://github.com/new |

### コマンド (コピペ用)

```bash
# ローカル PWA 監査 (ローカル検証用)
cd C:\Users\ko\claude\calc
python scripts/pwa_audit.py --serve --port 8000

# dist/ 再ビルド
bash build.sh

# Git コミット & push (C-2, C-3 の後)
git status
git add .
git commit -m "Prepare Microsoft Store submission"
git push origin main

# キャッシュバージョン更新 (リリース時)
# service-worker.js の CACHE_VERSION を rxn-heat-v1 -> rxn-heat-v2 に変更

# Google Play 用 Android パッケージ生成 (C-17)
npm install -g @bubblewrap/cli
bubblewrap init --manifest https://<your-domain>/manifest.json
bubblewrap build
# 生成物: app-release-bundle.aab (Play Console にアップロード) と assetlinks.json (Cloudflare Pages に配置)
```

### 参考ドキュメント (本リポジトリ内)

- `DEPLOY.md` — Cloudflare Pages 接続手順
- `STORE_SUBMISSION.md` — Partner Center + MSIX 詳細手順
- `STORE_LISTING.md` — Store 原稿一式
- `STORE_LISTING.review.md` — 改善提案 (本セッション成果物)
- `PRICING_STRATEGY.md` — 価格戦略分析
- `PRICING_DECISION.md` — 価格決定案 (本セッション成果物)
- `PWA_AUDIT.md` — ローカル監査レポート (本セッション成果物)
- `scripts/pwa_audit.py` — 再実行可能な監査スクリプト (本セッション成果物)

---

## E. 注意事項 / リスク

1. **`frontend/` `pfd-generator/` `ts_calculator/` `backend/` は Store 公開の対象外** (`CLAUDE.md` 参照)。これらの削除や変更は Store 提出と分けてコミットすることを推奨。
2. **ブランチ名**: 現在ローカルは `master`。既存リポ `flyingevaporator-cmyk/reaction-heat-calculator` の既定ブランチが `main` である想定で、C-2 で `git branch -m main` リネーム後に push する。GitHub 側が `master` のままなら Settings → Branches でデフォルト変更するか、どちらかに統一する。
3. **プライバシーポリシー URL** は本番ドメイン確定後、Partner Center と `privacy/index.html` 内リンクで統一すること。
4. **Service Worker のキャッシュバージョン**: コード修正ごとに `service-worker.js` の `CACHE_VERSION` をインクリメントする (現在 `rxn-heat-v1`)。インクリメント忘れるとユーザー側でキャッシュが更新されない。
5. **MSIX 生成後の Package ID / Publisher ID**: Partner Center で予約完了後でないと取得できないので、MSIX 生成 (C-8) は C-7 の後で。
6. **GitHub 既存リポとのマージ衝突**: `flyingevaporator-cmyk/reaction-heat-calculator` に既に README / LICENSE / .gitignore が置かれている場合、初回 push 前に `git pull --allow-unrelated-histories origin main` でマージが必要。GitHub 側 README を残したい場合はローカル `README.md` がないことを確認、あるいは両者を手動で統合してからコミット。

---

## F. 今回のセッションの監査結果 (抜粋)

### PWA 監査 (PWA_AUDIT.md)

- 合計 33 チェック / 33 PASS
- manifest 必須 7 フィールドすべて充足
- 192/512 相当のアイコンは SVG `sizes="any"` で担保
- maskable アイコン、screenshots 4 件、scope 設定すべて OK
- ローカル HTTP 経由で全リソース 200 取得

### Store リスティング指摘 (STORE_LISTING.review.md 抜粋)

- `thermodynamics` が Long description 本文に不在 → 挿入推奨
- `"Perfect for"` / `"Instantly"` / `"100%"` / `"Zero"` をやや中立化
- 同義語 `"heat of reaction"` / `"enthalpy change"` / `"エンタルピー変化"` を併記して SEO カバレッジ拡張
- 医療・禁止・最上級表現は未検出

### 価格決定 (PRICING_DECISION.md 要約、2026-04-22 オーナー確定)

1. ローンチ 14 日間は **$0.99 のイントロ価格**、15 日目以降は **$4.99 買い切り** に切替
2. v1.x の追加機能 (履歴 → PDF → テンプレ → ダーク → バッチ → パラメータ) は買い切り後の **無償アップデート** として提供 (Free/Pro 分割はしない)
3. 広告 **導入しない**
4. 化学パラメータ (Benson 群係数、結合解離エネルギー表) は **初期から CC0 で GitHub 公開**、アプリ本体のフル OSS 化は 1 年後に再検討
5. 告知チャネル: Reddit r/chemistry / r/chemhelp / r/Chempros + パラメータ GitHub リポの SEO 資産

### マルチストア展開 (C-15〜C-18 追加)

- Microsoft Store 公開後、同一 PWA を **TWA (Trusted Web Activity)** ラップで Google Play にも提出する
- 公開日は Microsoft と Google で別々 → 値上げ (`$0.99 → $4.99`) の 14 日カウントも **それぞれ独立** で管理する
- Google Play は個人アカウント本人確認が 1-2 週間かかるため、C-15 登録は Microsoft 審査中 (C-11) と並行着手することを推奨
- Android 専用素材 (80 字短文 / 4,000 字長文 / Feature Graphic 1024×500 / Phone 1080×1920 スクリーンショット / Data Safety 回答) は `STORE_LISTING.review.md` §12 に集約
- パッケージ名は `com.evaporatorlabs.reactionheatcalculator` を推奨 (一度公開すると変更不可)

---

以上。C-1 から順に実施することで Microsoft Store / Google Play の両方の公開を完了できます。特に次の期日はそれぞれ別カレンダーリマインダを必ず入れてください:

- **Microsoft**: C-11 公開承認 → C-13 の 14 日後値上げ
- **Google Play**: C-17 公開承認 → C-18 の 14 日後値上げ (Microsoft と独立カウント)
