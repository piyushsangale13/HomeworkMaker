from flask import Flask, request, send_file, render_template_string, url_for
import os
from PIL import Image, ImageDraw
import freetype
import uharfbuzz as hb
from build_font import build_font

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
    text = request.form.get('text', '').strip()
    if not text:
        return "Text is empty. <br><a href='/'>Go Back</a>"

    if not os.path.exists(FONT_FILE):
        return "Font not built yet. <br><a href='/'>Go Back</a>", 404

    face = freetype.Face(FONT_FILE)
    face.set_char_size(48 * 64)

    # HarfBuzz shaping
    font_bytes = open(FONT_FILE, 'rb').read()
    hb_blob = hb.Blob(font_bytes)
    hb_face = hb.Face(hb_blob)
    hb_font = hb.Font(hb_face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    features = {"calt": True}
    hb.shape(hb_font, buf, features)

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    # Calculate total width and height
    width = sum(pos.x_advance for pos in positions) // 64 + 40
    height = face.size.height // 64 + 40
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    pen_x, pen_y = 20, 20 + face.size.ascender // 64

    for info, pos in zip(infos, positions):
        glyph_index = info.codepoint
        face.load_glyph(glyph_index, freetype.FT_LOAD_RENDER)
        bitmap = face.glyph.bitmap
        top = face.glyph.bitmap_top
        left = face.glyph.bitmap_left

        glyph_image = Image.frombytes("L", (bitmap.width, bitmap.rows), bytes(bitmap.buffer))
        image.paste(Image.merge("RGB", (glyph_image,)*3), (pen_x + left, pen_y - top))

        pen_x += pos.x_advance // 64
        pen_y += pos.y_advance // 64


    image.save(RENDERED_IMAGE)
    return home()

if __name__ == "__main__":
    app.run(debug=True)
