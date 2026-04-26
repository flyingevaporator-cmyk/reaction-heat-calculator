# Microsoft Store 提出ガイド

Evaporator Labs / Reaction Heat Energy Calculator

このドキュメントは Step 5 (Partner Center 登録 + MSIX 生成) と Step 6 (提出) の手順書です。

---

## Step 5-A: Microsoft Partner Center 登録

1. [partner.microsoft.com](https://partner.microsoft.com/dashboard) にアクセス
2. 既存の Microsoft アカウント (Hotmail / Outlook / ビジネス MS アカウント) でサインイン
3. **Microsoft Store と Xbox 開発者** のプログラムを選択
4. アカウント種別を選択:

   | 種別 | 年会費 | 必要書類 | 推奨 |
   |---|---|---|---|
   | **個人 (Individual)** | 約 $19 (一度きり) | 氏名、住所、銀行口座 | 収益化初期はこれで OK |
   | **会社 (Company)** | 約 $99 (一度きり) | DUNS 番号、法人登記、役員承認 | 法人化済みならこちら |

   本プロジェクトは屋号 "Evaporator Labs" での個人登録で進めます。

5. 本人確認:
   - 住所確認 (1〜3 営業日以内にハガキが届く場合あり — 届かない国も多い)
   - 電話認証 (SMS or 音声通話)

6. **Publisher Display Name** に `Evaporator Labs` を入力
   - ここで設定した文字列が Store 画面に表示されます
   - 後から変更は可能だがレビュー要

7. 税金・支払い情報:
   - W-8BEN (米国外個人) を提出 (電子サインで完結)
   - 銀行口座情報 (SWIFT 必要)

## Step 5-B: アプリ本番デプロイ

MSIX 生成の前に、**公開 URL が必要**です (PWABuilder がアクセスしに行くため)。

[DEPLOY.md](DEPLOY.md) の手順で Cloudflare Pages にデプロイし、本番 URL (例: `https://reaction-heat-calculator.pages.dev`) を取得してください。

### デプロイ後チェック (PWABuilder 合格条件)

本番 URL に対して以下が満たされていることを確認:

```bash
# ブラウザで本番 URL を開き DevTools > Application タブで確認
# 1. Manifest が読み込まれている
# 2. Service Worker が activated
# 3. HTTPS で配信されている (Cloudflare は自動で HTTPS)
```

または [https://www.pwabuilder.com/reportcard](https://www.pwabuilder.com/reportcard) に URL を入力してスコア確認。

**満たすべき必須項目**:
- [x] HTTPS 配信
- [x] 有効な Web App Manifest
- [x] Service Worker が登録されている
- [x] Icons (192, 512 相当以上) が存在 *1
- [x] start_url, name, short_name, display が manifest に存在

*1 既存の 256 / 300 / 620 で代替可能。PWABuilder は warning を出すが Store 通る。

## Step 5-C: アプリ名の確保 (Reserve App Name)

1. Partner Center → **Overview** → **Create a new app**
2. アプリ名を入力:
   - 第一候補: `Reaction Heat Calculator`
   - 第二候補: `Reaction Heat Energy Calculator`
   - 既に使われていない名前を 3 日以内に使い始める必要あり
3. **Reserve product name** をクリック

## Step 5-D: PWABuilder で MSIX 生成

1. [pwabuilder.com](https://www.pwabuilder.com/) にアクセス
2. 本番 URL を入力 → **Start**
3. スコア確認 (90+ 推奨)
4. **Package for Stores** → **Windows** を選択
5. 以下のパラメータを入力:

   | 項目 | 値 |
   |---|---|
   | Package ID | (Partner Center でアプリ予約後に表示される ID、例: `1234EvaporatorLabs.ReactionHeatCalculator`) |
   | Publisher display name | `Evaporator Labs` |
   | Publisher ID | (Partner Center の **Account settings > Identity > Publisher ID**) |
   | App name | `Reaction Heat Calculator` |
   | App version | `1.0.1.0` |
   | App version (classic) | `1.0.0.0` |
   | URL | `https://<your-domain>` |

6. **Generate Package** をクリック → `.msixbundle` と `.appxbundle` と `.classic.appxbundle` をダウンロード

> PWABuilder は 2 種類のパッケージを生成:
> - **Modern PWA** (.msixbundle) — WebView2 ベース、Windows 10 1809+
> - **Classic PWA** (.classic.appxbundle) — Hosted Web App、Windows 10 対応を広く

## Step 5-E: Partner Center にパッケージをアップロード

1. Partner Center → 予約したアプリ → **Start your submission**
2. **Packages** セクション:
   - ダウンロードした `.msixbundle` と `.classic.appxbundle` を両方アップロード
   - PWABuilder が自動生成した各種アイコンサイズを含む
3. **Device families** で対応 OS を確認:
   - Windows 10 Desktop (1809+) 以降
   - Xbox はチェック不要

---

## Step 6-A: Store リスティング情報

次の情報を入力します (JA / EN 両方推奨):

### 基本情報

- **Short description** (200 文字以内)
- **Long description** (10,000 文字以内)
- **What's new in this version** (1,500 文字以内)

### メディア

- **Screenshots**: `icons/screenshot-desktop-*.png` をアップロード (最低 1、推奨 4+)
- **Store logos** (任意だが推奨):
  - 300×300: `icons/icon_300x300.png`
  - 150×150: `icons/icon_150x150.png`
- **Trailer video** (任意)

### 分類

- **Category**: Education (メイン) / Productivity (サブ)
- **Age rating**: IARC 質問票に回答 → "3+" (低年齢向け、問題コンテンツなし) を想定
- **Copyright**: `© 2026 Evaporator Labs`

### プライバシー

- **Privacy policy URL**: `https://<your-domain>/privacy/`
- **Support contact info**: `flying.rotavap@gmail.com`

### 価格・流通

- **Markets**: All markets (または JP+US+EU 等を選択)
- **Pricing**: 選択肢は Step 6-B 参照

## Step 6-B: 価格モデル検討

| モデル | 価格目安 | 特徴 | 推奨度 |
|---|---|---|---|
| 無料 | Free | インストール数最大化、将来の IAP 追加余地 | MVP 向け |
| 買い切り | $2.99 / $4.99 | シンプル、即収益、返金リスク小 | 機能完成品向け |
| フリーミアム | Free + IAP | 無料で試させ、Pro 課金 | 差別化機能が明確な場合 |
| サブスク | $1.99/月 | LTV 最大、継続的収益 | サーバー処理を提供する場合 |

### 初期推奨

**フリーミアム構成**:
- Free 版: 無制限計算 (結合エネルギー法のみ)
- **Pro ($4.99 買い切り)**: Benson group additivity、ΔG / ΔS 計算、計算履歴保存、CSV エクスポート

現状アプリは Benson 法も無料で提供されているため、Free 版の機能制限を入れるか、全機能無料で配布して広告モデルに切り替えるかの判断が必要です。

## Step 6-C: 提出 & 審査

1. すべて入力完了したら **Submit for certification**
2. 審査期間: 通常 24〜72 時間
3. **認証落ち**の場合は理由が通知される — 修正して再提出

### よくある落選理由

- Privacy policy URL がアクセスできない (404)
- Age rating が不適切 (IARC 質問に「化学物質」「爆発」などで YES するとレート上がる)
- Screenshot の解像度不足
- App 機能とタイトル / 説明の乖離

---

## 完了後

1. Store ページの **共有用リンク**を取得 (`ms-windows-store://pdp/?ProductId=...`)
2. Twitter / Reddit / Chemistry コミュニティで告知
3. 販売ダッシュボードで DL 数・売上を確認 (Partner Center > Analytics)

---

## 付録: 納税書類 (日本在住者向け)

- W-8BEN: 米国源泉徴収免除申請 (電子署名で完結)
- 日米租税条約により、ロイヤリティ等は 0% 源泉徴収可能
- 年間売上の記録は確定申告で雑所得 or 事業所得として計上
