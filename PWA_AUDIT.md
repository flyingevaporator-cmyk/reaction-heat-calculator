# PWA 監査レポート (PWA_AUDIT.md)

Evaporator Labs / Reaction Heat Energy Calculator

- 監査対象ルート: `/sessions/awesome-gallant-keller/mnt/calc`
- ローカルサーバ: http://127.0.0.1:8790/
- 実行時刻 (UTC): 2026-04-22T05:44:57Z

- 総合判定: **PASS**
- 通過: 33 / 33

## チェック結果

| # | 項目 | 結果 | 詳細 |
|---|---|---|---|
| 1 | manifest.json が存在する | PASS | /sessions/awesome-gallant-keller/mnt/calc/manifest.json |
| 2 | manifest.json が有効な JSON | PASS |  |
| 3 | manifest: 必須フィールド `name` が設定 | PASS |  |
| 4 | manifest: 必須フィールド `short_name` が設定 | PASS |  |
| 5 | manifest: 必須フィールド `start_url` が設定 | PASS |  |
| 6 | manifest: 必須フィールド `display` が設定 | PASS |  |
| 7 | manifest: 必須フィールド `icons` が設定 | PASS |  |
| 8 | manifest: 必須フィールド `background_color` が設定 | PASS |  |
| 9 | manifest: 必須フィールド `theme_color` が設定 | PASS |  |
| 10 | manifest: `display` の値が仕様内 (standalone / fullscreen / minimal-ui / browser) | PASS | 現在値: `standalone` |
| 11 | manifest: 192x192 以上相当のアイコンが存在 | PASS | svg any でカバー |
| 12 | manifest: 512x512 以上相当のアイコンが存在 | PASS | svg any でカバー |
| 13 | manifest: maskable アイコンが 1 つ以上 (推奨項目だが 90+ スコアに効く) | PASS |  |
| 14 | manifest: `start_url` が非空の文字列 | PASS | 値: `/?source=pwa` |
| 15 | manifest: `theme_color` が有効な色値 | PASS | 値: `#4f46e5` |
| 16 | manifest: `background_color` が有効な色値 | PASS | 値: `#f6f8fb` |
| 17 | manifest: `screenshots` が 1 件以上 (Store 表示で効果大) | PASS | 件数: 4 |
| 18 | service-worker.js が存在する | PASS | /sessions/awesome-gallant-keller/mnt/calc/service-worker.js |
| 19 | SW: fetch イベントハンドラを登録 | PASS |  |
| 20 | SW: install イベントハンドラを登録 | PASS |  |
| 21 | SW: activate イベントハンドラを登録 | PASS |  |
| 22 | SW: manifest.scope が設定されている (= SW の有効範囲) | PASS | scope: `/` |
| 23 | index.html が存在する | PASS |  |
| 24 | index.html 内に serviceWorker.register 呼び出し | PASS |  |
| 25 | index.html 内に manifest への <link rel="manifest"> | PASS |  |
| 26 | index.html に theme-color メタタグ | PASS |  |
| 27 | index.html に viewport メタタグ | PASS |  |
| 28 | manifest.icons で参照される全ファイルがディスク上に存在 | PASS |  |
| 29 | プライバシーポリシー (privacy/index.html) が存在 | PASS | /sessions/awesome-gallant-keller/mnt/calc/privacy/index.html |
| 30 | HTTP: manifest.json が 200 で取得できる | PASS | 200 http://127.0.0.1:8790/manifest.json |
| 31 | HTTP: service-worker.js が 200 で取得できる | PASS | 200 http://127.0.0.1:8790/service-worker.js |
| 32 | HTTP: index.html が 200 で取得できる | PASS | 200 http://127.0.0.1:8790/index.html |
| 33 | HTTP: privacy/index.html が 200 で取得できる | PASS | 200 http://127.0.0.1:8790/privacy/index.html |

## 補足

本監査はローカル検証のため、本番環境で追加されるチェック (HTTPS / valid SSL cert / Lighthouse パフォーマンス) は範囲外。
本番 URL 確定後は https://www.pwabuilder.com/ で最終スコアを確認すること。
