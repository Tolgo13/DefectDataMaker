"""karte_src.html と vendor/xlsx.full.min.js を1つのHTMLファイルにまとめるスクリプト。

使い方:  python karte_app/build.py
できあがるファイル:  karte_app/写真カルテ作成.html (このファイル1つだけで動きます)
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent          # このスクリプトがあるフォルダ
SRC = HERE / "karte_src.html"                   # 元になるHTML
LIB = HERE / "vendor" / "xlsx.full.min.js"      # Excel読み込み用の部品(SheetJS)
OUT = HERE / "写真カルテ作成.html"              # できあがるHTML
TAG = '<script src="vendor/xlsx.full.min.js"></script>'


def build() -> None:
    """元のHTMLの <script src=...> の部分を、部品の中身に置き換えて保存する。"""
    html = SRC.read_text(encoding="utf-8")
    lib = LIB.read_text(encoding="utf-8")
    if TAG not in html:
        raise SystemExit(f"{SRC.name} に {TAG} が見つかりません")
    OUT.write_text(html.replace(TAG, "<script>\n" + lib + "\n</script>"), encoding="utf-8")
    print(f"作成しました: {OUT}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
