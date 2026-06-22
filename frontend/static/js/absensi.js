// JavaScript untuk fungsi absensi (masuk/keluar) dengan kamera

document.addEventListener('DOMContentLoaded', function() {
    // Inisialisasi video untuk modal absen masuk
    const videoMasuk = document.getElementById('videoMasuk');
    const canvasMasuk = document.getElementById('canvasMasuk');
    const previewMasuk = document.getElementById('previewMasuk');
    const fotoMasukInput = document.getElementById('fotoMasuk');
    const btnAmbilFotoMasuk = document.getElementById('btnAmbilFotoMasuk');
    const btnKirimAbsenMasuk = document.getElementById('btnKirimAbsenMasuk');
    
    // Inisialisasi video untuk modal absen keluar
    const videoKeluar = document.getElementById('videoKeluar');
    const canvasKeluar = document.getElementById('canvasKeluar');
    const previewKeluar = document.getElementById('previewKeluar');
    const fotoKeluarInput = document.getElementById('fotoKeluar');
    const btnAmbilFotoKeluar = document.getElementById('btnAmbilFotoKeluar');
    const btnKirimAbsenKeluar = document.getElementById('btnKirimAbsenKeluar');
    
    let streamMasuk = null;
    let streamKeluar = null;
    let fotoMasukBlob = null;
    let fotoKeluarBlob = null;
    
    // Fungsi memulai kamera
    async function startCamera(videoElement, type) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: 'user',
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            });
            
            videoElement.srcObject = stream;
            
            if (type === 'masuk') {
                streamMasuk = stream;
            } else {
                streamKeluar = stream;
            }
        } catch (error) {
            console.error('Error accessing camera:', error);
            showNotification('Gagal mengakses kamera. Pastikan izin kamera diberikan.', 'danger');
        }
    }
    
    // Fungsi menghentikan kamera
    function stopCamera(stream) {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }
    
    // Fungsi mengambil foto
    function takePhoto(videoElement, canvasElement, previewElement, type) {
        const context = canvasElement.getContext('2d');
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
        context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
        
        // Tampilkan preview
        previewElement.src = canvasElement.toDataURL('image/jpeg', 0.8);
        previewElement.classList.remove('d-none');
        videoElement.classList.add('d-none');
        
        // Convert ke blob
        canvasElement.toBlob(function(blob) {
            if (type === 'masuk') {
                fotoMasukBlob = blob;
            } else {
                fotoKeluarBlob = blob;
            }
        }, 'image/jpeg', 0.8);
    }
    
    // Event listener untuk modal absen masuk
    const modalAbsenMasuk = document.getElementById('modalAbsenMasuk');
    if (modalAbsenMasuk) {
        modalAbsenMasuk.addEventListener('shown.bs.modal', function() {
            startCamera(videoMasuk, 'masuk');
        });
        
        modalAbsenMasuk.addEventListener('hidden.bs.modal', function() {
            stopCamera(streamMasuk);
            videoMasuk.classList.remove('d-none');
            if (previewMasuk) previewMasuk.classList.add('d-none');
            fotoMasukBlob = null;
        });
    }
    
    // Event listener untuk modal absen keluar
    const modalAbsenKeluar = document.getElementById('modalAbsenKeluar');
    if (modalAbsenKeluar) {
        modalAbsenKeluar.addEventListener('shown.bs.modal', function() {
            startCamera(videoKeluar, 'keluar');
        });
        
        modalAbsenKeluar.addEventListener('hidden.bs.modal', function() {
            stopCamera(streamKeluar);
            videoKeluar.classList.remove('d-none');
            if (previewKeluar) previewKeluar.classList.add('d-none');
            fotoKeluarBlob = null;
        });
    }
    
    // Tombol ambil foto masuk
    if (btnAmbilFotoMasuk) {
        btnAmbilFotoMasuk.addEventListener('click', function() {
            takePhoto(videoMasuk, canvasMasuk, previewMasuk, 'masuk');
        });
    }
    
    // Tombol ambil foto keluar
    if (btnAmbilFotoKeluar) {
        btnAmbilFotoKeluar.addEventListener('click', function() {
            takePhoto(videoKeluar, canvasKeluar, previewKeluar, 'keluar');
        });
    }
    
    // Input file alternatif (untuk mobile)
    if (fotoMasukInput) {
        fotoMasukInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                fotoMasukBlob = file;
                const reader = new FileReader();
                reader.onload = function(event) {
                    previewMasuk.src = event.target.result;
                    previewMasuk.classList.remove('d-none');
                    videoMasuk.classList.add('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    if (fotoKeluarInput) {
        fotoKeluarInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                fotoKeluarBlob = file;
                const reader = new FileReader();
                reader.onload = function(event) {
                    previewKeluar.src = event.target.result;
                    previewKeluar.classList.remove('d-none');
                    videoKeluar.classList.add('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Tombol kirim absen masuk
    if (btnKirimAbsenMasuk) {
        btnKirimAbsenMasuk.addEventListener('click', function() {
            if (!fotoMasukBlob) {
                showNotification('Silakan ambil foto terlebih dahulu', 'warning');
                return;
            }
            
            const formData = new FormData();
            formData.append('foto', fotoMasukBlob);
            
            btnKirimAbsenMasuk.disabled = true;
            btnKirimAbsenMasuk.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Mengirim...';
            
            fetch('/karyawan/absen/masuk', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification(data.message, 'danger');
                    btnKirimAbsenMasuk.disabled = false;
                    btnKirimAbsenMasuk.innerHTML = '<i class="bi bi-send"></i> Kirim Absen';
                }
            })
            .catch(error => {
                showNotification('Terjadi kesalahan: ' + error, 'danger');
                btnKirimAbsenMasuk.disabled = false;
                btnKirimAbsenMasuk.innerHTML = '<i class="bi bi-send"></i> Kirim Absen';
            });
        });
    }
    
    // Tombol kirim absen keluar
    if (btnKirimAbsenKeluar) {
        btnKirimAbsenKeluar.addEventListener('click', function() {
            if (!fotoKeluarBlob) {
                showNotification('Silakan ambil foto terlebih dahulu', 'warning');
                return;
            }
            
            const formData = new FormData();
            formData.append('foto', fotoKeluarBlob);
            
            btnKirimAbsenKeluar.disabled = true;
            btnKirimAbsenKeluar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Mengirim...';
            
            fetch('/karyawan/absen/keluar', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification(data.message, 'danger');
                    btnKirimAbsenKeluar.disabled = false;
                    btnKirimAbsenKeluar.innerHTML = '<i class="bi bi-send"></i> Kirim Absen';
                }
            })
            .catch(error => {
                showNotification('Terjadi kesalahan: ' + error, 'danger');
                btnKirimAbsenKeluar.disabled = false;
                btnKirimAbsenKeluar.innerHTML = '<i class="bi bi-send"></i> Kirim Absen';
            });
        });
    }
});
