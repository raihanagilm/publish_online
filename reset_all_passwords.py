"""
Skrip untuk reset password semua user di database ke hash yang valid (Werkzeug).
Jalankan SEKALI untuk memperbaiki password_hash yang corrupt/kosong.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from backend import create_app as backend_create_app
from backend.models import db, User

app = backend_create_app()

# Password default untuk setiap role (bisa diubah di sini)
DEFAULT_ADMIN_PASSWORD = 'Admin123!'
DEFAULT_KARYAWAN_PASSWORD = 'Karyawan123!'

with app.app_context():
    users = User.query.all()
    if not users:
        print("Tidak ada user di database.")
    else:
        print(f"Ditemukan {len(users)} user:")
        for u in users:
            if u.role == 'admin':
                pw = DEFAULT_ADMIN_PASSWORD
            else:
                pw = DEFAULT_KARYAWAN_PASSWORD
            u.set_password(pw)
            print(f"  [RESET] {u.role} | username={u.username} | password={pw}")
        
        db.session.commit()
        print("\n✅ Semua password berhasil di-reset!")
        print(f"   Admin     => password: {DEFAULT_ADMIN_PASSWORD}")
        print(f"   Karyawan  => password: {DEFAULT_KARYAWAN_PASSWORD}")
