from flask import Flask, request, send_file, render_template_string
import os
import shutil
from build_font_svg_3 import build_font

app = Flask(__name__)

UPLOAD_FOLDER = "svgs"
FONT_FILE = "master_ttf\MyHandwriting.ttf"
TEMPLATE_FILE = "handwriting_template.pdf"
# Make sure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
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
    """)

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

if __name__ == "__main__":
    app.run(debug=True)
