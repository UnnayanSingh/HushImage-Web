from flask import Flask, render_template, request, redirect, session, flash, send_file
from markupsafe import Markup
import MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash
from config import SECRET_KEY, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from stegano_utils import hide_message_in_image, reveal_message_from_image
import uuid
import os
import csv
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Flask app setup
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Uploads folder
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database connection (using config values from .env)
db = MySQLdb.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWORD,
    db=MYSQL_DB
)
cursor = db.cursor()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
        result = cursor.fetchone()
        if result and check_password_hash(result[1], password):
            session['user_id'] = result[0]
            session['username'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        try:
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password))
            db.commit()
            flash('Registered successfully! Please log in.')
            return redirect('/login')
        except:
            flash('Username already exists.')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'])

@app.route('/hide', methods=['GET', 'POST'])
def hide():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        uploaded_file = request.files['image']
        message = request.form['message']
        password = request.form['password']
        custom_filename = request.form['custom_filename'].strip().replace(' ', '_')

        if uploaded_file.filename == '' or not message or not password or not custom_filename:
            flash('All fields are required.')
            return redirect('/hide')

        filename = str(uuid.uuid4()) + "_" + uploaded_file.filename
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded_file.save(input_path)

        username = session['username'].replace(' ', '_')
        timestamp = int(time.time())
        output_filename = f"{username}_{custom_filename}_{timestamp}.png"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        try:
            hide_message_in_image(input_path, message, password, output_path)

            if os.path.exists(input_path):
                os.remove(input_path)

            relative_path = f'static/uploads/{output_filename}'
            cursor.execute(
                "INSERT INTO messages (user_id, encrypted_msg, image_path) VALUES (%s, %s, %s)",
                (session['user_id'], "Encrypted in image", relative_path)
            )
            db.commit()

            download_link = f'<a href="/{relative_path}" download>📥 Click here to download</a>'
            flash(Markup(f'Message hidden successfully! {download_link}'), 'success')
        except Exception as e:
            flash(str(e), 'danger')

        return redirect('/hide')

    return render_template('hide_message.html')

@app.route('/reveal', methods=['GET', 'POST'])
def reveal():
    if 'user_id' not in session:
        return redirect('/login')

    decrypted_message = None
    image_options = []

    cursor.execute("SELECT image_path FROM messages WHERE user_id=%s ORDER BY timestamp DESC", (session['user_id'],))
    image_options = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        image_name = request.form.get('image_name')
        password = request.form['password']

        if not image_name or not password:
            flash('Both image and password are required.')
            return redirect('/reveal')

        image_path = os.path.join(app.root_path, image_name)

        try:
            decrypted_message = reveal_message_from_image(image_path, password)
        except Exception as e:
            flash(f'Error: {str(e)}')

    return render_template('reveal_message.html', message=decrypted_message, images=image_options)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute("SELECT image_path, timestamp FROM messages WHERE user_id=%s ORDER BY timestamp DESC", (session['user_id'],))
    records = cursor.fetchall()
    return render_template('history.html', records=records)

@app.route('/export/csv')
def export_csv():
    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute("SELECT image_path, timestamp FROM messages WHERE user_id=%s", (session['user_id'],))
    records = cursor.fetchall()

    filename = f"message_history_{int(time.time())}.csv"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Image", "Timestamp"])
        for row in records:
            writer.writerow([os.path.basename(row[0]), row[1]])

    return send_file(filepath, as_attachment=True)

@app.route('/export/pdf')
def export_pdf():
    if 'user_id' not in session:
        return redirect('/login')

    cursor.execute("SELECT image_path, timestamp FROM messages WHERE user_id=%s", (session['user_id'],))
    records = cursor.fetchall()

    filename = f"message_history_{int(time.time())}.pdf"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Message History Report - {session['username']}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Total Messages: {len(records)}")

    y = height - 110
    for row in records:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, os.path.basename(row[0]))
        c.drawString(300, y, str(row[1]))
        y -= 20

    c.save()
    return send_file(filepath, as_attachment=True)

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        current_pw = request.form['current_password']
        new_pw = request.form['new_password']

        cursor.execute("SELECT password_hash FROM users WHERE id=%s", (session['user_id'],))
        result = cursor.fetchone()

        if result and check_password_hash(result[0], current_pw):
            new_hash = generate_password_hash(new_pw)
            cursor.execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, session['user_id']))
            db.commit()
            flash("Password updated successfully!", "success")
        else:
            flash("Current password is incorrect.", "danger")

        return redirect('/change-password')

    return render_template('change_password.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
