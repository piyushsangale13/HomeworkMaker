import os
import shutil
import handwrite

image_dir = "images"
output_svg_dir = "svgs"
output_bmp_dir = "bmps"

os.makedirs(output_svg_dir, exist_ok=True)
os.makedirs(output_bmp_dir, exist_ok=True)

handwrite.PNGtoSVG().convert(image_dir)

for filename in os.listdir(image_dir):
    if filename.endswith(".svg"):
        src_path = os.path.join(image_dir, filename)
        dest_path = os.path.join(output_svg_dir, filename)
        shutil.move(src_path, dest_path)

print("SVG files have been moved to", output_svg_dir)

for filename in os.listdir(image_dir):
    if filename.endswith(".bmp"):
        src_path = os.path.join(image_dir, filename)
        dest_path = os.path.join(output_bmp_dir, filename)
        shutil.move(src_path, dest_path)

print("SVG files have been moved to", output_bmp_dir)