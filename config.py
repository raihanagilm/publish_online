import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-ganti-nanti')
    
    # 1. Ambil URL Database (Raw string untuk parsing manual di backend)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL wajib diisi di .env")

    # Konfigurasi lain
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'Absensi Kantor <onboarding@resend.dev>')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')