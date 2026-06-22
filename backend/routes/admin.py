from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Absensi
from datetime import datetime, date, time
import cloudinary.uploader

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'danger')
        return redirect(url_for('karyawan.dashboard'))
    
    today = date.today()
    total_karyawan = User.query.filter_by(role='karyawan').count()
    absen_hari_ini = Absensi.query.filter_by(tanggal=today).count()
    
    karyawan_absen = User.query.filter_by(role='karyawan').all()
    status_absensi = []
    
    for karyawan in karyawan_absen:
        absensi = Absensi.query.filter_by(user_id=karyawan.id, tanggal=today).first()
        status_absensi.append({
            'karyawan': karyawan,
            'absensi': absensi
        })
    
    return render_template('admin/dashboard.html', 
                         total_karyawan=total_karyawan,
                         absen_hari_ini=absen_hari_ini,
                         status_absensi=status_absensi,
                         today=today)

@admin_bp.route('/admin/karyawan')
@login_required
def manage_karyawan():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'danger')
        return redirect(url_for('karyawan.dashboard'))
    
    karyawan = User.query.filter_by(role='karyawan').order_by(User.nama).all()
    return render_template('admin/karyawan.html', karyawan=karyawan)

@admin_bp.route('/admin/karyawan/tambah', methods=['POST'])
@login_required
def tambah_karyawan():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    nama = request.form.get('nama')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email sudah terdaftar'}), 400
    
    user_baru = User(nama=nama, email=email, role='karyawan')
    user_baru.set_password(password)
    db.session.add(user_baru)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Karyawan berhasil ditambahkan'})

@admin_bp.route('/admin/karyawan/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_karyawan(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Karyawan berhasil dihapus'})

@admin_bp.route('/admin/laporan')
@login_required
def laporan():
    if current_user.role != 'admin':
        flash('Akses ditolak', 'danger')
        return redirect(url_for('karyawan.dashboard'))
    
    tanggal_mulai = request.args.get('tanggal_mulai', date.today().strftime('%Y-%m-01'))
    tanggal_selesai = request.args.get('tanggal_selesai', date.today().strftime('%Y-%m-%d'))
    
    absensi = Absensi.query\
        .filter(Absensi.tanggal >= tanggal_mulai)\
        .filter(Absensi.tanggal <= tanggal_selesai)\
        .join(User)\
        .order_by(Absensi.tanggal.desc())\
        .all()
    
    return render_template('admin/laporan.html', 
                         absensi=absensi,
                         tanggal_mulai=tanggal_mulai,
                         tanggal_selesai=tanggal_selesai)

@admin_bp.route('/admin/karyawan/<int:id>/reset-password', methods=['POST'])
@login_required
def reset_password_karyawan(id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    user = User.query.get_or_404(id)
    default_password = 'password123'
    user.set_password(default_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Password {user.nama} direset ke: {default_password}'})
