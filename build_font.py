import os
import shutil
from svgpathtools import svg2paths
from svgpathtools import Line, QuadraticBezier, CubicBezier
from ufoLib2 import Font
from fontmake.font_project import FontProject

# Settings
IMAGE_FOLDER   = "svgs"
FONT_NAME      = "MyHandwriting"
OUTPUT_STYLE   = "Regular"
USE_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_RANGE = "[a b c d e f g h i j k l m n o p q r s t u v w x y z]"
VARIANTS       = 3

def interpolate(p1, p2, t):
    return (p1[0]*(1-t) + p2[0]*t, p1[1]*(1-t) + p2[1]*t)

def subdivide_cubic(p0, p1, p2, p3, steps=8):
    return [interpolate(
                interpolate(
                    interpolate(p0, p1, t),
                    interpolate(p1, p2, t),
                    t),
                interpolate(
                    interpolate(p1, p2, t),
                    interpolate(p2, p3, t),
                    t),
                t
            ) for t in [i/steps for i in range(steps+1)]]

def subdivide_quadratic(p0, p1, p2, steps=8):
    return [interpolate(
                interpolate(p0, p1, t),
                interpolate(p1, p2, t),
                t
            ) for t in [i/steps for i in range(steps+1)]]

def svg_to_glyph(glyph, svg_path):
    paths, _ = svg2paths(svg_path)
    if not paths:
        print(f"⚠️ No paths found in {svg_path}")
        return

    min_x = float('inf')
    max_x = float('-inf')
    for path in paths:
        for segment in path:
            for point in segment:
                x, y = point.real, point.imag
                min_x = min(min_x, x)
                max_x = max(max_x, x)

    width = max_x - min_x
    height = 1000
    
    if width == 0 or height == 0:
        print(f"⚠️ Empty path in {svg_path}")
        return

    pen = glyph.getPen()
    offset = complex(-min_x, -height/3)
    for path in paths:
        first = True
        for segment in path:
            segment = segment.translated(offset)

            if isinstance(segment, Line):
                for point in segment:
                    x, y = point.real, point.imag
                    if first:
                        pen.moveTo((x, y))
                        first = False
                    else:
                        pen.lineTo((x, y))

            elif isinstance(segment, QuadraticBezier):
                p0 = segment.start
                p1 = segment.control
                p2 = segment.end
                points = subdivide_quadratic((p0.real, p0.imag), (p1.real, p1.imag), (p2.real, p2.imag), steps=32)
                if first:
                    pen.moveTo(points[0])
                    first = False
                for pt in points[1:]:
                    pen.lineTo(pt)

            elif isinstance(segment, CubicBezier):
                p0 = segment.start
                p1 = segment.control1
                p2 = segment.control2
                p3 = segment.end
                points = subdivide_cubic((p0.real, p0.imag), (p1.real, p1.imag), (p2.real, p2.imag), (p3.real, p3.imag), steps=16)
                if first:
                    pen.moveTo(points[0])
                    first = False
                for pt in points[1:]:
                    pen.lineTo(pt)

        pen.closePath()

    glyph.width = int(width + 20)

def build_font():

    if os.path.exists('master_ttf'):
        shutil.rmtree('master_ttf')
        print("Deleted existing 'master_ttf' folder.")

    if os.path.exists(f"{FONT_NAME}.ufo"):
        shutil.rmtree(f"{FONT_NAME}.ufo")
        print(f"Deleted existing '{FONT_NAME}.ufo' folder.")
        
    ufo = Font()
    ufo.info.familyName   = FONT_NAME
    ufo.info.styleName    = OUTPUT_STYLE
    ufo.info.unitsPerEm   = 1000
    ufo.info.ascender     = 667
    ufo.info.descender    = -333

    feature_lines = []

    for ch in USE_CHARACTERS:
        alt_names = []

        for i in range(1, VARIANTS + 1):
            fn   = f"{ch}{i}.svg"
            path = os.path.join(IMAGE_FOLDER, fn)
            if not os.path.exists(path):
                print(f"❌ Missing {fn}")
                continue

            glyph_name = ch if i == 1 else f"{ch}.alt{i-1}"
            glyph = ufo.newGlyph(glyph_name)
            if i == 1:
                glyph.unicodes = [ord(ch)]

            svg_to_glyph(glyph, path)
            print(f"✅ Added {glyph_name}")

            if i > 1:
                alt_names.append(glyph_name)

        for alt in alt_names:
            feature_lines.append(f"sub {ALPHABET_RANGE} {ch}' by {alt};")
         
    ufo.features.text = (
        "feature calt {\n    " +
        "\n    ".join(feature_lines) +
        "\n} calt;\n"
    )

    space = ufo.newGlyph("space")
    space.unicodes = [ord(' ')]
    space.width = 500
    print("✅ Added wide space glyph")

    ufo_path = f"{FONT_NAME}.ufo"
    ufo.save(ufo_path)

    project = FontProject()
    project.build_ttfs([ufo])
    print(f"\n🎉 Done — {FONT_NAME}-Regular.ttf generated")

if __name__ == "__main__":
    build_font()
