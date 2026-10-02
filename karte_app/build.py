"""アプリ本体のHTMLと vendor/xlsx.full.min.js を、それぞれ1つのHTMLファイルにまとめるスクリプト。

使い方:  python karte_app/build.py
できあがるファイル(どちらもファイル1つだけで動きます):
  karte_app/写真カルテ作成.html  … karte_src.html から作る(決まった様式のカルテ)
  karte_app/汎用カルテ作成.html  … generic_src.html から作る(表の形を自由に変えられるカルテ)
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent          # このスクリプトがあるフォルダ
LIB = HERE / "vendor" / "xlsx.full.min.js"      # Excel読み込み用の部品(SheetJS)
TAG = '<script src="vendor/xlsx.full.min.js"></script>'

# (元になるHTML, できあがるHTML) の組み合わせ
TARGETS = [
    ("karte_src.html", "写真カルテ作成.html"),
    ("generic_src.html", "汎用カルテ作成.html"),
]


def build_one(src_name: str, out_name: str, lib: str) -> None:
    """元のHTMLの <script src=...> の部分を、部品の中身に置き換えて保存する。"""
    src = HERE / src_name
    out = HERE / out_name
    html = src.read_text(encoding="utf-8")
    if TAG not in html:
        raise SystemExit(f"{src.name} に {TAG} が見つかりません")
    out.write_text(html.replace(TAG, "<script>\n" + lib + "\n</script>"), encoding="utf-8")
    print(f"作成しました: {out}  ({out.stat().st_size // 1024} KB)")


def build() -> None:
    """TARGETS にあるすべてのHTMLを作る。"""
    lib = LIB.read_text(encoding="utf-8")
    for src_name, out_name in TARGETS:
        build_one(src_name, out_name, lib)


if __name__ == "__main__":
    build()
