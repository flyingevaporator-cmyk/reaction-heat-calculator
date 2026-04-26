"""Playwright でストア用スクリーンショットを 4 枚自動生成するスクリプト.

事前条件:
  - プレビュー/静的サーバーが http://localhost:8000 で index.html を配信中であること
  - playwright + chromium がインストール済みであること
      pip install playwright
      python -m playwright install chromium

出力先: icons/
  - screenshot-desktop-1.png   (1920x1080)  空の初期画面
  - screenshot-desktop-2.png   (1920x1080)  反応入力済み
  - screenshot-desktop-3.png   (1920x1080)  ΔH 計算結果表示
  - screenshot-mobile-1.png    ( 720x1280)  モバイルレイアウト
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8000/index.html"
OUT = Path(__file__).resolve().parent.parent / "icons"
OUT.mkdir(exist_ok=True)


def add_molecule(page, smiles: str, side: str):
    """SMILES を入力して + Reactant or + Product ボタンを押す."""
    page.fill("#smilesInput", smiles)
    sel = "button.btn-reactant" if side == "reactant" else "button.btn-product"
    page.click(sel)
    page.wait_for_timeout(200)


def set_coeff(page, list_id: str, index: int, value: int):
    """指定リストの i 番目の係数入力欄に値をセット."""
    # .mol-item 内の .coeff
    loc = page.locator(f"#{list_id} .mol-item .coeff").nth(index)
    loc.fill(str(value))
    loc.blur()
    page.wait_for_timeout(100)


def take_desktop_shots(browser):
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=1,
        color_scheme="light",
    )
    page = context.new_page()
    page.goto(URL, wait_until="networkidle")
    # Ketcher 初期化待ち。なくても良いが描画のズレ防止。
    page.wait_for_timeout(1500)

    # ---- 1. 空の初期画面 ----
    page.screenshot(path=str(OUT / "screenshot-desktop-1.png"), full_page=False)
    print("  saved: screenshot-desktop-1.png")

    # ---- 2. 反応入力済み (メタン燃焼) ----
    # CH4 + 2 O2 -> CO2 + 2 H2O
    add_molecule(page, "C", "reactant")       # メタン
    add_molecule(page, "O=O", "reactant")     # 酸素
    add_molecule(page, "O=C=O", "product")    # 二酸化炭素
    add_molecule(page, "O", "product")        # 水
    # 係数調整
    set_coeff(page, "reactantList", 1, 2)     # O2 を 2
    set_coeff(page, "productList", 1, 2)      # H2O を 2
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / "screenshot-desktop-2.png"), full_page=False)
    print("  saved: screenshot-desktop-2.png")

    # ---- 3. 計算結果表示 ----
    page.click("#calcBtn")
    # 結果表示待ち (#resultBox から hidden が外れるのを待つ)
    try:
        page.wait_for_function(
            "document.getElementById('resultBox') && "
            "!document.getElementById('resultBox').classList.contains('hidden')",
            timeout=8000,
        )
    except Exception as e:
        print(f"  warn: result not shown within timeout: {e}")
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / "screenshot-desktop-3.png"), full_page=False)
    print("  saved: screenshot-desktop-3.png")

    context.close()


def take_mobile_shot(browser):
    context = browser.new_context(
        viewport={"width": 720, "height": 1280},
        device_scale_factor=1,
        color_scheme="light",
        is_mobile=True,
        has_touch=True,
    )
    page = context.new_page()
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(1500)

    # 少しだけコンテンツを入れた状態を撮る (ただの空よりも魅力的)
    add_molecule(page, "CCO", "reactant")      # エタノール
    add_molecule(page, "CC=O", "product")      # アセトアルデヒド
    page.wait_for_timeout(400)

    page.screenshot(path=str(OUT / "screenshot-mobile-1.png"), full_page=False)
    print("  saved: screenshot-mobile-1.png")
    context.close()


def main():
    print(f"Output: {OUT}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            take_desktop_shots(browser)
            take_mobile_shot(browser)
        finally:
            browser.close()
    print("Done.")


if __name__ == "__main__":
    main()
