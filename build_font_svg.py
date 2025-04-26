import os
from svgpathtools import svg2paths
from svgpathtools import Line, QuadraticBezier, CubicBezier
from ufoLib2 import Font
from fontmake.font_project import FontProject

# Settings
IMAGE_FOLDER   = "svgs"  # Folder containing SVGs
FONT_NAME      = "MyHandwriting"
OUTPUT_STYLE   = "Regular"
USE_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
VARIANTS       = 3

def interpolate(p1, p2, t):
    """ Interpolate between two points p1 and p2 by a scalar t. """
    x1, y1 = p1
    x2, y2 = p2
    return (x1 * (1 - t) + x2 * t, y1 * (1 - t) + y2 * t)

def subdivide_cubic(p0, p1, p2, p3, steps=8):
    """ Subdivide a cubic Bezier curve into smaller segments for smoother results. """
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        # Subdivide cubic bezier curve by subdividing the 4 points
        p01 = interpolate(p0, p1, t)
        p12 = interpolate(p1, p2, t)
        p23 = interpolate(p2, p3, t)
        p012 = interpolate(p01, p12, t)
        p123 = interpolate(p12, p23, t)
        p0123 = interpolate(p012, p123, t)
        curve_points.append(p0123)
    return curve_points

def subdivide_quadratic(p0, p1, p2, steps=8):
    """ Subdivide a quadratic Bezier curve into smaller segments for smoother results. """
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        # Subdivide quadratic bezier curve
        p01 = interpolate(p0, p1, t)
        p12 = interpolate(p1, p2, t)
        p012 = interpolate(p01, p12, t)
        curve_points.append(p012)
    return curve_points

def svg_to_glyph(glyph, svg_path, scale_factor=0.8):
    """
    Converts SVG path data to a glyph in the UFO format.
    """
    # Parse SVG file and get paths
    paths, _ = svg2paths(svg_path)

    # Initialize pen for drawing the glyph
    pen = glyph.getPen()
    bounding_box = None  # To store the bounding box of the glyph

    for path in paths:
        first = True
        for segment in path:
            if isinstance(segment, Line):
                # Handle straight lines
                for point in segment:
                    x, y = point.real, point.imag
                    # Scale coordinates if needed
                    x *= scale_factor
                    y *= scale_factor

                    # Update bounding box
                    if bounding_box is None:
                        bounding_box = (x, y, x, y)
                    else:
                        min_x, min_y, max_x, max_y = bounding_box
                        bounding_box = (
                            min(min_x, x),
                            min(min_y, y),
                            max(max_x, x),
                            max(max_y, y)
                        )

                    # Draw the points in the glyph
                    if first:
                        pen.moveTo((x, y))
                        first = False
                    else:
                        pen.lineTo((x, y))

            elif isinstance(segment, QuadraticBezier):
                # Handle quadratic Bezier curves (with subdivision)
                p0 = segment.start
                p1 = segment.control
                p2 = segment.end
                p0x, p0y = p0.real * scale_factor, p0.imag * scale_factor
                p1x, p1y = p1.real * scale_factor, p1.imag * scale_factor
                p2x, p2y = p2.real * scale_factor, p2.imag * scale_factor

                # Subdivide the curve into smaller segments for smoother results
                curve_points = subdivide_quadratic((p0x, p0y), (p1x, p1y), (p2x, p2y), steps=16)

                # Draw the subdivided quadratic curve
                if first:
                    pen.moveTo(curve_points[0])
                    first = False
                for point in curve_points[1:]:
                    pen.lineTo(point)

            elif isinstance(segment, CubicBezier):
                # Handle cubic Bezier curves (with subdivision)
                p0 = segment.start
                p1 = segment.control1
                p2 = segment.control2
                p3 = segment.end
                p0x, p0y = p0.real * scale_factor, p0.imag * scale_factor
                p1x, p1y = p1.real * scale_factor, p1.imag * scale_factor
                p2x, p2y = p2.real * scale_factor, p2.imag * scale_factor
                p3x, p3y = p3.real * scale_factor, p3.imag * scale_factor

                # Subdivide the curve into smaller segments for smoother results
                curve_points = subdivide_cubic((p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y), steps=16)

                # Draw the subdivided cubic curve
                if first:
                    pen.moveTo(curve_points[0])
                    first = False
                for point in curve_points[1:]:
                    pen.lineTo(point)

        pen.closePath()

    # Set width based on bounding box
    if bounding_box:
        min_x, min_y, max_x, max_y = bounding_box
        width = 200  # Glyph width is the difference in x-coordinates
        # Add some padding to avoid overlap between glyphs
        padding = 500  # You can adjust this value as needed
        glyph.width = int(width + padding)  # Add padding to the width to prevent overlap

def build_font():
    ufo = Font()
    ufo.info.familyName   = FONT_NAME
    ufo.info.styleName    = OUTPUT_STYLE
    ufo.info.unitsPerEm   = 1000
    ufo.info.ascender     = 800
    ufo.info.descender    = -200

    feature_lines = []

    for ch in USE_CHARACTERS:
        alt_names = []

        for i in range(1, VARIANTS + 1):
            fn   = f"{ch}{i}.svg"
            path = os.path.join(IMAGE_FOLDER, fn)
            if not os.path.exists(path):
                print(f"❌ Missing {fn}")
                continue

            # Default glyph is 'a', alternates are 'a.alt1', 'a.alt2'
            glyph_name = ch if i == 1 else f"{ch}.alt{i-1}"
            glyph = ufo.newGlyph(glyph_name)
            if i == 1:
                glyph.unicodes = [ord(ch)]

            # Create the glyph using SVG
            svg_to_glyph(glyph, path)
            print(f"✅ Added {glyph_name}")

            if i > 1:
                alt_names.append(glyph_name)

        # Add one substitution line per alternate
        for alt in alt_names:
            feature_lines.append(f"sub {ch}' by {alt};")

    # Write the OpenType `calt` feature
    ufo.features.text = (
        "feature calt {\n    " +
        "\n    ".join(feature_lines) +
        "\n} calt;\n"
    )

    # Save UFO and compile to TTF
    ufo_path = f"{FONT_NAME}.ufo"
    ufo.save(ufo_path)

    project = FontProject()
    project.build_ttfs([ufo])
    print(f"\n🎉 Done — {FONT_NAME}-Regular.ttf generated")

if __name__ == "__main__":
    build_font()
