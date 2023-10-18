from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from PIL import Image
from flask import send_file
import secrets
import string

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Generate a random secret key
def generate_secret_key(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(secrets.choice(characters) for _ in range(length))
    return secret_key

# Set the Flask app secret key
app.secret_key = generate_secret_key()


# Function to convert images to PDF
def images_to_pdf(images, pdf_name):
    try:
        pdf = Image.open(images[0])
        pdf.save(pdf_name, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
        return True, "Images successfully converted to PDF."
    except Exception as e:
        return False, f"Conversion failed. Error: {str(e)}"

# Route for the home page
@app.route('/')
def index():
    return render_template('img2pdf.html')

# Route to upload images and convert to PDF
@app.route('/convert', methods=['POST'])
def convert():
    if 'images' not in request.files:
        flash('No file part')
        return redirect(request.url)

    uploaded_images = request.files.getlist('images')
    if len(uploaded_images) == 0:
        flash('No selected file')
        return redirect(request.url)

    image_paths = []
    for image in uploaded_images:
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), filename)
            image.save(image_path)
            image_paths.append(image_path)

    pdf_name = os.path.join(app.config['UPLOAD_FOLDER'], 'converted.pdf')
    success, message = images_to_pdf(image_paths, pdf_name)

    if success:
        return render_template('img2pdfsuccess.html', message=message)
    else:
        return render_template('img2pdferror.html', message=message)
    # Route to download the converted PDF
@app.route('/download-pdf')
def download_pdf():
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted.pdf')
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
