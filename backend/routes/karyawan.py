from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from backend.__init__ import get_db_connection
from datetime import datetime, date, time
import bcrypt

karyawan_bp = Blueprint('karyawan', __name__)

def check_karyawan():
    """Decorator manual untuk cek karyawan"""
    if 'user_id' not in session:
        return False
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT role FROM users WHERE id = %s"
            cursor.execute(sql, (session.get('user_id'),))
            result = cursor.fetchone()
            return result and result['role'] == 'karyawan'
    finally:
        conn.close()

@karyawan_bp.route('/karyawan/dashboard')
def dashboard():
    if not check_karyawan():
        return redirect(url_for('admin.dashboard'))
    
    today = date.today()
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Ambil absensi hari ini
            cursor.execute("""SELECT * FROM absensi 
                             WHERE user_id = %s AND tanggal = %s""", 
                          (session.get('user_id'), today))
            absensi_hari_ini = cursor.fetchone()
            
            # Ambil riwayat 10 terakhir
            cursor.execute("""SELECT * FROM absensi 
                             WHERE user_id = %s 
                             ORDER BY tanggal DESC LIMIT 10""", 
                          (session.get('user_id'),))
            riwayat = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('karyawan/dashboard.html', 
                         absensi_hari_ini=absensi_hari_ini, 
                         riwayat=riwayat,
                         today=today)

@karyawan_bp.route('/karyawan/absen/masuk', methods=['POST'])
def absen_masuk():
    if not check_karyawan():
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    today = date.today()
    now = datetime.now().time()
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Cek apakah sudah absen masuk hari ini
            cursor.execute("""SELECT * FROM absensi 
                             WHERE user_id = %s AND tanggal = %s""", 
                          (session.get('user_id'), today))
            absensi_hari_ini = cursor.fetchone()
            
            if absensi_hari_ini and absensi_hari_ini['jam_masuk']:
                return jsonify({'success': False, 'message': 'Anda sudah absen masuk hari ini'}), 400
            
            # Handle upload foto (jika ada)
            foto = request.files.get('foto')
            foto_url = None
            
            if foto and foto.filename:
                # TODO: Implementasi upload ke Cloudinary nanti
                # Untuk sementara simpan nama file saja
                foto_url = f"/static/uploads/{foto.filename}"
            
            if not absensi_hari_ini:
                # Insert absensi baru
                insert_sql = """INSERT INTO absensi (user_id, tanggal, jam_masuk, foto_masuk, status) 
                               VALUES (%s, %s, %s, %s, 'hadir')"""
                cursor.execute(insert_sql, (session.get('user_id'), today, now, foto_url))
            else:
                # Update absensi yang ada
                update_sql = """UPDATE absensi SET jam_masuk = %s, foto_masuk = %s 
                               WHERE user_id = %s AND tanggal = %s"""
                cursor.execute(update_sql, (now, foto_url, session.get('user_id'), today))
            
            conn.commit()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({'success': True, 'message': 'Absen masuk berhasil'})

@karyawan_bp.route('/karyawan/absen/keluar', methods=['POST'])
def absen_keluar():
    if not check_karyawan():
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    today = date.today()
    now = datetime.now().time()
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Cek apakah sudah absen masuk hari ini
            cursor.execute("""SELECT * FROM absensi 
                             WHERE user_id = %s AND tanggal = %s""", 
                          (session.get('user_id'), today))
            absensi_hari_ini = cursor.fetchone()
            
            if not absensi_hari_ini or not absensi_hari_ini['jam_masuk']:
                return jsonify({'success': False, 'message': 'Anda belum absen masuk hari ini'}), 400
            
            if absensi_hari_ini['jam_keluar']:
                return jsonify({'success': False, 'message': 'Anda sudah absen keluar hari ini'}), 400
            
            # Handle upload foto (jika ada)
            foto = request.files.get('foto')
            foto_url = None
            
            if foto and foto.filename:
                # TODO: Implementasi upload ke Cloudinary nanti
                foto_url = f"/static/uploads/{foto.filename}"
            
            # Update jam keluar
            update_sql = """UPDATE absensi SET jam_keluar = %s, foto_keluar = %s 
                           WHERE user_id = %s AND tanggal = %s"""
            cursor.execute(update_sql, (now, foto_url, session.get('user_id'), today))
            conn.commit()
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()
    
    return jsonify({'success': True, 'message': 'Absen keluar berhasil'})

@karyawan_bp.route('/karyawan/riwayat')
def riwayat():
    if not check_karyawan():
        return redirect(url_for('admin.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM absensi 
                             WHERE user_id = %s 
                             ORDER BY tanggal DESC 
                             LIMIT %s OFFSET %s""", 
                          (session.get('user_id'), per_page, offset))
            riwayat_absensi = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('karyawan/riwayat.html', riwayat=riwayat_absensi)
