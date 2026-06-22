from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Absensi, ResetToken
from datetime import datetime, date, time, timedelta
import cloudinary.uploader
import resend
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('karyawan.dashboard'))
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login berhasil!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('karyawan.dashboard'))
        flash('Email atau password salah', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            reset_token = ResetToken(user_id=user.id, token=token, expires_at=expires_at)
            db.session.add(reset_token)
            db.session.commit()
            
            reset_link = f"{request.host_url}reset-password/{token}"
            
            try:
                resend.Emails.send({
                    "from": "Absensi Kantor <onboarding@resend.dev>",
                    "to": user.email,
                    "subject": "Reset Password Absensi",
                    "html": f"""
                    <h2>Reset Password</h2>
                    <p>Klik link berikut untuk reset password Anda:</p>
                    <a href="{reset_link}">{reset_link}</a>
                    <p>Link ini berlaku selama 1 jam.</p>
                    """
                })
                flash('Link reset password telah dikirim ke email Anda', 'success')
            except Exception as e:
                flash(f'Gagal mengirim email: {str(e)}', 'danger')
        else:
            flash('Email tidak ditemukan', 'danger')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = ResetToken.query.filter_by(token=token, used=False).first()
    
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        flash('Token tidak valid atau sudah kadaluarsa', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Password tidak cocok', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        user = User.query.get(reset_token.user_id)
        user.set_password(password)
        reset_token.used = True
        db.session.commit()
        
        flash('Password berhasil direset, silakan login', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)
