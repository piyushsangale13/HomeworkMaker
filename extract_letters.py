import fitz
from PIL import Image, ImageDraw
import os

def extract_letters(pdf_path="handwriting_template_filled.pdf",
                    output_dir="images",
                    dpi=300):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    characters = "abcdefghijklmnopqrstuvwxyz"
    variants = 3

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pw_pt, ph_pt = page.rect.width, page.rect.height

        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        scale = pix.width / pw_pt

        margin_pt = 40
        grid_cols = 6
        grid_w_pt = (pw_pt - 2 * margin_pt) / grid_cols
        grid_h_pt = 100
        square_size_pt = grid_h_pt * 0.6
        square_margin_pt = (grid_h_pt - square_size_pt) / 2
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

                x0_pt = margin_pt + col * grid_w_pt
                y1_pt = ph_pt - margin_pt - row * (grid_h_pt + gap_pt)
                y0_pt = y1_pt - grid_h_pt

                square_x0_pt = x0_pt + (grid_w_pt - square_size_pt) / 2
                square_y0_pt = y1_pt - square_margin_pt - square_size_pt

                x0_px = int(x0_pt * scale)
                y0_px = int((ph_pt - y1_pt) * scale) 
                x1_px = int((x0_pt + grid_w_pt) * scale)
                y1_px = int((ph_pt - y0_pt) * scale) 

                square_x0_px = int(square_x0_pt * scale)
                square_y0_px = int((ph_pt - square_y0_pt) * scale)
                square_x1_px = int((square_x0_pt + square_size_pt) * scale)
                square_y1_px = int((ph_pt - (square_y0_pt + square_size_pt)) * scale)

                if square_y0_px > square_y1_px:
                    square_y0_px, square_y1_px = square_y1_px, square_y0_px
                
                crop = img.crop((square_x0_px + 3, square_y0_px + 3, square_x1_px - 3, square_y1_px - 3))
                crop.save(os.path.join(output_dir, f"{label}.png"))

                box_idx += 1

    print(f"✅ Extracted {box_idx} images into `{output_dir}/`")

if __name__ == "__main__":
    extract_letters()
