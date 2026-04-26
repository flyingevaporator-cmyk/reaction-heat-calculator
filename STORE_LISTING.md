# Microsoft Store リスティング原稿集

Evaporator Labs / Reaction Heat Energy Calculator

Partner Center の入力フォームにコピペする用の原稿を JA/EN 両方で用意しています。

---

## 1. App name (product name) — 必須

- **EN**: `Reaction Heat Calculator`
- **JA**: `反応熱計算機` (Partner Center はアプリ名の多言語設定が可能)

> 補足: Microsoft Store は同名アプリの存在チェックを行うので、予約前に [Store 検索](https://apps.microsoft.com/home) で重複確認しておくこと。

## 2. Short description — 200 文字以内

### EN (178 chars)

```
Estimate reaction enthalpy (delta H) and thermodynamics from SMILES or by drawing molecules. Offline, private, no account required. Built for chemistry students, teachers, and process engineers.
```

### JA (94 文字)

```
分子描画またはSMILES 入力から反応熱 (ΔH) と熱力学量を推定。完全オフライン、アカウント不要、データ送信なし。化学系の学生・教員・プロセスエンジニア向け。
```

## 3. Long description — 10,000 文字以内

### EN

```
Reaction Heat Calculator is a chemistry and thermodynamics utility that estimates reaction enthalpy (ΔH), also known as the heat of reaction, in real time. Draw reactants and products using the built-in molecular editor, or paste SMILES strings, and see whether your reaction is exothermic or endothermic and by how much.

KEY FEATURES

• Dual estimation engines
  - Bond-energy method: fast first-order estimate from bond dissociation energies
  - Benson group additivity: refined thermodynamic estimates including entropy (ΔS) and Gibbs free energy (ΔG) at 298 K
• Molecular editor powered by OpenChemLib — draw complex structures with ease
• SMILES input for quick keyboard-only workflow
• Stoichiometric coefficient editing per species
• Per-species contribution breakdown table
• Fully offline after first load
• Mobile-responsive layout
• Bilingual interface (English / Japanese)
• No tracking, no telemetry, no accounts

USE CASES

• Students verifying homework reactions (combustion, hydrogenation, neutralization)
• Teachers demonstrating thermochemistry concepts in class
• Process engineers doing quick back-of-the-envelope heat balances
• R&D chemists prioritizing reaction routes by exothermicity

HOW IT WORKS

1. Draw a molecule in the structure editor (or type SMILES like CCO for ethanol)
2. Click "+ Reactant" or "+ Product"
3. Repeat for each species and adjust coefficients if needed
4. Click "Calculate ΔH" — results appear instantly with full breakdown

TECHNICAL NOTES

Calculations run entirely in your browser. Bond-energy estimates use standard tabulated bond dissociation energies (Cottrell, 1958; CRC Handbook). Benson group additivity uses a NIST-compatible thermodynamic parameter set. Typical accuracy is ±20-40 kJ/mol for organic reactions at standard conditions — suitable for qualitative sign prediction and rough quantitative estimates of the enthalpy change.

PRIVACY FIRST

We collect no personal data. No analytics, no cookies, no server calls for your chemistry input. The only external request on first launch is for web typefaces, which are cached offline thereafter. See our privacy policy for details.

FUTURE ROADMAP (Pro features under consideration)

• Calculation history with export to CSV / PDF
• Batch reaction screening
• Optional cloud-assisted ab initio refinement (xTB)
• Reaction database integration

Feedback and feature requests: flying.rotavap@gmail.com
```

### JA

```
Reaction Heat Calculator は、反応熱 (ΔH, エンタルピー変化) をリアルタイムで推定する化学・熱力学向けユーティリティです。組込みの分子エディタで反応物・生成物を描くか、SMILES 文字列を貼り付けるだけで、発熱反応か吸熱反応か、その大きさを確認できます。

主な機能

• 2 つの推定エンジン
  - 結合エネルギー法: 結合解離エネルギーからの 1 次近似 (高速)
    - Benson 群加算法: エントロピー (ΔS) とギブス自由エネルギー (ΔG、298 K) も同時算出
• OpenChemLib 搭載の分子エディタで複雑な構造も直感的に入力
• SMILES 直接入力でキーボードのみの高速ワークフロー
• 分子種ごとの化学量論係数の編集
• 分子種ごとの寄与を分解表示するブレイクダウン表
• 初回読込後は 100% オフライン動作
• モバイル対応のレスポンシブデザイン
• 日英バイリンガル UI
• 追跡なし、テレメトリなし、アカウント不要

利用シーン

• 学生: 燃焼・水素化・中和反応の宿題チェック
• 教員: 熱化学の授業デモ
• プロセスエンジニア: 熱収支の概算 (桁合わせ)
• R&D 化学者: 発熱量ベースで反応経路を優先順位付け

使い方

1. 構造エディタで分子を描画 (または SMILES を入力、例: エタノール = CCO)
2. 「+ Reactant」または「+ Product」をクリック
3. 各分子種について繰り返し、必要なら係数を調整
4. 「Calculate ΔH」をクリック — 詳細な分解と共に結果表示

技術的補足

計算はすべてブラウザ内で完結します。結合エネルギー推定は標準表 (Cottrell, 1958; CRC Handbook) を使用、Benson 群加算法は NIST 互換パラメータセットを採用。有機反応での典型精度は ±20〜40 kJ/mol 程度であり、符号の定性予測および桁合わせの定量推定に適しています。

プライバシー最優先

個人情報の収集は一切ありません。解析も cookie も、入力された化学式のサーバー送信もありません。初回起動時の外部リクエストは Web フォント取得のみで、以降はオフラインキャッシュされます。詳しくはプライバシーポリシーをご覧ください。

今後の予定 (Pro 機能として検討中)

• 計算履歴の CSV / PDF エクスポート
• バッチ反応スクリーニング
• オプションのクラウド連携による ab initio 精密化 (xTB)
• 反応データベース統合

フィードバック・機能要望: flying.rotavap@gmail.com
```

## 4. What's new in this version — 1,500 文字以内

### EN (v1.0.0)

```
Initial release.

• Bond-energy and Benson group additivity estimation methods
• Molecular editor with SMILES input
• Multi-species reactions with coefficient editing
• English / Japanese interface
• Fully offline-capable after first launch
```

### JA (v1.0.0)

```
初回リリース。

• 結合エネルギー法と Benson 群加算法の 2 手法を搭載
• SMILES 入力対応の分子エディタ
• 多分子種反応と係数編集
• 日本語 / 英語 UI
• 初回読込後はオフライン動作
```

## 5. Search keywords — 最大 7 個

```
chemistry
thermodynamics
reaction heat
enthalpy
SMILES
molecular editor
heat of reaction
```

## 6. Features list (Store 表示用ビュレット) — 最大 20 個、各 200 文字以内

1. Real-time reaction enthalpy (ΔH) estimation
2. Bond-energy and Benson group additivity methods
3. Built-in molecular editor (OpenChemLib)
4. SMILES input support
5. Stoichiometric coefficient editing
6. Per-species contribution breakdown
7. Thermodynamic extras: Gibbs free energy (ΔG) and entropy (ΔS) at 298 K
8. Fully offline after first load
9. No account, no tracking, no telemetry
10. Bilingual interface (English / Japanese)
11. Mobile-responsive design
12. Native-like packaged app performance
13. Works on Windows 10 / 11 desktop and tablet

## 7. System requirements

- **OS**: Windows 10 version 1809 (build 17763) or later
- **Architecture**: x64, ARM64, x86
- **RAM**: 512 MB minimum
- **Storage**: 50 MB
- **Display**: 1280×720 minimum

## 8. Age rating (IARC)

IARC 質問票の推奨回答:

| 質問 | 回答 |
|---|---|
| Does your app contain violent or aggressive content? | No |
| Does it feature firearms, explosives, or hazardous materials in an instructive way? | No (chemistry reference only, not how-to) |
| Does it feature gambling / real money betting? | No |
| Does it enable user-generated content sharing? | No |
| Does it collect personal information? | No |
| Does it include advertising? | No |

期待されるレーティング: **3+ (Everyone)**

## 9. Privacy-related answers (Partner Center では質問票形式で回答)

| 項目 | 回答 |
|---|---|
| Does your app collect personal info? | No |
| Does your app access any of these: microphone, camera, contacts, photos, location? | No |
| Does your app contain third-party tracking? | No |
| Does your app request specific permissions? | No (standard packaged app only) |
| Privacy policy URL | `https://<your-domain>/privacy/` |

## 10. Support contacts

- **Support email**: `flying.rotavap@gmail.com`
- **Response SLA**: 3 営業日以内に返信目標

---

## 11. ストア外のプロモーション原稿

### X (Twitter) ポスト案 (280 字)

```
化学系の学生・教員・プロセスエンジニア向けに作りました。

Reaction Heat Calculator - 反応熱をブラウザで瞬時に推定

• 分子エディタ / SMILES 対応
• 結合エネルギー法 + Benson 群加算法
• 完全オフライン、追跡なし
• Windows 対応 (PWA)

$4.99 → Microsoft Store
https://<store-url>
#chemistry #化学
```

### Reddit r/chemistry / r/chemhelp ポスト案

```
Title: Built a free ΔH calculator PWA — thought it might help students

After tutoring thermochemistry for a semester, I kept reaching for the same bond-energy table over and over. So I built a little web app that does the lookup + coefficient arithmetic automatically. Includes both bond-energy and Benson group additivity methods.

Free on Microsoft Store, no login, no ads, all calculation happens in your browser.

Open to feedback, especially on which functional-group parameters you'd most like added.

Link: <store url>
Privacy policy: <privacy url>
```

### 化学系 Discord / メーリングリスト向け短文

```
オフラインで動く反応熱 (ΔH) 推定 Web アプリを作りました。
結合エネルギー法と Benson 群加算法の両方、298 K での ΔG も。
完全クライアント側処理、入力データは外に出ません。
フィードバック歓迎: <url>
```
