# Deployment Guide — Cloudflare Pages

Evaporator Labs / Reaction Heat Energy Calculator

## 1. 前提

- GitHub (または GitLab) アカウント
- Cloudflare アカウント (無料)
- このリポジトリがリモートに push 済みであること

## 2. リポジトリ準備

`.gitignore` に以下を追加 (未追加であれば):

```
# Build output
dist/

# Worktrees / local artifacts
.claude/worktrees/
node_modules/
```

`build.sh` を実行可能にする:

```bash
chmod +x build.sh
./build.sh   # 動作確認: dist/ が生成されることを確認
```

## 3. Cloudflare Pages プロジェクト作成

1. [dash.cloudflare.com](https://dash.cloudflare.com/) → 左メニュー **Workers & Pages** → **Create** → **Pages** タブ → **Connect to Git**
2. GitHub 連携を許可し、このリポジトリを選択
3. ビルド設定:

   | 項目 | 値 |
   |---|---|
   | Project name | `reaction-heat-calculator` (任意、サブドメイン名になる) |
   | Production branch | `main` |
   | Framework preset | **None** |
   | Build command | `bash build.sh` |
   | Build output directory | `dist` |
   | Root directory | (空欄のまま) |
   | Environment variables | (不要) |

4. **Save and Deploy** で初回ビルド開始 (1〜2 分)

デプロイ完了後、`https://reaction-heat-calculator.pages.dev` で公開されます。

## 4. 独自ドメインを当てる (任意)

1. プロジェクト → **Custom domains** → **Set up a custom domain**
2. 例: `calc.evaporatorlabs.com` 入力 → DNS レコード自動追加を許可
3. 伝播後 HTTPS 証明書は自動発行

独自ドメインを使う場合は PWA 申請時の URL もこちらに統一してください。

## 5. 動作確認チェックリスト

デプロイ後、本番 URL で以下を確認:

- [ ] `https://<domain>/` で本体が開く
- [ ] `https://<domain>/privacy/` でポリシーが開く
- [ ] DevTools → Application → **Manifest** が 200 で読まれている
- [ ] DevTools → Application → **Service Workers** が `activated` になっている
- [ ] DevTools → Application → **Cache Storage** に `rxn-heat-v1-shell` が存在
- [ ] オフライン化 (DevTools → Network → Offline) でリロードしても開く
- [ ] Lighthouse → **Installable** 合格 (PWA 監査)
- [ ] Chrome アドレスバー右端に「インストール」アイコンが出る

## 6. 更新フロー

コード変更 → `git push origin main` → Cloudflare Pages が自動でビルド & デプロイ。

Service Worker は `CACHE_VERSION = 'rxn-heat-v1'` を `service-worker.js` 内で管理しています。
**重要な変更があるたびに `v1` → `v2` のようにインクリメント**してください。
古いキャッシュはアクティベート時に自動削除されます。

## 7. 次のステップ

本番 URL が確定したら次は:

1. Lighthouse / PWABuilder でスコア 100 を目指す (Step 3)
2. Store 用スクリーンショット撮影 (Step 4)
3. Partner Center 登録 + MSIX 生成 (Step 5)
