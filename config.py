import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-ganti-nanti')
    
    # Database TiDB (dari .env)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://45UHE2q32UHTPze.root:O76oTRVfNoC6Virr@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/Absensi')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cloudinary (dari .env)
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
    
    # Resend API (dari .env)
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    
    # Email Sender (dari .env)
    EMAIL_FROM = os.environ.get('EMAIL_FROM', 'Absensi Kantor <onboarding@resend.dev>')
    
    # Frontend URL (dari .env)
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')
