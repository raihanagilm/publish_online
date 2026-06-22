import os
import pymysql
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL').replace("mysql+pymysql://", "mysql://")
    # Parsing URL manual
    clean_url = db_url.replace("mysql://", "")
    parts = clean_url.split('@')
    user_pass = parts[0]
    host_db = parts[1]
    
    user, password = user_pass.split(':', 1)
    host_port, db_name = host_db.rsplit('/', 1)
    host, port = host_port.rsplit(':', 1)

    return pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor,
        ssl={'ca': None} # SSL tetap aktif
    )

# Decorator untuk proteksi halaman (harus login dulu)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def create_app():
    app = Flask(__name__, template_folder='frontend/templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-ganti-nanti')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # Cari user berdasarkan username
                    sql = "SELECT * FROM users WHERE username = %s"
                    cursor.execute(sql, (username,))
                    user = cursor.fetchone()

                    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                        # Password cocok, buat sesi
                        session['user_id'] = user['id']
                        session['username'] = user['username']
                        flash('Login berhasil!', 'success')
                        return redirect(url_for('dashboard')) # Redirect ke halaman utama setelah login
                    else:
                        flash('Username atau password salah.', 'danger')
            except Exception as e:
                flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            finally:
                conn.close()

        return render_template('auth/login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Anda telah logout.', 'info')
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def dashboard():
        return f"Halo, {session.get('username')}! Ini adalah halaman dashboard rahasia."

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)