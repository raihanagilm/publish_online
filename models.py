# Models untuk referensi struktur database saja
# Tidak digunakan langsung karena kita pakai raw SQL dengan pymysql

class User:
    """
    Referensi struktur tabel users:
    - id: INT PRIMARY KEY AUTO_INCREMENT
    - username: VARCHAR(100) UNIQUE NOT NULL
    - email: VARCHAR(120) UNIQUE NOT NULL
    - password_hash: VARCHAR(256) NOT NULL
    - role: ENUM('admin', 'karyawan') DEFAULT 'karyawan'
    - nama_lengkap: VARCHAR(100)
    - created_at: DATETIME
    """
    pass

class Absensi:
    """
    Referensi struktur tabel absensi:
    - id: INT PRIMARY KEY AUTO_INCREMENT
    - user_id: INT FOREIGN KEY REFERENCES users(id)
    - tanggal: DATE NOT NULL
    - jam_masuk: TIME
    - jam_keluar: TIME
    - foto_masuk: VARCHAR(500)
    - foto_keluar: VARCHAR(500)
    - status: VARCHAR(20) DEFAULT 'hadir'
    - created_at: DATETIME
    """
    pass

class ResetToken:
    """
    Referensi struktur tabel reset_tokens:
    - id: INT PRIMARY KEY AUTO_INCREMENT
    - user_id: INT FOREIGN KEY REFERENCES users(id)
    - token: VARCHAR(100) UNIQUE NOT NULL
    - expires_at: DATETIME NOT NULL
    - used: BOOLEAN DEFAULT FALSE
    """
    pass
