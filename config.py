import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY wajib diisi di .env")

    # 1. Ambil URL Database (tanpa parameter ssl di belakangnya)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL wajib diisi di .env")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 2. Konfigurasi SSL Khusus untuk TiDB Cloud via SQLAlchemy
    # Kita inject parameter 'ssl' ke dalam opsi engine
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {
            "ssl": {
                "ca": None,          # Gunakan CA default sistem atau set path file jika punya
                "check_hostname": False, # Kadang perlu dimatikan jika hostname verification gagal
                "verify_mode": 1     # 1 = CERT_REQUIRED (Wajib SSL)
            }
        }
    }
    
    # Konfigurasi lain
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'Absensi Kantor <onboarding@resend.dev>')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')