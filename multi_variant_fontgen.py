# === multi_variant_fontgen.py ===
# New pipeline: extract from handwriting_template_filled.pdf
# 1. Use extract_letters.py to create images/a1.png ... z3.png
# 2. This script converts them to SVG, then builds a font with calt alternates

import os
import uuid
import json
import subprocess
from PIL import Image
from handwrite.pngtosvg import PNGtoSVG
import fontforge

# === SETTINGS ===
IMAGE_DIR = "images"  # input folder with a1.png, a2.png ... z3.png
OUTPUT_DIR = "output_fonts"
FONT_NAME = "MyHandwritingFont"
CONFIG = "default.json"  # optional config file (for metadata)
VARIANTS = 3
CHARS = "abcdefghijklmnopqrstuvwxyz"

# === 1. Convert all PNGs to BMP and SVG ===
def convert_all_pngs_to_svgs(image_dir):
    PNGtoSVG().convert(image_dir)

# === 2. Create .ttf with calt alternates ===
def convert_svgs_to_ttf(image_dir, outdir, font_name):
    font = fontforge.font()
    font.encoding = "UnicodeFull"
    font.familyname = font_name
    font.fontname = font_name.replace(" ", "") + "-Regular"
    font.fullname = font_name + " Regular"
    font.appendSFNTName("English (US)", "Family", font_name)
    font.appendSFNTName("English (US)", "Fullname", font.fullname)
    font.appendSFNTName("English (US)", "PostScriptName", font.fontname)
    font.appendSFNTName("English (US)", "SubFamily", "Regular")
    font.appendSFNTName("English (US)", "UniqueID", font.fullname + str(uuid.uuid4()))

    calt_rules = []

    for ch in CHARS:
        for i in range(1, VARIANTS + 1):
            img_id = f"{ch}{i}"
            svg_path = os.path.join(image_dir, img_id + ".svg")
            if not os.path.exists(svg_path):
                continue

            glyphname = ch if i == 1 else f"{ch}.alt{i-1}"
            codepoint = ord(ch) if i == 1 else -1

            g = font.createChar(codepoint, glyphname)
            g.importOutlines(svg_path)
            g.removeOverlap()
            g.correctDirection()

            if i > 1:
                calt_rules.append(f"  sub {ch}' by {glyphname};")

    # Add space
    space = font.createChar(32)
    space.width = 500

    # Add OpenType calt feature
    if calt_rules:
        feature_text = "feature calt {\n" + "\n".join(calt_rules) + "\n} calt;"
        fea_path = os.path.join(outdir, "features.fea")
        with open(fea_path, "w") as f:
            f.write(feature_text)
        font.mergeFeature(fea_path)

    # Output final TTF
    os.makedirs(outdir, exist_ok=True)
    output_path = os.path.join(outdir, font_name + ".ttf")
    font.generate(output_path)
    print(f"\n✅ Font generated: {output_path}")

# === Main entrypoint ===
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    convert_all_pngs_to_svgs(IMAGE_DIR)
    convert_svgs_to_ttf(IMAGE_DIR, OUTPUT_DIR, FONT_NAME)
