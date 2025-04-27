#!/usr/bin/env fontforge
import fitz               # PyMuPDF
from PIL import Image, ImageDraw
import os

def extract_letters(pdf_path="handwriting_template_filled.pdf",
                    output_dir="images",
                    dpi=300,
                    debug=False):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    characters = "abcdefghijklmnopqrstuvwxyz"
    variants = 3

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # PDF page size in points
        pw_pt, ph_pt = page.rect.width, page.rect.height

        # Rasterize page at desired DPI
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Optional debug drawer
        if debug:
            draw = ImageDraw.Draw(img)

        # scale factor from points → pixels
        scale = pix.width / pw_pt

        # Template layout parameters (in points)
        margin_pt = 40
        grid_cols = 6  # Number of boxes in one row
        grid_w_pt = (pw_pt - 2 * margin_pt) / grid_cols
        grid_h_pt = 100  # Height of each box
        square_size_pt = grid_h_pt * 0.6  # Size of the square (60% of the box height)
        square_margin_pt = (grid_h_pt - square_size_pt) / 2  # To center the square inside the grid
        gap_pt = 20
        rows_per_page = int((ph_pt - 2 * margin_pt) // (grid_h_pt + gap_pt))

        box_idx = page_num * (grid_cols * rows_per_page)
        for row in range(rows_per_page):
            for col in range(grid_cols):
                if box_idx >= len(characters) * variants:
                    break

                ch = characters[box_idx // variants]
                var = (box_idx % variants) + 1
                label = f"{ch}{var}"

                # Compute box in PDF points
                x0_pt = margin_pt + col * grid_w_pt
                y1_pt = ph_pt - margin_pt - row * (grid_h_pt + gap_pt)   # upper y
                y0_pt = y1_pt - grid_h_pt                                # lower y

                # Compute the square's position inside the box
                square_x0_pt = x0_pt + (grid_w_pt - square_size_pt) / 2
                square_y0_pt = y1_pt - square_margin_pt - square_size_pt

                # Convert to pixels
                x0_px = int(x0_pt * scale)
                y0_px = int((ph_pt - y1_pt) * scale)  # top in image coords
                x1_px = int((x0_pt + grid_w_pt) * scale)
                y1_px = int((ph_pt - y0_pt) * scale)  # bottom in image coords

                square_x0_px = int(square_x0_pt * scale)
                square_y0_px = int((ph_pt - square_y0_pt) * scale)
                square_x1_px = int((square_x0_pt + square_size_pt) * scale)
                square_y1_px = int((ph_pt - (square_y0_pt + square_size_pt)) * scale)

                # Ensure square_y0_px <= square_y1_px (fix for the error)
                if square_y0_px > square_y1_px:
                    square_y0_px, square_y1_px = square_y1_px, square_y0_px

                # Optional debug drawer
                # if debug:
                #     draw.rectangle([square_x0_px, square_y0_px, square_x1_px, square_y1_px],
                #                    outline="blue", width=2)

                # Crop the square region
                crop = img.crop((square_x0_px + 3, square_y0_px + 3, square_x1_px - 3, square_y1_px - 3))
                crop.save(os.path.join(output_dir, f"{label}.png"))

                box_idx += 1

        if debug:
            img.save(os.path.join(output_dir, f"debug_page_{page_num+1}.png"))

    print(f"✅ Extracted {box_idx} images into `{output_dir}/`")

if __name__ == "__main__":
    # Turn debug=True the first time so you can open debug_page_1.png
    extract_letters(debug=True)
