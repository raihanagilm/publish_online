from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from backend.__init__ import get_db_connection
from datetime import datetime, date
import bcrypt

admin_bp = Blueprint('admin', __name__)

def check_admin():
    """Decorator manual untuk cek admin"""
    if 'user_id' not in session:
        return False
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT role FROM users WHERE id = %s"
            cursor.execute(sql, (session.get('user_id'),))
            result = cursor.fetchone()
            return result and result['role'] == 'admin'
    finally:
        conn.close()

@admin_bp.route('/admin/dashboard')
def dashboard():
    if not check_admin():
        flash('Akses ditolak', 'danger')
        return redirect(url_for('karyawan.dashboard'))
    
    today = date.today()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Hitung total karyawan
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'karyawan'")
            total_karyawan = cursor.fetchone()['count']
            
            # Hitung absen hari ini
            cursor.execute("SELECT COUNT(*) as count FROM absensi WHERE tanggal = %s", (today,))
            absen_hari_ini = cursor.fetchone()['count']
            
            # Ambil semua karyawan
            cursor.execute("SELECT * FROM users WHERE role = 'karyawan' ORDER BY nama_lengkap")
            karyawan_list = cursor.fetchall()
            
            status_absensi = []
            for karyawan in karyawan_list:
                cursor.execute("""SELECT * FROM absensi 
                                 WHERE user_id = %s AND tanggal = %s""", 
                              (karyawan['id'], today))
                absensi = cursor.fetchone()
                status_absensi.append({
                    'karyawan': karyawan,
                    'absensi': absensi
                })
    finally:
        conn.close()
    
    return render_template('admin/dashboard.html', 
                         total_karyawan=total_karyawan,
                         absen_hari_ini=absen_hari_ini,
                         status_absensi=status_absensi,
                         today=today)

@admin_bp.route('/admin/karyawan')
def manage_karyawan():
    if not check_admin():
        flash('Akses ditolak', 'danger')
        return redirect(url_for('karyawan.dashboard'))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE role = 'karyawan' ORDER BY nama_lengkap")
            karyawan = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('admin/karyawan.html', karyawan=karyawan)

@admin_bp.route('/admin/karyawan/tambah', methods=['POST'])
def tambah_karyawan():
    if not check_admin():
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    nama = request.form.get('nama')
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username', email.split('@')[0])
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Cek email sudah ada atau tidak
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Email sudah terdaftar'}), 400
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert user baru
            insert_sql = """INSERT INTO users (username, email, password_hash, role, nama_lengkap) 
                           VALUES (%s, %s, %s, 'karyawan', %s)"""
            cursor.execute(insert_sql, (username, email, password_hash, nama))
            conn.commit()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({'success': True, 'message': 'Karyawan berhasil ditambahkan'})

@admin_bp.route('/admin/karyawan/hapus/<int:id>', methods=['POST'])
def hapus_karyawan(id):
    if not check_admin():
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Hapus absensi terkait dulu (jika ada foreign key constraint)
            cursor.execute("DELETE FROM absensi WHERE user_id = %s", (id,))
            # Hapus user
            cursor.execute("DELETE FROM users WHERE id = %s", (id,))
            conn.commit()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({'success': True, 'message': 'Karyawan berhasil dihapus'})

@admin_bp.route('/admin/laporan')
def laporan():
    if not check_admin():
        flash('Akses ditolak', 'danger')
        return redirect(url_for('karyawan.dashboard'))
    
    tanggal_mulai = request.args.get('tanggal_mulai', date.today().strftime('%Y-%m-01'))
    tanggal_selesai = request.args.get('tanggal_selesai', date.today().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """SELECT a.*, u.nama_lengkap, u.email 
                     FROM absensi a 
                     JOIN users u ON a.user_id = u.id
                     WHERE a.tanggal >= %s AND a.tanggal <= %s
                     ORDER BY a.tanggal DESC"""
            cursor.execute(sql, (tanggal_mulai, tanggal_selesai))
            absensi = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('admin/laporan.html', 
                         absensi=absensi,
                         tanggal_mulai=tanggal_mulai,
                         tanggal_selesai=tanggal_selesai)

@admin_bp.route('/admin/karyawan/<int:id>/reset-password', methods=['POST'])
def reset_password_karyawan(id):
    if not check_admin():
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    default_password = 'password123'
    password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                          (password_hash, id))
            conn.commit()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({'success': True, 'message': f'Password karyawan direset ke: {default_password}'})
