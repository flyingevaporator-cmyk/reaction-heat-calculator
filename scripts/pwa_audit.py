#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pwa_audit.py — Reaction Heat Calculator の PWA 妥当性をローカル監査するスクリプト

用途:
  Cloudflare Pages への本番デプロイ前に、manifest.json と service-worker.js が
  PWABuilder (https://www.pwabuilder.com/) のスコア 90+ を満たす最低条件を
  備えているかをローカルでチェックする。

使い方:
  $ python scripts/pwa_audit.py                # リポジトリルートから静的チェックのみ
  $ python scripts/pwa_audit.py --serve        # http.server を起動して localhost 経由でも検証
  $ python scripts/pwa_audit.py --port 8000    # ポート指定 (デフォルト 8000)
  $ python scripts/pwa_audit.py --root ./dist  # dist/ を対象にする (ビルド後のチェック向け)

終了コード:
  0: すべてのチェック通過 (PASS)
  1: 1 つ以上の必須項目が NG

出力:
  PWA_AUDIT.md に Markdown レポートを書き出す (--report で出力先変更可能)

依存:
  標準ライブラリのみ (json, http.server, urllib, argparse, pathlib, re)
"""

from __future__ import annotations

import argparse
import contextlib
import http.server
import json
import re
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# --- 判定ルール --------------------------------------------------------------

MANIFEST_REQUIRED_FIELDS: list[str] = [
    "name",
    "short_name",
    "start_url",
    "display",
    "icons",
    "background_color",
    "theme_color",
]

REQUIRED_ICON_SIZES: list[int] = [192, 512]
DISPLAY_VALID_VALUES = {"standalone", "fullscreen", "minimal-ui", "browser"}


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class AuditReport:
    checks: list[CheckResult] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append(CheckResult(name, passed, detail))

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def as_markdown(self, root: Path, served_url: str | None) -> str:
        lines: list[str] = []
        lines.append("# PWA 監査レポート (PWA_AUDIT.md)")
        lines.append("")
        lines.append("Evaporator Labs / Reaction Heat Energy Calculator")
        lines.append("")
        lines.append(f"- 監査対象ルート: `{root}`")
        if served_url:
            lines.append(f"- ローカルサーバ: {served_url}")
        lines.append(f"- 実行時刻 (UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
        lines.append("")
        lines.append(f"- 総合判定: **{'PASS' if self.all_passed else 'FAIL'}**")
        passed = sum(1 for c in self.checks if c.passed)
        lines.append(f"- 通過: {passed} / {len(self.checks)}")
        lines.append("")
        lines.append("## チェック結果")
        lines.append("")
        lines.append("| # | 項目 | 結果 | 詳細 |")
        lines.append("|---|---|---|---|")
        for i, c in enumerate(self.checks, 1):
            status = "PASS" if c.passed else "FAIL"
            detail = c.detail.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {i} | {c.name} | {status} | {detail} |")
        lines.append("")
        lines.append("## 補足")
        lines.append("")
        lines.append(
            "本監査はローカル検証のため、本番環境で追加されるチェック "
            "(HTTPS / valid SSL cert / Lighthouse パフォーマンス) は範囲外。"
        )
        lines.append(
            "本番 URL 確定後は https://www.pwabuilder.com/ で最終スコアを確認すること。"
        )
        lines.append("")
        return "\n".join(lines)


# --- 静的チェック本体 ---------------------------------------------------------

def check_manifest(root: Path, report: AuditReport) -> dict | None:
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        report.add("manifest.json が存在する", False, f"見つからない: {manifest_path}")
        return None
    report.add("manifest.json が存在する", True, str(manifest_path))

    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        report.add("manifest.json が有効な JSON", False, str(e))
        return None
    report.add("manifest.json が有効な JSON", True, "")

    for field_name in MANIFEST_REQUIRED_FIELDS:
        value = manifest.get(field_name)
        present = value not in (None, "", [], {})
        report.add(
            f"manifest: 必須フィールド `{field_name}` が設定",
            present,
            "" if present else "空または未定義",
        )

    display = manifest.get("display", "")
    report.add(
        "manifest: `display` の値が仕様内 (standalone / fullscreen / minimal-ui / browser)",
        display in DISPLAY_VALID_VALUES,
        f"現在値: `{display}`",
    )

    icons = manifest.get("icons", [])
    size_ok = {s: False for s in REQUIRED_ICON_SIZES}
    svg_any = False
    maskable = False
    for icon in icons:
        sizes_attr = icon.get("sizes", "")
        purpose = icon.get("purpose", "any")
        if "maskable" in purpose:
            maskable = True
        if sizes_attr == "any":
            svg_any = True
            for k in size_ok:
                size_ok[k] = True
            continue
        for token in sizes_attr.split():
            m = re.match(r"(\d+)x(\d+)", token)
            if not m:
                continue
            w = int(m.group(1))
            for need in REQUIRED_ICON_SIZES:
                if w >= need:
                    size_ok[need] = True

    for need, ok in size_ok.items():
        report.add(
            f"manifest: {need}x{need} 以上相当のアイコンが存在",
            ok,
            ("svg any でカバー" if svg_any else f"{need}x{need} 以上の PNG を manifest に登録"),
        )

    report.add(
        "manifest: maskable アイコンが 1 つ以上 (推奨項目だが 90+ スコアに効く)",
        maskable,
        "purpose に maskable を含むアイコンが必要" if not maskable else "",
    )

    start_url = manifest.get("start_url", "")
    start_url_ok = isinstance(start_url, str) and start_url != ""
    report.add("manifest: `start_url` が非空の文字列", start_url_ok, f"値: `{start_url}`")

    for color_field in ("theme_color", "background_color"):
        val = manifest.get(color_field, "")
        color_ok = bool(re.match(r"^#[0-9A-Fa-f]{3,8}$|^[a-zA-Z]+$", val))
        report.add(f"manifest: `{color_field}` が有効な色値", color_ok, f"値: `{val}`")

    screenshots = manifest.get("screenshots", [])
    report.add(
        "manifest: `screenshots` が 1 件以上 (Store 表示で効果大)",
        isinstance(screenshots, list) and len(screenshots) > 0,
        f"件数: {len(screenshots) if isinstance(screenshots, list) else 0}",
    )

    return manifest


def check_service_worker(root: Path, report: AuditReport, manifest_scope: str) -> None:
    sw_path = root / "service-worker.js"
    if not sw_path.exists():
        report.add("service-worker.js が存在する", False, f"見つからない: {sw_path}")
        return
    report.add("service-worker.js が存在する", True, str(sw_path))

    code = sw_path.read_text(encoding="utf-8")

    has_fetch = bool(re.search(r"addEventListener\s*\(\s*['\"]fetch['\"]", code))
    report.add("SW: fetch イベントハンドラを登録", has_fetch, "")

    has_install = bool(re.search(r"addEventListener\s*\(\s*['\"]install['\"]", code))
    report.add("SW: install イベントハンドラを登録", has_install, "")

    has_activate = bool(re.search(r"addEventListener\s*\(\s*['\"]activate['\"]", code))
    report.add("SW: activate イベントハンドラを登録", has_activate, "")

    report.add(
        "SW: manifest.scope が設定されている (= SW の有効範囲)",
        bool(manifest_scope),
        f"scope: `{manifest_scope}`",
    )


def check_index_html_registers_sw(root: Path, report: AuditReport) -> None:
    index = root / "index.html"
    if not index.exists():
        report.add("index.html が存在する", False, f"見つからない: {index}")
        return
    report.add("index.html が存在する", True, "")

    register_found = False
    manifest_link_found = False
    theme_meta_found = False
    viewport_found = False
    with index.open("r", encoding="utf-8", errors="replace") as f:
        carry = ""
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            buf = carry + chunk
            if not register_found and re.search(r"serviceWorker\.register\s*\(", buf):
                register_found = True
            if not manifest_link_found and re.search(
                r"<link[^>]+rel=['\"]manifest['\"]", buf, re.IGNORECASE
            ):
                manifest_link_found = True
            if not theme_meta_found and re.search(
                r"<meta[^>]+name=['\"]theme-color['\"]", buf, re.IGNORECASE
            ):
                theme_meta_found = True
            if not viewport_found and re.search(
                r"<meta[^>]+name=['\"]viewport['\"]", buf, re.IGNORECASE
            ):
                viewport_found = True
            carry = buf[-1024:]

    report.add("index.html 内に serviceWorker.register 呼び出し", register_found, "")
    report.add("index.html 内に manifest への <link rel=\"manifest\">", manifest_link_found, "")
    report.add("index.html に theme-color メタタグ", theme_meta_found, "")
    report.add("index.html に viewport メタタグ", viewport_found, "")


def check_icons_exist_on_disk(root: Path, manifest: dict | None, report: AuditReport) -> None:
    if manifest is None:
        return
    icons = manifest.get("icons", [])
    missing: list[str] = []
    for icon in icons:
        src = icon.get("src", "")
        if not src:
            continue
        rel = src.lstrip("./")
        p = root / rel
        if not p.exists():
            missing.append(src)
    report.add(
        "manifest.icons で参照される全ファイルがディスク上に存在",
        not missing,
        (f"欠損: {missing}" if missing else ""),
    )


def check_privacy_page(root: Path, report: AuditReport) -> None:
    p = root / "privacy" / "index.html"
    report.add(
        "プライバシーポリシー (privacy/index.html) が存在",
        p.exists(),
        str(p) if p.exists() else "Store 審査でプライバシー URL が必要",
    )


# --- オプショナル: localhost での到達性確認 ------------------------------------

class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    """ログを抑えた静的配信ハンドラ。"""

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        pass


@contextlib.contextmanager
def _serve_directory(root: Path, port: int):
    import os

    cwd = os.getcwd()
    os.chdir(root)
    try:
        with socketserver.TCPServer(("127.0.0.1", port), _QuietHandler) as httpd:
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            try:
                yield f"http://127.0.0.1:{port}/"
            finally:
                httpd.shutdown()
    finally:
        os.chdir(cwd)


def check_via_http(root: Path, port: int, report: AuditReport) -> str | None:
    try:
        with _serve_directory(root, port) as base_url:
            time.sleep(0.3)
            for rel, label in [
                ("manifest.json", "HTTP: manifest.json が 200 で取得できる"),
                ("service-worker.js", "HTTP: service-worker.js が 200 で取得できる"),
                ("index.html", "HTTP: index.html が 200 で取得できる"),
                ("privacy/index.html", "HTTP: privacy/index.html が 200 で取得できる"),
            ]:
                url = base_url + rel
                try:
                    with urllib.request.urlopen(url, timeout=5) as resp:
                        ok = resp.status == 200
                        report.add(label, ok, f"{resp.status} {url}")
                except (urllib.error.URLError, TimeoutError) as e:
                    report.add(label, False, f"{type(e).__name__}: {e}")
            return base_url
    except OSError as e:
        report.add("HTTP: ローカルサーバ起動", False, str(e))
        return None


# --- main --------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Reaction Heat Calculator PWA 監査")
    parser.add_argument("--root", default=".", help="監査対象ディレクトリ")
    parser.add_argument("--serve", action="store_true", help="ローカル HTTP サーバを立てて検証")
    parser.add_argument("--port", type=int, default=8000, help="HTTP サーバのポート")
    parser.add_argument("--report", default="PWA_AUDIT.md", help="レポート出力先")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2

    report = AuditReport()
    manifest = check_manifest(root, report)
    scope = manifest.get("scope", "") if manifest else ""
    check_service_worker(root, report, scope)
    check_index_html_registers_sw(root, report)
    check_icons_exist_on_disk(root, manifest, report)
    check_privacy_page(root, report)

    served_url: str | None = None
    if args.serve:
        served_url = check_via_http(root, args.port, report)

    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = root / report_path
    report_path.write_text(report.as_markdown(root, served_url), encoding="utf-8")

    passed = sum(1 for c in report.checks if c.passed)
    total = len(report.checks)
    print(f"PWA audit: {passed}/{total} PASS -> {report_path}")
    for c in report.checks:
        status = "PASS" if c.passed else "FAIL"
        print(f"  [{status}] {c.name}  {c.detail}")

    return 0 if report.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
