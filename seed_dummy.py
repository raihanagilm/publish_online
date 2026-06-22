import os
import pymysql
import bcrypt
import random
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
fake = Faker('id_ID') # Data dummy nama Indonesia

# --- KONFIGURASI KONEKSI (SAMA PERSIS DENGAN app.py) ---
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL').replace("mysql+pymysql://", "mysql://")
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
        ssl={'ca': None} 
    )

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Memulai pengisian data dummy...")

    try:
        # 1. Buat Admin
        admin_password = "admin123" # Password asli
        admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        sql_user = """
        INSERT INTO users (username, email, password_hash, role, nama_lengkap, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE username=username
        """
        
        # Insert Admin
        cursor.execute(sql_user, (
            'admin', 
            'admin@perusahaan.com', 
            admin_hash, 
            'admin', 
            'Administrator Utama', 
            datetime.now()
        ))
        print(f"[-] User Admin dibuat. Password: {admin_password}")

        # 2. Buat 5 Karyawan Dummy
        karyawan_password = "karyawan123" # Password asli sama untuk semua agar mudah tes
        karyawan_hash = bcrypt.hashpw(karyawan_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_ids = []
        
        for i in range(1, 6):
            username = f"karyawan{i}"
            email = f"karyawan{i}@perusahaan.com"
            nama = fake.name()
            
            cursor.execute(sql_user, (
                username, email, karyawan_hash, 'karyawan', nama, datetime.now()
            ))
            
            # Ambil ID user yang baru dibuat/diupdate
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            user_ids.append(result['id'])
            print(f"[-] User {username} ({nama}) dibuat. Password: {karyawan_password}")

        # 3. Buat Data Absensi Dummy untuk 7 hari terakhir
        sql_absen = """
        INSERT INTO absensi (user_id, tanggal, jam_masuk, jam_keluar, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        today = datetime.now().date()
        
        for uid in user_ids:
            for i in range(7): # 7 hari ke belakang
                tanggal = today - timedelta(days=i)
                
                # Random jam masuk (07:00 - 09:00)
                jam_masuk_dt = datetime.combine(tanggal, time(random.randint(7, 8), random.randint(0, 59)))
                # Random jam pulang (16:00 - 18:00)
                jam_keluar_dt = datetime.combine(tanggal, time(random.randint(16, 17), random.randint(0, 59)))
                
                status = random.choice(['hadir', 'hadir', 'hadir', 'terlambat', 'izin'])
                
                cursor.execute(sql_absen, (
                    uid,
                    tanggal,
                    jam_masuk_dt.time(),
                    jam_keluar_dt.time(),
                    status,
                    datetime.now()
                ))
        
        conn.commit()
        print("\n[SUKSES] Data dummy berhasil dimasukkan!")
        print("\n--- KREDENSIAL LOGIN ---")
        print(f"Admin   : admin / {admin_password}")
        print(f"Karyawan: karyawan1 / {karyawan_password}")
        print("------------------------")

    except Exception as e:
        conn.rollback()
        print(f"Terjadi kesalahan: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()