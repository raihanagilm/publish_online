import os
from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
from models import db
from functools import wraps

load_dotenv()


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
    
    # Konfigurasi database dari environment variable
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///absensi.db')
    if db_url.startswith('mysql://'):
        db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-ganti-nanti')
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session timeout 1 jam
    
    # Inisialisasi ekstensi
    db.init_app(app)
    
    # Inisialisasi Flask-Login
    from flask_login import LoginManager, current_user
    from models import User
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
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
    
    # Buat tabel database jika belum ada
    with app.app_context():
        db.create_all()
    
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
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('karyawan.dashboard'))
        return redirect(url_for('auth.login'))

    return app