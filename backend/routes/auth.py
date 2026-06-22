from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import bcrypt
import secrets
from datetime import datetime, timedelta
from backend.__init__ import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT role FROM users WHERE id = %s"
                cursor.execute(sql, (session.get('user_id'),))
                result = cursor.fetchone()
                if result and result['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif result:
                    return redirect(url_for('karyawan.dashboard'))
        finally:
            conn.close()
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                
                if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Login berhasil!', 'success')
                    
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    
                    if user['role'] == 'admin':
                        return redirect(url_for('admin.dashboard'))
                    return redirect(url_for('karyawan.dashboard'))
                else:
                    flash('Username atau password salah', 'danger')
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
                
                if user:
                    token = secrets.token_urlsafe(32)
                    expires_at = datetime.utcnow() + timedelta(hours=1)
                    
                    # Simpan token ke database (asumsikan ada tabel reset_tokens)
                    # Jika tabel belum ada, skip bagian ini untuk sementara
                    try:
                        insert_sql = """INSERT INTO reset_tokens (user_id, token, expires_at, used) 
                                       VALUES (%s, %s, %s, FALSE)"""
                        cursor.execute(insert_sql, (user['id'], token, expires_at))
                        conn.commit()
                        
                        reset_link = f"{request.host_url}reset-password/{token}"
                        
                        # TODO: Implementasi kirim email dengan Resend nanti
                        flash('Link reset password telah dikirim ke email Anda', 'success')
                    except Exception as e:
                        flash(f'Token dibuat namun gagal simpan ke DB: {str(e)}', 'warning')
                else:
                    flash('Email tidak ditemukan', 'danger')
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """SELECT rt.*, u.id as user_id FROM reset_tokens rt
                     JOIN users u ON rt.user_id = u.id
                     WHERE rt.token = %s AND rt.used = FALSE AND rt.expires_at > %s"""
            cursor.execute(sql, (token, datetime.utcnow()))
            reset_token = cursor.fetchone()
            
            if not reset_token:
                flash('Token tidak valid atau sudah kadaluarsa', 'danger')
                return redirect(url_for('auth.forgot_password'))
            
            if request.method == 'POST':
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                
                if password != confirm_password:
                    flash('Password tidak cocok', 'danger')
                    return render_template('auth/reset_password.html', token=token)
                
                # Hash password baru
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Update password user
                update_sql = "UPDATE users SET password_hash = %s WHERE id = %s"
                cursor.execute(update_sql, (password_hash, reset_token['user_id']))
                
                # Tandai token sebagai digunakan
                mark_used_sql = "UPDATE reset_tokens SET used = TRUE WHERE token = %s"
                cursor.execute(mark_used_sql, (token,))
                conn.commit()
                
                flash('Password berhasil direset, silakan login', 'success')
                return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return render_template('auth/reset_password.html', token=token)
