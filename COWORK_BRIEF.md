# Cowork 引き継ぎ指示書 (Master Brief)

Evaporator Labs / Reaction Heat Energy Calculator — Microsoft Store 公開プロジェクト

このファイル 1 つを読めば、別セッション (Claude Cowork / 別の Claude インスタンス) が続きを自動で進められる自己完結ブリーフです。

---

## 0. この依頼の目的

反応熱計算 PWA (`index.html`) を **Microsoft Store で $4.99 / 無料フェーズ F モデル**で公開する。
現在 Step 1〜4 完了済み。残り Step 5 (Partner Center + MSIX) と Step 6 (提出) を進めたい。

**Cowork に期待する範囲**: 人間の介入が不要な全タスクを自動実行・準備する。
人間 (= オーナー flying.rotavap@gmail.com) のアクションが必要な箇所は、**そのまま貼り付けて実行できる形の指示書**を出力する。

---

## 1. プロジェクト基本情報

| 項目 | 値 |
|---|---|
| ブランド | Evaporator Labs |
| 連絡先 | flying.rotavap@gmail.com |
| ホスティング | Cloudflare Pages (予定) |
| 想定本番 URL | 未定 (`https://reaction-heat-calculator.pages.dev` を第一候補として仮置き) |
| アプリ名 (EN) | Reaction Heat Calculator |
| アプリ名 (JA) | 反応熱計算機 |
| 作業ルート | `C:\Users\ko\claude\calc` |
| バージョン | 1.0.0 (Classic 1.0.0.0 / Modern 1.0.1.0) |

---

## 2. 現在の状態 (Done / Todo)

### Done (Cowork が前提にしてよい)

- [x] `index.html` (ルート) — Clean & Professional 配色にリスタイル済み、PWA メタタグ・SW 登録済み
- [x] `manifest.json` — 完全記述済み (icons 11 種、screenshots 4 枚、shortcuts、edge_side_panel)
- [x] `service-worker.js` — `rxn-heat-v1`、shell cache-first + Google Fonts SWR
- [x] `privacy/index.html` — JA/EN バイリンガル プライバシーポリシー
- [x] `build.sh` — `dist/` を生成する Cloudflare Pages ビルドスクリプト
- [x] `_headers`, `_redirects` — セキュリティヘッダ & リダイレクト
- [x] `.gitignore` — ルート `index.html` のトラッキング解除済み
- [x] `icons/screenshot-desktop-{1,2,3}.png` + `screenshot-mobile-1.png` — Playwright で生成済み
- [x] `DEPLOY.md`, `STORE_SUBMISSION.md`, `STORE_LISTING.md`, `PRICING_STRATEGY.md` — ドキュメント完備
- [x] `scripts/take_screenshots.py` — 再生成用スクリプト

### Todo (Cowork で進めてほしい)

1. **Cloudflare Pages デプロイ前検証**
   - `build.sh` をローカル実行 → `dist/` の内容チェック (index.html, manifest.json, service-worker.js, icons/, privacy/, _headers, _redirects, robots.txt, sitemap.xml が揃っているか)
   - `dist/` に開発用ファイル (frontend/, backend/, ts_calculator/, pfd-generator/, .claude/, node_modules/) が混入していないか
   - ファイルサイズサマリをレポート (特に index.html の 3.5MB が想定内か)

2. **git 状態確認と push 準備**
   - `git status` でコミット漏れ確認
   - 追跡対象に機密情報 (API キー、.env、個人情報) が混入していないか grep (`AIza`, `sk-`, `password`, `PRIVATE KEY`)
   - push コマンド 1 行 (例: `git push origin main`) をレポートに記載するが、**実際の push は実行しない** (人間承認事項)

3. **Store リスティング磨き込み**
   - `STORE_LISTING.md` の EN/JA ロングディスクリプションを読み、以下の観点で改善版を出力
     - Microsoft Store の SEO に効くキーワード密度 (chemistry, thermodynamics, enthalpy)
     - 禁止表現 (「medical」「drug」等、審査で引っかかりやすい語) の確認
     - Apple App Store 的な過剰マーケ語 (「best」「#1」) の削除
   - 改善案は `STORE_LISTING.md` を **直接書き換えず**、`STORE_LISTING.review.md` に diff 形式で提示

4. **価格決定レポート**
   - `PRICING_STRATEGY.md` §7 の未決事項 5 項目について、Cowork の推奨を明記した `PRICING_DECISION.md` を作成
     - 推奨前提: 個人開発、初年度 DL 3,000 想定、学生市場、競合不在
     - 出力フォーマット: 各項目につき (a) 推奨値, (b) 理由 3 行以内, (c) 代替案との差分

5. **PWABuilder スコアチェック準備**
   - 本番 URL がまだ無い前提なので、**ローカル preview server を立てて** (`python -m http.server 8000` in repo root) `http://localhost:8000/` を対象に
     - `manifest.json` の妥当性 (required fields: name, short_name, start_url, display, icons 192+512 相当, background_color, theme_color)
     - `service-worker.js` の scope 設定と fetch イベントハンドラ存在確認
     - これらを満たしているかチェックするスクリプト `scripts/pwa_audit.py` を作成・実行
   - 結果を `PWA_AUDIT.md` にレポート

6. **最終サマリ出力**
   - `HANDOFF_STATUS.md` に以下を含める
     - 完了した Cowork 作業一覧
     - 人間のアクションが必要なタスク (順序付き TODO)
     - 各タスクで使うリンク・コマンド・貼り付け文言 (Partner Center URL、PWABuilder URL、MSIX upload 手順、予約すべきアプリ名候補 3 つ)

---

## 3. 絶対に守る制約 (CLAUDE.md 由来)

- **日本語で応答する** (コードコメント含む)
- **絵文字をファイルに書かない** (会話でもなるべく使わない)
- **git commit は明示依頼されるまで行わない**
- **git push も人間承認事項** (Cowork は push しない)
- ユーザー判断が必要なら AskUserQuestion を使う

## 4. 絶対に触らないファイル

- `frontend/`, `backend/`, `ts_calculator/`, `pfd-generator/` — 本 Store 公開の対象外 (ルート `index.html` が対象)
- `bom-cost.html` — 生成物、`.gitignore` で除外済み
- `.claude/worktrees/` 配下 — worktree なので編集しない

## 5. Cowork が参照すべきファイル (絶対パス)

- プロジェクトルート: `C:\Users\ko\claude\calc`
- 主要ドキュメント:
  - `C:\Users\ko\claude\calc\DEPLOY.md`
  - `C:\Users\ko\claude\calc\STORE_SUBMISSION.md`
  - `C:\Users\ko\claude\calc\STORE_LISTING.md`
  - `C:\Users\ko\claude\calc\PRICING_STRATEGY.md`
- 公開対象: `C:\Users\ko\claude\calc\index.html` (3.5MB, 自己完結 PWA)
- PWA 三点セット: `manifest.json`, `service-worker.js`, `privacy/index.html`
- ビルド: `build.sh`, `_headers`, `_redirects`

## 6. 人間 (オーナー) のアクションが必要なタスク

Cowork はこれらを **実行しない**。代わりに実行手順を `HANDOFF_STATUS.md` に書く。

1. [ ] Microsoft Partner Center 個人登録 ($19) + 本人確認 + W-8BEN
2. [ ] GitHub リポジトリ作成 (`reaction-heat-calculator` 推奨) → `git push`
3. [ ] Cloudflare Pages で上記リポジトリを接続 (Build: `bash build.sh`, Output: `dist`)
4. [ ] 本番 URL 確認後、Partner Center でアプリ名予約
5. [ ] PWABuilder (https://www.pwabuilder.com/) に本番 URL を入力し MSIX 生成
6. [ ] Partner Center に `.msixbundle` / `.classic.appxbundle` をアップロード
7. [ ] Store リスティング入力 (`STORE_LISTING.md` からコピペ)
8. [ ] Submit for certification

## 7. Cowork の出力形式

最終的に以下 5 ファイルを生成 (or 更新) すること:

1. `STORE_LISTING.review.md` — 改善提案 (diff 形式)
2. `PRICING_DECISION.md` — 価格 5 項目の決定案
3. `PWA_AUDIT.md` — ローカル PWA 監査結果
4. `scripts/pwa_audit.py` — 再実行可能な監査スクリプト
5. `HANDOFF_STATUS.md` — オーナー向け最終 TODO リスト (人間アクション手順)

既存ファイルを **書き換える場合は必ず `.review.md` / `.decision.md` 等の別ファイル**にする。既存ドキュメントは原本として保持。

---

## 8. 起動プロンプト (コピペ用)

Cowork セッションを開く際、以下をそのまま貼り付ければ開始できる:

```
C:\Users\ko\claude\calc\COWORK_BRIEF.md を読んで、§2 "Todo" の 6 項目を順に実行してください。
§3 の制約 (日本語、絵文字禁止、git commit/push しない) を厳守。
§7 の 5 ファイルを最終成果物として出力してください。
各ステップ完了時に短いサマリを日本語で報告してください。
```

---

以上。このブリーフと指定ファイル群だけで続きを進められます。
