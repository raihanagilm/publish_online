import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY wajib diisi di .env")

    # 1. Ambil URL Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL wajib diisi di .env")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 2. Konfigurasi SSL Khusus untuk TiDB Cloud via SQLAlchemy
    # TiDB Cloud memerlukan SSL, jadi kita set ssl_require=True
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {
            "ssl": {
                "ca": None,
                "check_hostname": False,
                "verify_mode": 0  # CERT_NONE - disable verification for simplicity
            }
        }
    }
    
    # Konfigurasi lain
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'Absensi Kantor <onboarding@resend.dev>')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')