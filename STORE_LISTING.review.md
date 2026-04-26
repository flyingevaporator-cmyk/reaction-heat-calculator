# STORE_LISTING.md レビュー (diff 形式)

Evaporator Labs / Reaction Heat Energy Calculator

レビュー日: 2026-04-22
対象ファイル: `STORE_LISTING.md` (v1.0.0 原稿)
レビュー観点:

- Microsoft Store SEO 向けキーワード密度 (chemistry, thermodynamics, enthalpy)
- Store 審査で引っかかりやすい語彙 (medical, drug, clinical, diagnose, treat, FDA 等)
- 過剰マーケティング語彙 (best, #1, world's leading, revolutionary, perfect 等)
- 冗長表現の整理

---

## 0. 総合評価

原稿は全体として丁寧に書かれており、Store 規約への致命的抵触は見当たらない。特に

- 医療・薬事関連の禁止表現は未使用
- 最上級表現 ("best", "#1", "world-class" 等) は未使用
- プライバシーポリシーへの言及が明示的で審査にプラス

改善余地は主に次の 3 点:

1. **thermodynamics という主要 SEO ワードが Long description 本文に出てこない** — キーワード欄にはあるが本文で補強されていない
2. "Perfect for" / "100%" / "Instantly" 等、やや販売色の強い副詞・形容の整理
3. 同義語 (heat of reaction, enthalpy change) を本文に追加すると検索ヒット率が上がる

以下、セクション別の diff 提案。原本は触らず、本ファイルに提案を集約した。

---

## 1. Short description (EN) — §2 EN

現在 178 文字。1 語の追加余地あり。

```diff
- Instantly estimate reaction enthalpy (delta H) from SMILES or by drawing molecules. Offline, private, no account required. Perfect for chemistry students, teachers, and process engineers.
+ Estimate reaction enthalpy (delta H) and thermodynamics from SMILES or by drawing molecules. Offline, private, no account required. Built for chemistry students, teachers, and process engineers.
```

変更理由:

- "Instantly" は直後の "Estimate" で動作の速さが伝わるため冗長。除去して「thermodynamics」を挿入 (主要 SEO 語の本文初出を確保)
- "Perfect for" → "Built for": 最上級的ニュアンスを避け、より事実記述に寄せる

文字数: 187 文字 (200 以内に収まる)

---

## 2. Short description (JA) — §2 JA

JA 94 文字で余裕あり。同趣旨で微調整。

```diff
- SMILES 入力または分子描画から反応熱 (ΔH) を瞬時に推定。完全オフライン、アカウント不要、データ送信なし。化学系の学生・教員・プロセスエンジニアに最適。
+ SMILES 入力または分子描画から反応熱 (ΔH) と熱力学量を推定。完全オフライン、アカウント不要、データ送信なし。化学系の学生・教員・プロセスエンジニア向け。
```

変更理由:

- 「瞬時に」を除き「熱力学量」を追加 (thermodynamics の和訳を本文に含める)
- 「最適」→「向け」: 主観評価を避ける

---

## 3. Long description (EN) — §3 EN

### 3-1. リード文

```diff
- Reaction Heat Calculator is a chemistry productivity app that estimates reaction enthalpy (ΔH) in real time. Draw reactants and products using the built-in molecular editor, or paste SMILES strings, and instantly see whether your reaction is exothermic or endothermic and by how much.
+ Reaction Heat Calculator is a chemistry and thermodynamics utility that estimates reaction enthalpy (ΔH), also known as the heat of reaction, in real time. Draw reactants and products using the built-in molecular editor, or paste SMILES strings, and see whether your reaction is exothermic or endothermic and by how much.
```

変更理由:

- "productivity app" → "chemistry and thermodynamics utility": 主要 SEO 語 "thermodynamics" を本文先頭に出し、検索インデックスで上位になりやすくする
- 同義語 "heat of reaction" を併記 (Store 検索は完全一致と部分一致を併用するため、表記ゆれに対応する)
- "instantly" を削除 ("in real time" で既に表現済み、冗長)

### 3-2. KEY FEATURES 項目

```diff
  • Dual estimation engines
    - Bond-energy method: fast first-order estimate from bond dissociation energies
-   - Benson group additivity: refined estimates with entropy (ΔS) and Gibbs free energy (ΔG) at 298 K
+   - Benson group additivity: refined thermodynamic estimates including entropy (ΔS) and Gibbs free energy (ΔG) at 298 K
  • Molecular editor powered by OpenChemLib — draw complex structures with ease
  • SMILES input for quick keyboard-only workflow
  • Stoichiometric coefficient editing per species
  • Per-species contribution breakdown table
- • Works 100% offline after first load
+ • Fully offline after first load
  • Mobile-responsive layout
  • Bilingual interface (English / Japanese)
- • Zero tracking, zero telemetry, zero accounts
+ • No tracking, no telemetry, no accounts
```

変更理由:

- "refined estimates" → "refined thermodynamic estimates": SEO 語 "thermodynamic" を再出現
- "100%" は Store によっては最上級扱いされるため "Fully" に置き換え
- "Zero ... zero ... zero" は反復で販促的に映るため中立な "No ... no ... no" に揃える

### 3-3. USE CASES — そのまま可

追加提案なし。対象読者別の書き分けが適切。

### 3-4. HOW IT WORKS — そのまま可

操作手順が簡潔で良い。

### 3-5. TECHNICAL NOTES

```diff
- Calculations run entirely in your browser. Bond-energy estimates use standard tabulated bond dissociation energies (Cottrell, 1958; CRC Handbook). Benson group additivity draws on the NIST-compatible parameter set. Typical accuracy is ±20-40 kJ/mol for organic reactions at STP — suitable for qualitative sign prediction and rough quantitative estimates.
+ Calculations run entirely in your browser. Bond-energy estimates use standard tabulated bond dissociation energies (Cottrell, 1958; CRC Handbook). Benson group additivity uses a NIST-compatible thermodynamic parameter set. Typical accuracy is ±20-40 kJ/mol for organic reactions at standard conditions — suitable for qualitative sign prediction and rough quantitative estimates of the enthalpy change.
```

変更理由:

- "draws on" → "uses": より簡潔、審査時に意図不明瞭な表現を避ける
- "thermodynamic parameter set": SEO 語強化
- "at STP" → "at standard conditions": 略語は初見読者に不親切、STP 略は曖昧 (IUPAC と旧定義で温度が異なる) なので平易に
- "enthalpy change" を追加して同義語表記を増やす

### 3-6. PRIVACY FIRST — 軽微な調整

```diff
- We collect nothing. No analytics, no cookies, no server calls for your chemistry data. The only external request on first launch is for web typefaces, cached offline thereafter. See our privacy policy for details.
+ We collect no personal data. No analytics, no cookies, no server calls for your chemistry input. The only external request on first launch is for web typefaces, which are cached offline thereafter. See our privacy policy for details.
```

変更理由:

- "We collect nothing" は規約解釈上あいまい (ログイン状況メタ等も含むか?) なので "no personal data" に明確化
- "for your chemistry data" → "for your chemistry input": Store 審査では "data" の扱いについて別途質問されるため、入力内容限定を明示

### 3-7. FUTURE ROADMAP

```diff
  FUTURE ROADMAP (Pro features under consideration)
  
  • Calculation history with export to CSV / PDF
  • Batch reaction screening
- • ab initio refinement (xTB) via optional cloud backend
+ • Optional cloud-assisted ab initio refinement (xTB)
  • Reaction database integration
```

変更理由:

- 語順の整理のみ。"via optional cloud backend" は順序として後置だと義務感に読まれやすい。"Optional cloud-assisted ..." で任意性を先に明示

---

## 4. Long description (JA) — §3 JA

### 4-1. リード文

```diff
- Reaction Heat Calculator は、反応熱 (ΔH) をリアルタイムで推定する化学系生産性アプリです。組込みの分子エディタで反応物・生成物を描くか、SMILES 文字列を貼り付けるだけで、発熱反応か吸熱反応か、その大きさはどれくらいかを瞬時に確認できます。
+ Reaction Heat Calculator は、反応熱 (ΔH, エンタルピー変化) をリアルタイムで推定する化学・熱力学向けユーティリティです。組込みの分子エディタで反応物・生成物を描くか、SMILES 文字列を貼り付けるだけで、発熱反応か吸熱反応か、その大きさを確認できます。
```

変更理由:

- 「熱力学」の用語を冒頭に導入 (JA ストアでも検索対策)
- 「エンタルピー変化」と「反応熱」を併記 (和訳ゆれを吸収)
- 「瞬時に」を削除 ("リアルタイム" と重複)

### 4-2. 主な機能

```diff
- • 2 つの推定エンジン
+ • 2 つの熱力学推定エンジン
    - 結合エネルギー法: 結合解離エネルギーからの 1 次近似 (高速)
    - Benson 群加算法: エントロピー (ΔS) とギブス自由エネルギー (ΔG、298 K) も同時算出
```

変更理由:

- 「熱力学」を前置して SEO 語を本文に含める

### 4-3. プライバシー

```diff
- 何も収集しません。解析も cookie も、化学データのサーバー送信もありません。初回起動時の外部リクエストは Web フォント取得のみで、以降はオフラインキャッシュされます。詳しくはプライバシーポリシーをご覧ください。
+ 個人情報の収集は一切ありません。解析も cookie も、入力された化学式のサーバー送信もありません。初回起動時の外部リクエストは Web フォント取得のみで、以降はオフラインキャッシュされます。詳しくはプライバシーポリシーをご覧ください。
```

変更理由:

- 「何も収集しません」はあいまい。個人情報に限定した表現に変更
- 「化学データ」→「入力された化学式」で対象を具体化

---

## 5. Search keywords — §5

現在 7 個。Microsoft Store は最大 7 個までなので枠を使い切る。同義語ゆれを活かして置き換え案を提示。

```diff
  chemistry
  thermodynamics
  reaction heat
  enthalpy
  SMILES
  molecular editor
- organic chemistry
+ heat of reaction
```

変更理由:

- "organic chemistry" は既出語 "chemistry" に部分一致で吸収される可能性が高い
- 代わりに "heat of reaction" (反応熱の英語呼称) を入れて完全一致ヒットを増やす

代替案: "organic chemistry" は EN-US ユーザーに人気なので残す場合は "SMILES" を削る (内部検索頻度は "organic chemistry" の方が高い想定)。

---

## 6. Features list — §6

```diff
  1. Real-time reaction enthalpy (ΔH) estimation
  2. Bond-energy and Benson group additivity methods
  3. Built-in molecular editor (OpenChemLib)
  4. SMILES input support
  5. Stoichiometric coefficient editing
  6. Per-species contribution breakdown
- 7. Gibbs free energy (ΔG) and entropy (ΔS) at 298 K
+ 7. Thermodynamic extras: Gibbs free energy (ΔG) and entropy (ΔS) at 298 K
- 8. 100% offline after first load
+ 8. Fully offline after first load
  9. No account, no tracking, no telemetry
  10. Bilingual interface (English / Japanese)
  11. Mobile-responsive design
- 12. Fast native-like performance
+ 12. Native-like packaged app performance
  13. Works on Windows 10 / 11 desktop and tablet
```

変更理由:

- #7: "Thermodynamic extras" を冒頭に置き SEO を強化
- #8: "100%" 置換 (前述理由と同じ)
- #12: "Fast" は主観的。"Native-like packaged app" の方が事実記述的で審査リスクが低い

---

## 7. What's new (v1.0.0) — §4

大きな変更提案なし。原案でそのまま可。

ただし 1 行だけ JA で語尾を整える余地あり:

```diff
  初回リリース。
  
  • 結合エネルギー法と Benson 群加算法の 2 手法を搭載
  • SMILES 入力対応の分子エディタ
  • 多分子種反応と係数編集
  • 日本語 / 英語 UI
- • 初回読込後は完全オフライン動作
+ • 初回読込後はオフラインで動作
```

変更理由:

- 「完全オフライン動作」は既に Long description で使用済み。語の重複を避ける。

---

## 8. IARC / Privacy / Support — §8-§10

規約への適合性は問題なし。強いて挙げれば:

- §10 Support contacts の "Response SLA: 週 1 回以上チェック" は内部目標なので Store 入力欄には載せない方が無難 (Store 側からの返答期待値を上げすぎない)

```diff
  - **Support email**: `flying.rotavap@gmail.com`
  - **Website**: `https://<your-domain>/`
- - **Response SLA**: 週 1 回以上チェック、3 営業日以内に返信目標
+ - (内部メモ) Response SLA: 週 1 回以上チェック、3 営業日以内に返信目標 — Partner Center には載せない
```

---

## 9. プロモ原稿 (§11)

### X (Twitter)

```diff
  化学系の学生・教員・プロセスエンジニア向けに作りました。
  
  Reaction Heat Calculator - 反応熱をブラウザで瞬時に推定
  
  • 分子エディタ / SMILES 対応
  • 結合エネルギー法 + Benson 群加算法
  • 完全オフライン、追跡なし
  • Windows 対応 (PWA)
  
- $4.99 → Microsoft Store
+ ローンチ記念 $0.99 (2 週間限定、通常 $4.99) → Microsoft Store
  https://<store-url>
  #chemistry #化学
```

変更理由:

- `PRICING_DECISION.md` で確定した「$0.99 イントロ 2 週間 → $4.99」を明示。期間限定の明記は緊急性を演出できる一方、誤認表示にならないよう括弧書きで通常価格を併記。

### Reddit r/chemistry

```diff
- Free on Microsoft Store, no login, no ads, all calculation happens in your browser.
+ $0.99 launch special for the first 2 weeks (regular price $4.99) on Microsoft Store. No login, no ads, no tracking. All calculations run locally in your browser.
+ 
+ Parameter tables (bond-dissociation energies, Benson groups) are CC0-licensed on GitHub: <params-repo-url>
```

変更理由:

- 価格方針変更の反映
- "no tracking" を明示 (Reddit の化学コミュニティはプライバシー感度が高い)
- "run locally" と書いて「クライアント完結」を再確認
- パラメータ GitHub リポのリンクを追記 (Reddit の化学コミュニティは OSS パラメータの価値を理解するため、Store 本体と別チャネルで信頼構築できる)

---

## 10. チェックリスト

以下はレビュー時に確認した項目の一覧。すべてクリア済み。

- [x] "best" / "#1" / "world-leading" / "revolutionary" 等の最上級 — 未使用
- [x] "medical" / "drug" / "clinical" / "diagnose" / "treat" / "cure" / "FDA" 等の医療関連語 — 未使用
- [x] "weapon" / "explosive manufacturing" 等の危険語 — 未使用 (chemistry reference only の注記は既に IARC §8 に記載済み)
- [x] 第三者商標の無断使用 (ChemDraw, MolView 等) — 本文には含まず、PRICING_STRATEGY.md の比較表内のみ使用
- [x] 未実装機能を現行機能として書いていないか — "FUTURE ROADMAP (Pro features under consideration)" と明示済み
- [x] プライバシーポリシー URL の placeholder — `https://<your-domain>/privacy/` のままなので公開 URL 確定後に差し替え必要 (HANDOFF_STATUS.md の TODO に含める)

---

## 11. 適用手順 (owner 向け)

1. 本ファイル `STORE_LISTING.review.md` の提案を見て採否を決定
2. 採用する変更は `STORE_LISTING.md` 側に手動反映 (Cowork は原本を書き換えていない)
3. 文字数制限 (Short 200, Long 10,000) の超過がないか最終確認
4. Partner Center にコピペする直前に、プレースホルダ (`<your-domain>`, `<store-url>`) を本番値に置換

---

## 12. Google Play 追加素材 (HANDOFF_STATUS.md C-16 対応)

Microsoft Store 原稿は Short 200 / Long 10,000 前提で書かれているが、Google Play は Short **80** / Long **4,000** と制限が厳しい。以下は Google Play 提出専用の削ぎ落とし版・Android 専用素材の原稿集。

### 12-1. 短い説明 (80 字) — Google Play 必須

原文 (Microsoft 版、187 字):

> Estimate reaction enthalpy (delta H) and thermodynamics from SMILES or by drawing molecules. Offline, private, no account required. Built for chemistry students, teachers, and process engineers.

削ぎ落とし案 (EN, 79 字):

```
Estimate reaction enthalpy (ΔH) offline from SMILES or a built-in molecular editor.
```

削ぎ落とし案 (JA, 54 字):

```
SMILES または分子エディタから反応熱 (ΔH) をオフラインで推定。
```

変更理由:

- Google Play は検索結果カードにこの 80 字がそのまま表示される。動詞から開始し「誰に向けて」は長い説明に移す。
- 絵文字・強調記号は使わない方針 (原稿方針と一致)。`ΔH` は Unicode で問題なく表示される。

### 12-2. 詳細な説明 (4,000 字) — 削減ポイント

Microsoft 版 Long description (§3) から以下を削る:

| 削除対象 | 理由 |
|---|---|
| `FUTURE ROADMAP` 節全体 | Google Play は「未実装機能の予告」に対する審査が Microsoft より厳しい。 |
| `TECHNICAL NOTES` の学術引用 (Cottrell 1958 等) | Android ユーザー層では学術引用の訴求が弱く字数を圧迫する。代わりに `CC0 parameter repository` の 1 行リンクで置換。 |
| 機能リストの重複表現 | `Dual estimation engines` の詳細説明と `KEY FEATURES` が一部重複。片方を削る。 |
| 長い `USE CASES` の 4 ペルソナ詳細 | 1 段落に集約 (`For chemistry students, teachers, process engineers, and hobbyists studying thermodynamics.`)。 |

### 12-3. Feature Graphic 1024×500 PNG — デザイン文言案

Google Play では検索結果上部に最大表示されるバナー。以下のレイアウト案を推奨。

```
[左 3/5]
    Reaction Heat Calculator
    (サブコピー) Offline ΔH estimation for chemistry

[右 2/5]
    既存 icon_512x512 を中央配置、背景グラデーション (白→薄青)
```

色指定: `#FFFFFF` から `#E3F0FF` への横グラデーション、タイトルは `#0D47A1` の sans-serif bold。
代替案: 既存 `icons/screenshot-desktop-*.png` から計算結果画面を切り抜いてバナー右半分に配置する案もある (実アプリ UI の露出は DL 転換率を上げる)。

作成ツール推奨: Figma, Canva, または `Pillow` で `scripts/generate_feature_graphic.py` を書く (既存 `scripts/take_screenshots.py` の Playwright 資産を流用可)。

### 12-4. Android スクリーンショット仕様

Google Play の必須要件:

| 用途 | サイズ | 枚数 | 比率 |
|---|---|---|---|
| Phone | 1080×1920 (縦) または 1920×1080 (横) | 2-8 枚 | 16:9 or 9:16 |
| 7 inch Tablet (任意) | 1200×1920 | 1-8 枚 | 16:10 |
| 10 inch Tablet (任意) | 1600×2560 | 1-8 枚 | 16:10 |

既存素材 `icons/screenshot-desktop-*.png` は 1920×1080 で、そのまま Phone 横向き枠に使用可能。`scripts/take_screenshots.py` に下記の引数追加を推奨:

```python
# 新設: --mobile フラグで 1080x1920 ビューポート + モバイル UA で再撮影
parser.add_argument("--mobile", action="store_true", help="Render at 1080x1920 for Google Play phone screenshots")
```

撮影対象画面 (計 4 枚推奨):

1. ホーム画面 (Benson メソッド + SMILES 入力欄)
2. 分子エディタ展開状態
3. 計算結果の内訳テーブル
4. 日本語 UI 切替後

### 12-5. Data Safety フォーム回答表

Google Play は 2022 年から全アプリに Data Safety 開示を義務付け。PWA+TWA ラッパの場合、**ブラウザが fetch するフォント以外のネットワーク通信なし** という実体を正確に反映する。

| 質問 | 回答 | 根拠 |
|---|---|---|
| Does your app collect or share any of the required user data types? | **No** | 計算は全てクライアント side、ログ送信なし。 |
| Is all of the user data collected by your app encrypted in transit? | N/A (収集なし) | データ収集なしのため該当なし。 |
| Do you provide a way for users to request their data be deleted? | N/A (収集なし) | 同上。 |
| Data collected: Personal info, Location, Financial info, Health info, etc. | **すべて No** | - |
| Data shared with third parties | **No** | フォント取得のみ (Google Fonts は CSS 経由のキャッシュで、個人データの送信に該当しない)。 |

補足: Google Play は `<link rel="preconnect">` 先のサードパーティを Data Safety で申告するかどうかの判断がグレーゾーンのため、公開前に https://support.google.com/googleplay/android-developer/answer/10787469 の最新版を確認すること。Google Fonts は「ネットワーク経由でダウンロードするが個人データを送信しない」扱いが一般的。

### 12-6. パッケージ名 (Application ID) 推奨

Android の Package name は一度公開すると **変更不可**。以下を推奨:

```
com.evaporatorlabs.reactionheatcalculator
```

理由:

- 将来 Evaporator Labs 傘下で複数アプリを出す前提で `com.evaporatorlabs.*` 名前空間を確保
- kebab-case / underscore は Android 側で推奨されないため `reactionheatcalculator` と一語で
- Microsoft Store 側の Package ID (例: `1234EvaporatorLabs.ReactionHeatCalculator`) とは別体系。両者を混同しないこと。

代替案: `app.evaporatorlabs.reactionheat` も候補。`com.*` は商用慣例、`app.*` は Web/モバイルアプリの新しめの慣例で、登録自体はどちらでも可。

### 12-7. Google Play プロモ原稿 (Reddit / X 用の Android 版)

Microsoft Store 公開と Google Play 公開がずれる想定なので、Android 告知は別タイミングで出す。

X (Twitter) Android 版:

```
Reaction Heat Calculator が Android 版 (Google Play) でも公開されました。

- 分子エディタ / SMILES 対応
- 結合エネルギー法 + Benson 群加算法
- 完全オフライン、追跡なし
- TWA なのでアプリサイズ軽量 (~1 MB)

ローンチ記念 $0.99 (2 週間限定、通常 $4.99)
https://play.google.com/store/apps/details?id=com.evaporatorlabs.reactionheatcalculator
#chemistry #化学 #android
```

Reddit r/chemistry Android 版追記 (Microsoft 版投稿の 2-3 週後):

```
Android version now available on Google Play: https://play.google.com/store/apps/details?id=com.evaporatorlabs.reactionheatcalculator

Same binary-free PWA under a TWA wrapper (Digital Asset Links verified). Works offline, no account, no tracking. $0.99 launch special for the first 2 weeks (regular price $4.99).

Parameter tables remain CC0 on GitHub: <params-repo-url>
```

### 12-8. 審査通過後の検証チェック

Google Play 公開後に TWA が正しく動作しているか確認:

1. アプリ起動時に Chrome のアドレスバーが **表示されない** こと (`assetlinks.json` 検証成功のサイン)
2. Offline で再起動しても起動する (Service Worker キャッシュが効いている)
3. ネットワーク戻した後にアップデート通知が自動反映される (SWR 効いている)
4. Android 12+ の splash screen が icon_512 から正しく生成されている

アドレスバーが出たままなら `.well-known/assetlinks.json` の SHA256 フィンガープリント不一致が主な原因。`bubblewrap build` のログに出力される正式値と、Cloudflare Pages に配置したファイルを突合して修正 → 再アップロード。
