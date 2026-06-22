import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-ganti-nanti')
    
    # Database TiDB (dengan SSL)
    db_user = "45UHE2q32UHTPze.root"
    db_pass = "O76oTRVfNoC6Virr"
    db_host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
    db_port = "4000"
    db_name = "Absensi"
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfigurasi SSL untuk PyMySQL
    MYSQL_SSL_CA = '/etc/ssl/certs/ca-certificates.crt'
    MYSQL_SSL_CERT = None
    MYSQL_SSL_KEY = None
    
    # Cloudinary
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', 'cloudinary://884765233771594:qOYvn2w1TsW_ipwEzhgqB8RRTKE@daknwopl3')
    
    # Resend API
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', 're_XUbJjQoc_EQLWRddD2DgQLvkgYyrwGEU9')
