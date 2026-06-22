from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, User, Absensi
from datetime import datetime, date, time
import cloudinary.uploader

karyawan_bp = Blueprint('karyawan', __name__)

@karyawan_bp.route('/karyawan/dashboard')
@login_required
def dashboard():
    if current_user.role != 'karyawan':
        return redirect(url_for('admin.dashboard'))
    
    today = date.today()
    absensi_hari_ini = Absensi.query.filter_by(user_id=current_user.id, tanggal=today).first()
    
    riwayat = Absensi.query.filter_by(user_id=current_user.id).order_by(Absensi.tanggal.desc()).limit(10).all()
    
    return render_template('karyawan/dashboard.html', 
                         absensi_hari_ini=absensi_hari_ini, 
                         riwayat=riwayat,
                         today=today)

@karyawan_bp.route('/karyawan/absen/masuk', methods=['POST'])
@login_required
def absen_masuk():
    if current_user.role != 'karyawan':
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    today = date.today()
    now = datetime.now().time()
    
    absensi_hari_ini = Absensi.query.filter_by(user_id=current_user.id, tanggal=today).first()
    
    if absensi_hari_ini and absensi_hari_ini.jam_masuk:
        return jsonify({'success': False, 'message': 'Anda sudah absen masuk hari ini'}), 400
    
    foto = request.files.get('foto')
    foto_url = None
    
    if foto:
        try:
            upload_result = cloudinary.uploader.upload(foto, folder='absensi/masuk')
            foto_url = upload_result['secure_url']
        except Exception as e:
            return jsonify({'success': False, 'message': f'Gagal upload foto: {str(e)}'}), 500
    
    if not absensi_hari_ini:
        absensi_hari_ini = Absensi(
            user_id=current_user.id,
            tanggal=today,
            jam_masuk=now,
            foto_masuk=foto_url,
            status='hadir'
        )
        db.session.add(absensi_hari_ini)
    else:
        absensi_hari_ini.jam_masuk = now
        absensi_hari_ini.foto_masuk = foto_url
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Absen masuk berhasil'})

@karyawan_bp.route('/karyawan/absen/keluar', methods=['POST'])
@login_required
def absen_keluar():
    if current_user.role != 'karyawan':
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403
    
    today = date.today()
    now = datetime.now().time()
    
    absensi_hari_ini = Absensi.query.filter_by(user_id=current_user.id, tanggal=today).first()
    
    if not absensi_hari_ini or not absensi_hari_ini.jam_masuk:
        return jsonify({'success': False, 'message': 'Anda belum absen masuk hari ini'}), 400
    
    if absensi_hari_ini.jam_keluar:
        return jsonify({'success': False, 'message': 'Anda sudah absen keluar hari ini'}), 400
    
    foto = request.files.get('foto')
    foto_url = None
    
    if foto:
        try:
            upload_result = cloudinary.uploader.upload(foto, folder='absensi/keluar')
            foto_url = upload_result['secure_url']
        except Exception as e:
            return jsonify({'success': False, 'message': f'Gagal upload foto: {str(e)}'}), 500
    
    absensi_hari_ini.jam_keluar = now
    absensi_hari_ini.foto_keluar = foto_url
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Absen keluar berhasil'})

@karyawan_bp.route('/karyawan/riwayat')
@login_required
def riwayat():
    if current_user.role != 'karyawan':
        return redirect(url_for('admin.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    riwayat_absensi = Absensi.query.filter_by(user_id=current_user.id)\
        .order_by(Absensi.tanggal.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('karyawan/riwayat.html', riwayat=riwayat_absensi)
