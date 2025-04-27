from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_template(characters="abcdefghijklmnopqrstuvwxyz", variants=3):
    c = canvas.Canvas("handwriting_template.pdf", pagesize=A4)
    width, height = A4
    margin = 40
    grid_cols = 6  # Number of boxes in one row
    grid_w = (width - 2 * margin) / grid_cols
    grid_h = 100  # Height of each box
    square_size = grid_h * 0.6  # Size of the square (60% of grid height)
    square_margin = (grid_h - square_size) / 2  # To center the square in the box
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

            # Draw the outer rectangle for the grid box
            c.rect(x, y - grid_h, grid_w, grid_h)

            # Draw the centered square inside the box
            square_x = x + (grid_w - square_size) / 2
            square_y = y - grid_h + square_margin
            c.rect(square_x, square_y, square_size, square_size)

            # Draw 3 faint horizontal lines inside the square
            line_count = 2
            line_spacing = square_size / (line_count + 1)  # Divide the square into 4 parts

            # Set faint color for the lines (a very light gray, close to white)
            c.setStrokeColorRGB(0.9, 0.9, 0.9)  # Light gray color (faint)

            for i in range(line_count):
                # Draw faint lines evenly spaced inside the square
                line_y = square_y + (i + 1) * line_spacing  # (i + 1) avoids the base and starts inside
                c.line(square_x, line_y, square_x + square_size, line_y)

            # Reset the stroke color to black for the bottom line (square's base) and the label
            c.setStrokeColorRGB(0, 0, 0)  # Black color for the grid, box, and label

            # Draw the bottom line of the square (the base, which should not be faint)
            bottom_line_y = square_y + square_size
            c.line(square_x, bottom_line_y, square_x + square_size, bottom_line_y)

            # Draw the label above the square
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
