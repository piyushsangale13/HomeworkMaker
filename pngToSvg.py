import os
import shutil
import handwrite

# Input and output folders
image_dir = "images"
output_svg_dir = "svgs"
output_bmp_dir = "bmps"


# Make sure output folder exists
os.makedirs(output_svg_dir, exist_ok=True)
# Make sure output folder exists
os.makedirs(output_bmp_dir, exist_ok=True)

# 1. Convert PNG files
handwrite.PNGtoSVG().convert(image_dir)

# 2. Move all generated SVG files to output folder
for filename in os.listdir(image_dir):
    if filename.endswith(".svg"):
        src_path = os.path.join(image_dir, filename)
        dest_path = os.path.join(output_svg_dir, filename)
        shutil.move(src_path, dest_path)

print("SVG files have been moved to", output_svg_dir)

# 2. Move all generated SVG files to output folder
for filename in os.listdir(image_dir):
    if filename.endswith(".bmp"):
        src_path = os.path.join(image_dir, filename)
        dest_path = os.path.join(output_bmp_dir, filename)
        shutil.move(src_path, dest_path)

print("SVG files have been moved to", output_bmp_dir)


