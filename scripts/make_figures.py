"""Cover images (1120x560, Kaggle size) in Portuguese and English: docs/img/cover.png, cover.en.png.

    python scripts/make_figures.py      # after build.py; needs Pillow and the Inter font
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
BG, INK, MUTED, GRID = "#fdfdfc", "#111111", "#555555", "#e6e6e6"
NAMES, SURNAMES = "#2a78d6", "#1f9e89"
TEXT = {
    "pt": {"title": "Nomes e sobrenomes do Brasil",
           "sub": "{n} nomes · {s} sobrenomes · Censo 2010 (IBGE) · CNPJ · significados escritos por GPT",
           "left": "Nomes mais comuns (pessoas, Censo 2010)", "right": "Sobrenomes mais comuns (sócios no CNPJ)",
           "file": "cover.png", "mi": " mi", "mil": " mil", "dec": ","},
    "en": {"title": "Brazilian given names and surnames",
           "sub": "{n} names · {s} surnames · IBGE 2010 Census · CNPJ register · meanings written by GPT",
           "left": "Most common given names (people, 2010 Census)", "right": "Most common surnames (CNPJ partners)",
           "file": "cover.en.png", "mi": "M", "mil": "k", "dec": "."},
}


def font(weight: str, size: int):
    return ImageFont.truetype(FONT.format(weight), size)


def short(v: float, t: dict) -> str:
    if v >= 1e6:
        return f"{v / 1e6:.1f}".replace(".", t["dec"]) + t["mi"]
    return f"{v / 1e3:.0f}" + t["mil"]


def thousands(v: int, lang: str) -> str:
    return f"{v:,}".replace(",", "." if lang == "pt" else ",")


def panel(d, x0, y0, width, title, rows, color, t):
    d.text((x0, y0), title, font=font("SemiBold", 17), fill=INK)
    top = max(v for _, v in rows)
    label_w, bar_w = 108, width - 108 - 70
    for i, (name, v) in enumerate(rows):
        y = y0 + 38 + i * 36
        d.text((x0 + label_w - 10 - d.textlength(name, font=font("Regular", 16)), y + 3), name, font=font("Regular", 16), fill=INK)
        w = max(2, int(bar_w * v / top))
        d.rectangle((x0 + label_w, y + 4, x0 + label_w + w, y + 24), fill=color)
        d.text((x0 + label_w + w + 8, y + 5), short(v, t), font=font("Regular", 14), fill=MUTED)


def main() -> None:
    names = pd.read_parquet(ROOT / "data" / "nomes.parquet")
    surnames = pd.read_parquet(ROOT / "data" / "sobrenomes.parquet")
    top_names = names.nlargest(8, "ibge_frequency")[["name", "ibge_frequency"]].values.tolist()
    top_surnames = surnames.nlargest(8, "cnpj_partners")[["surname", "cnpj_partners"]].values.tolist()
    out = ROOT / "docs" / "img"
    out.mkdir(parents=True, exist_ok=True)
    for lang, t in TEXT.items():
        im = Image.new("RGB", (1120, 560), BG)
        d = ImageDraw.Draw(im)
        d.text((56, 52), t["title"], font=font("Bold", 42), fill=INK)
        d.text((56, 112), t["sub"].format(n=thousands(len(names), lang), s=thousands(len(surnames), lang)),
               font=font("Regular", 19), fill=MUTED)
        d.line((56, 158, 1064, 158), fill=GRID, width=1)
        panel(d, 56, 176, 500, t["left"], top_names, NAMES, t)
        panel(d, 590, 176, 474, t["right"], top_surnames, SURNAMES, t)
        d.text((56, 528), "github.com/CaiqueDourado", font=font("Regular", 15), fill=MUTED)
        im.save(out / t["file"])
    print("covers written to", out)


if __name__ == "__main__":
    main()
