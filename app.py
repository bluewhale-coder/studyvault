from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = 'vijaykumarsa321'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'
db = SQLAlchemy(app)

# --- Cloudinary Config ---
cloudinary.config(
    cloud_name='dxifrfyac',
    api_key='231573691677745',
    api_secret='mfKcIpK1N12gs7JAv0tihJfS2Go',
    secure=True
)

# --- Upload Folder Paths ---
BASE = os.path.dirname(__file__)
NOTES_FOLDER = os.path.join(BASE, 'uploads/notes')
QP_FOLDER = os.path.join(BASE, 'uploads/qp')
os.makedirs(NOTES_FOLDER, exist_ok=True)
os.makedirs(QP_FOLDER, exist_ok=True)

# --- Allowed file types ---
ALLOWED = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

# --- Models (Only Gallery Uses DB) ---
class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300))
    description = db.Column(db.String(255))
    public_id = db.Column(db.String(200))

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        if u == 'admin' and p == 'admin123':
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))
        elif u == 'student' and p == 'student123':
            session['role'] = 'student'
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', role=session['role'])

@app.route('/qp', methods=['GET', 'POST'])
def qp():
    if request.method == 'POST' and session.get('role') == 'admin':
        f = request.files['file']
        y = request.form['year']
        s = request.form.get('subject')
        if not s:
            flash("Subject is required", "warning")
            return redirect(url_for('qp'))

        if f and allowed_file(f.filename):
            fn = secure_filename(f.filename)
            public_id = f"{y}_{s.replace(' ', '_')}_{fn}"
            cloudinary.uploader.upload(f, resource_type="raw", public_id=public_id)
            flash("Question Paper uploaded!", "success")
            return redirect(url_for('qp'))

    result = cloudinary.Search().expression("resource_type:raw").sort_by("created_at", "desc").execute()
    files = result.get("resources", [])
    return render_template('qp.html', files=files, role=session.get('role'))

@app.route('/delete_qp_cloud', methods=['POST'])
def delete_qp_cloud():
    if session.get('role') != 'admin':
        return redirect(url_for('qp'))

    public_id = request.form.get('public_id')
    if public_id:
        cloudinary.uploader.destroy(public_id, resource_type="raw")
        flash("QP deleted from Cloudinary!", "success")
    return redirect(url_for('qp'))

# ----- Gallery -----
@app.route('/gallery')
def gallery():
    imgs = Gallery.query.all()
    return render_template('gallery.html', images=imgs)

@app.route('/upload_gallery', methods=['POST'])
def upload_gallery():
    file = request.files['image']
    description = request.form['description']
    if file:
        result = cloudinary.uploader.upload(file)
        new_img = Gallery(filename=result['secure_url'], description=description, public_id=result['public_id'])
        db.session.add(new_img)
        db.session.commit()
        flash("Image uploaded!", "success")
        return redirect(url_for('gallery'))
    return "No image selected"

@app.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    image = Gallery.query.get(image_id)
    if image and image.public_id:
        cloudinary.uploader.destroy(image.public_id)
        db.session.delete(image)
        db.session.commit()
        flash("Image deleted!", "success")
    return redirect(url_for('gallery'))

# ----- Skills -----
@app.route('/skills')
def skills():
    links = [
        ('GeeksForGeeks', 'https://geeksforgeeks.org'),
        ('LeetCode', 'https://leetcode.com'),
        ('HackerRank', 'https://hackerrank.com'),
        ('Codeforces', 'https://codeforces.com')
    ]
    return render_template('skills.html', links=links)

# ----- App Runner -----
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)