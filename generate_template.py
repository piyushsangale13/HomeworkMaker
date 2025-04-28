from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_template(characters="abcdefghijklmnopqrstuvwxyz", variants=3):
    c = canvas.Canvas("handwriting_template.pdf", pagesize=A4)
    width, height = A4
    margin = 40
    grid_cols = 6
    grid_w = (width - 2 * margin) / grid_cols
    grid_h = 100
    square_size = grid_h * 0.6
    square_margin = (grid_h - square_size) / 2
    grid_rows_per_page = int((height - 2 * margin) // (grid_h + 20))
    boxes_per_page = grid_cols * grid_rows_per_page

    total_boxes = len(characters) * variants
    pages_needed = (total_boxes + boxes_per_page - 1) // boxes_per_page

    box_index = 0

    for page in range(pages_needed):
        x = margin
        y = height - margin

        c.setFont("Helvetica", 10)

        for _ in range(boxes_per_page):
            if box_index >= total_boxes:
                break

            ch_index = box_index // variants
            var_index = (box_index % variants) + 1
            label = f"{characters[ch_index]}{var_index}"

            c.rect(x, y - grid_h, grid_w, grid_h)

            square_x = x + (grid_w - square_size) / 2
            square_y = y - grid_h + square_margin
            c.rect(square_x, square_y, square_size, square_size)

            line_count = 2
            line_spacing = square_size / (line_count + 1)
            
            c.setStrokeColorRGB(0.9, 0.9, 0.9)

            for i in range(line_count):
                line_y = square_y + (i + 1) * line_spacing
                c.line(square_x, line_y, square_x + square_size, line_y)

            c.setStrokeColorRGB(0, 0, 0)
            
            bottom_line_y = square_y + square_size
            c.line(square_x, bottom_line_y, square_x + square_size, bottom_line_y)

            c.drawString(x + 5, y - 15, label)

            x += grid_w
            if x + grid_w > width - margin:
                x = margin
                y -= grid_h + 20

            box_index += 1

        c.showPage()

    c.save()
    print("Template saved as handwriting_template.pdf")

if __name__ == "__main__":
    generate_template()
