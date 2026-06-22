import os
import pymysql
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
from functools import wraps

load_dotenv()


def get_db_connection():
    """Membuat koneksi database manual ke TiDB Cloud"""
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


def create_app():
    """
    Flask application factory.
    Semua konfigurasi dan registrasi blueprint ada di sini.
    """
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-ganti-nanti')
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session timeout 1 jam
    
    # Inisialisasi Flask-Login
    from flask_login import LoginManager
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        # Query user manual dari database
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE id = %s"
                cursor.execute(sql, (int(user_id),))
                user_data = cursor.fetchone()
                if user_data:
                    from models import User
                    user = User()
                    user.id = user_data['id']
                    user.username = user_data['username']
                    user.password_hash = user_data['password_hash']
                    user.role = user_data['role']
                    user.nama_lengkap = user_data.get('nama_lengkap', '')
                    user.email = user_data.get('email', '')
                    user.is_active = True
                    return user
        finally:
            conn.close()
        return None
    
    # Decorator untuk proteksi halaman (harus login dulu)
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                from flask import flash
                flash('Silakan login terlebih dahulu.', 'warning')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Import dan register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.admin import admin_bp
    from backend.routes.karyawan import karyawan_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(karyawan_bp)
    
    # Route utama - redirect berdasarkan role
    @app.route('/')
    @login_required
    def index():
        from flask import current_app
        # Cek role dari session atau query manual
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT role FROM users WHERE id = %s"
                cursor.execute(sql, (session.get('user_id'),))
                result = cursor.fetchone()
                if result and result['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif result:
                    return redirect(url_for('karyawan.dashboard'))
        finally:
            conn.close()
        return redirect(url_for('auth.login'))

    return app