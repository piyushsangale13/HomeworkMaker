from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output_path = 'static/output.png'

    if request.method == 'POST':
        text = request.form['text']
        font_path = 'master_ttf\MyHandwriting.ttf'
        font_size = 40

        # Create a blank image
        img = Image.new('RGB', (1200, 800), color='white')
        draw = ImageDraw.Draw(img)

        # Load handwriting-like font
        font = ImageFont.truetype(font_path, font_size)

        # Draw text line by line
        x, y = 40, 40
        line_height = font_size + 20
        for line in text.split('\n'):
            draw.text((x, y), line, font=font, fill='black')
            y += line_height

        img.save(output_path)

        return render_template('index.html', output_image=output_path)

    return render_template('index.html', output_image=None)

@app.route('/download')
def download():
    return send_file('static/output.png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
