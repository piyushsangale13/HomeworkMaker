from flask import Flask, request, send_file, render_template_string, url_for
import os
from PIL import Image, ImageDraw, ImageFont
from build_font import build_font  # Assumes you have this module

app = Flask(__name__)

UPLOAD_FOLDER = "svgs"
FONT_FILE = "master_ttf/MyHandwriting.ttf"
TEMPLATE_FILE = "handwriting_template.pdf"
RENDERED_IMAGE = "static/rendered.png"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

@app.route('/')
def home():
    rendered = os.path.exists(RENDERED_IMAGE)
    return render_template_string("""
    <!doctype html>
    <title>Font Builder</title>
    <h2>Download template</h2>
    <a href="/downloadTemplate">Download Template</a>
    
    <h1>Upload SVG Files</h1>
    <form method=post enctype=multipart/form-data action="/upload">
      <input type=file name=files multiple>
      <input type=submit value=Upload>
    </form>

    <h2>Or Build Font</h2>
    <form method=post action="/build">
      <input type=submit value="Build Font">
    </form>

    <h2>Download TTF</h2>
    <a href="/download">Download Font</a>

    <h2>Render Preview</h2>
    <form method=post action="/render">
      <textarea name="text" rows="4" cols="50" placeholder="Type your text here..."></textarea><br>
      <input type=submit value="Render">
    </form>

    {% if rendered %}
        <h3>Preview:</h3>
        <img src="{{ url_for('static', filename='rendered.png') }}" alt="Rendered Text"><br>
        <a href="{{ url_for('static', filename='rendered.png') }}" download>Download Image</a>
    {% endif %}
    """, rendered=rendered)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "No file part", 400

    files = request.files.getlist('files')

    for file in files:
        filename = file.filename
        if filename.endswith('.svg'):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

    return "✅ Uploaded successfully! <br><a href='/'>Go Back</a>"

@app.route('/build', methods=['POST'])
def build():
    build_font()
    return "🎉 Font built successfully! <br><a href='/'>Go Back</a>"

@app.route('/download')
def download():
    if os.path.exists(FONT_FILE):
        return send_file(FONT_FILE, as_attachment=True)
    else:
        return "Font not built yet. <br><a href='/'>Go Back</a>", 404

@app.route('/downloadTemplate')
def downloadTemplate():
    if os.path.exists(TEMPLATE_FILE):
        return send_file(TEMPLATE_FILE, as_attachment=True)
    else:
        return "Template not available. <br><a href='/'>Go Back</a>", 404

@app.route('/render', methods=['POST'])
def render_text():
    text = request.form.get('text', '')

    if not text.strip():
        return "Text is empty. <br><a href='/'>Go Back</a>"

    if not os.path.exists(FONT_FILE):
        return "Font not built yet. <br><a href='/'>Go Back</a>", 404

    font_size = 48
    try:
        font = ImageFont.truetype(FONT_FILE, font_size)
    except Exception as e:
        return f"Error loading font: {e}"

    # Create dummy image and get text bounding box
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Create image with padding
    img = Image.new("RGB", (text_width + 40, text_height + 40), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), text, font=font, fill="black")

    img.save(RENDERED_IMAGE)

    return home()


if __name__ == "__main__":
    app.run(debug=True)
