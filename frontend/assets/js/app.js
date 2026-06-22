// === UTILITY: LIVE CLOCK ===
function startLiveClock() {
    const clockEl = document.getElementById('live-clock');
    const largeDateEl = document.getElementById('large-date-string');
    const largeTimeEl = document.getElementById('large-time-string');
    
    if (!clockEl && !largeTimeEl) return;

    const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
    const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];

    setInterval(() => {
        const now = new Date();
        const dayName = days[now.getDay()];
        const dayNum = now.getDate();
        const monthName = months[now.getMonth()];
        const year = now.getFullYear();
        
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        const dateStr = `${dayName}, ${dayNum} ${monthName} ${year}`;
        const timeStr = `${hours}:${minutes}:${seconds}`;

        if (clockEl) {
            clockEl.innerText = `${dateStr} | ${timeStr}`;
        }
        if (largeDateEl) {
            largeDateEl.innerText = dateStr;
        }
        if (largeTimeEl) {
            largeTimeEl.innerText = timeStr;
        }
    }, 1000);
}

// === UTILITY: SIDEBAR DRAWER ON MOBILE ===
function initMobileSidebar() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (!toggleBtn || !sidebar) return;

    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        sidebar.classList.toggle('open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== toggleBtn) {
            sidebar.classList.remove('open');
        }
    });
}

// === UTILITY: PHOTO VIEWER MODAL ===
function initPhotoViewer() {
    const modal = document.getElementById('photo-modal');
    const modalImg = document.getElementById('modal-img-element');
    const modalCaption = document.getElementById('modal-img-caption');
    const closeBtn = document.getElementById('close-photo-modal');

    if (!modal) return;

    // Delegate click event for thumbnail images
    document.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('img-thumb')) {
            modalImg.src = e.target.src;
            modalCaption.innerText = e.target.dataset.caption || 'Foto Absen';
            modal.style.display = 'flex';
        }
    });

    // Close modal triggers
    const closeModalFunc = () => { modal.style.display = 'none'; };
    closeBtn.addEventListener('click', closeModalFunc);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModalFunc();
    });
}

// === SESSION PROFILE SYNC & LOGOUT ===
async function checkSession() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        
        // Sync profile components on page if logged in
        if (data.logged_in) {
            const displayNameEls = document.querySelectorAll('#user-display-name');
            const displayRoleEls = document.querySelectorAll('#user-display-role');
            const avatarEls = document.querySelectorAll('.avatar-circle, #karyawan-avatar');
            
            displayNameEls.forEach(el => el.innerText = data.user.nama_lengkap || data.user.username);
            displayRoleEls.forEach(el => el.innerText = data.user.role === 'admin' ? 'Administrator' : 'Karyawan');
            avatarEls.forEach(el => {
                const initial = (data.user.nama_lengkap || data.user.username).charAt(0).toUpperCase();
                el.innerText = initial;
            });
            
            // Redirect if user is on login page
            if (document.body.classList.contains('login-page') && !document.getElementById('reset-password-form')) {
                if (data.user.role === 'admin') {
                    window.location.href = '/admin/dashboard';
                } else {
                    window.location.href = '/karyawan/absen';
                }
            }
        } else {
            // If not logged in and not on login or reset pages, redirect to login
            if (!document.body.classList.contains('login-page')) {
                window.location.href = '/';
            }
        }
    } catch (err) {
        console.error('Session check failed:', err);
    }
}

function initLogout() {
    const logoutLinks = document.querySelectorAll('.logout-link');
    logoutLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            if (confirm('Apakah Anda yakin ingin keluar?')) {
                try {
                    // Try POST logout first
                    const res = await fetch('/api/auth/logout', { method: 'POST', credentials: 'same-origin' });
                    // If POST fails (non-2xx), fallback to GET
                    if (!res.ok) {
                        await fetch('/api/auth/logout', { method: 'GET', credentials: 'same-origin' });
                    }
                } catch (err) {
                    // On network error, attempt GET logout as fallback
                    try {
                        await fetch('/api/auth/logout', { method: 'GET', credentials: 'same-origin' });
                    } catch (fallbackErr) {
                        console.error('Logout fallback failed:', fallbackErr);
                    }
                } finally {
                    // Redirect to home page after attempting logout
                    window.location.href = '/';
                }
            }
        });
    });
}


// ==========================================
// 1. LOGIN PAGE CONTROLLER
// ==========================================
function initLoginPage() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const usernameInput = document.getElementById('input-username');
        const passwordInput = document.getElementById('input-password');
        const errorEl = document.getElementById('error-msg');
        const submitBtn = document.getElementById('btn-login');

        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        // Reset
        errorEl.style.display = 'none';
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memproses...';

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || 'Login gagal.');
            }

            // Redirect based on role
            if (data.user.role === 'admin') {
                window.location.href = '/admin/dashboard';
            } else {
                window.location.href = '/karyawan/absen';
            }
        } catch (err) {
            errorEl.innerText = err.message;
            errorEl.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });

    // Forgot Password Trigger
    const forgotLink = document.getElementById('link-lupa-password');
    if (forgotLink) {
        forgotLink.addEventListener('click', async (e) => {
            e.preventDefault();
            const email = prompt('Masukkan Email terdaftar Anda untuk mengirim link reset password:');
            if (email === null) return; // cancelled
            if (!email.trim()) {
                alert('Email tidak boleh kosong!');
                return;
            }

            try {
                const res = await fetch('/api/auth/forgot-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email.trim() })
                });
                const data = await res.json();
                alert(data.message);
            } catch (err) {
                alert('Gagal mengirimkan permintaan reset password.');
            }
        });
    }
}


// ==========================================
// 2. RESET PASSWORD PAGE CONTROLLER
// ==========================================
function initResetPasswordPage() {
    const form = document.getElementById('reset-password-form');
    if (!form) return;

    // Check token
    const token = new URLSearchParams(window.location.search).get('token');
    const errorEl = document.getElementById('error-msg');
    const successEl = document.getElementById('success-msg');
    const submitBtn = document.getElementById('btn-reset-password');

    if (!token) {
        errorEl.innerText = 'Token reset password tidak ditemukan / tidak valid.';
        errorEl.style.display = 'block';
        submitBtn.disabled = true;
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const newPass = document.getElementById('input-new-password').value;
        const confirmPass = document.getElementById('input-confirm-password').value;

        if (newPass !== confirmPass) {
            errorEl.innerText = 'Password dan konfirmasi password tidak cocok!';
            errorEl.style.display = 'block';
            return;
        }

        errorEl.style.display = 'none';
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Menyimpan...';

        try {
            const res = await fetch('/api/auth/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, password: newPass })
            });
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || 'Gagal reset password.');
            }

            successEl.style.display = 'block';
            form.style.display = 'none';
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        } catch (err) {
            errorEl.innerText = err.message;
            errorEl.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.innerText = 'Simpan Password Baru';
        }
    });
}


// ==========================================
// 3. ADMIN DASHBOARD CONTROLLER
// ==========================================
async function loadAdminStats() {
    try {
        const res = await fetch('/api/admin/stats');
        if (!res.ok) return;
        const data = await res.json();
        
        document.getElementById('stat-total-karyawan').innerText = data.total_karyawan;
        document.getElementById('stat-hadir').innerText = data.hadir;
        document.getElementById('stat-sakit').innerText = data.sakit;
        document.getElementById('stat-izin').innerText = data.izin;
        document.getElementById('stat-alfa').innerText = data.alfa;
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function loadAdminLogs(dateStr = '') {
    const tbody = document.querySelector('#table-logs tbody');
    if (!tbody) return;

    try {
        let url = '/api/admin/logs';
        if (dateStr) url += `?tanggal=${dateStr}`;

        const res = await fetch(url);
        if (!res.ok) throw new Error('Gagal memuat log');
        const logs = await res.json();

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-8 text-light">Tidak ada log absensi untuk tanggal ini.</td></tr>';
            return;
        }

        tbody.innerHTML = logs.map(log => {
            const photoMasukHtml = log.foto_masuk 
                ? `<img src="${log.foto_masuk}" class="img-thumb" data-caption="Foto Masuk: ${log.nama_lengkap}" alt="Masuk">` 
                : '<span class="text-light">-</span>';
                
            const photoKeluarHtml = log.foto_keluar 
                ? `<img src="${log.foto_keluar}" class="img-thumb" data-caption="Foto Keluar: ${log.nama_lengkap}" alt="Keluar">` 
                : '<span class="text-light">-</span>';
                
            const jamMasuk = log.jam_masuk || '-';
            const jamKeluar = log.jam_keluar || '-';
            
            return `
                <tr>
                    <td data-label="Nama Lengkap"><strong>${log.nama_lengkap}</strong><br><span class="text-light">@${log.username}</span></td>
                    <td data-label="Status"><span class="badge badge-${log.status}">${log.status}</span></td>
                    <td data-label="Jam Masuk">${jamMasuk}</td>
                    <td data-label="Foto Masuk">${photoMasukHtml}</td>
                    <td data-label="Jam Keluar">${jamKeluar}</td>
                    <td data-label="Foto Keluar">${photoKeluarHtml}</td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-red">Error: ${err.message}</td></tr>`;
    }
}

function initAdminDashboard() {
    if (!document.body.classList.contains('admin-dashboard')) return;

    // Set default date input to today
    const dateInput = document.getElementById('filter-date');
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;

    // Load initial
    loadAdminStats();
    loadAdminLogs(today);

    // Refresh logs on date change
    dateInput.addEventListener('change', () => {
        loadAdminLogs(dateInput.value);
    });
}


// ==========================================
// 4. ADMIN DATA KARYAWAN (CRUD) CONTROLLER
// ==========================================
let allEmployees = [];

async function loadEmployees() {
    const tbody = document.querySelector('#table-karyawan tbody');
    if (!tbody) return;

    try {
        const res = await fetch('/api/admin/karyawan');
        if (!res.ok) throw new Error('Gagal memuat data karyawan');
        allEmployees = await res.json();

        if (allEmployees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-light">Belum ada karyawan terdaftar.</td></tr>';
            return;
        }

        tbody.innerHTML = allEmployees.map(emp => {
            const initial = emp.nama_lengkap.charAt(0).toUpperCase();
            return `
                <tr>
                    <td data-label="Nama Lengkap" class="avatar-cell">
                        <div class="avatar-init">${initial}</div>
                        <div>
                            <strong>${emp.nama_lengkap}</strong>
                        </div>
                    </td>
                    <td data-label="Username">@${emp.username}</td>
                    <td data-label="Email">${emp.email}</td>
                    <td data-label="Aksi" class="td-actions">
                        <button class="btn btn-outline btn-xs btn-edit" data-id="${emp.id}">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-danger btn-xs btn-delete" data-id="${emp.id}">
                            <i class="fas fa-trash"></i> Hapus
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center py-8 text-red">Error: ${err.message}</td></tr>`;
    }
}

function initAdminKaryawanCRUD() {
    if (!document.body.classList.contains('admin-karyawan')) return;

    // Load data
    loadEmployees();

    const modal = document.getElementById('karyawan-modal');
    const form = document.getElementById('karyawan-form');
    const modalTitle = document.getElementById('modal-title');
    const closeBtn = document.getElementById('close-karyawan-modal');
    const cancelBtn = document.getElementById('btn-cancel-modal');
    const openAddModalBtn = document.getElementById('btn-open-add-modal');
    
    const inputId = document.getElementById('karyawan-id');
    const inputNama = document.getElementById('karyawan-nama');
    const inputUsername = document.getElementById('karyawan-username');
    const inputEmail = document.getElementById('karyawan-email');
    const inputPassword = document.getElementById('karyawan-password');
    const labelPassword = document.getElementById('label-password');
    const helpPassword = document.getElementById('help-password');
    const modalError = document.getElementById('modal-error-msg');

    const openModal = (editMode = false, emp = null) => {
        modalError.style.display = 'none';
        form.reset();
        
        if (editMode && emp) {
            modalTitle.innerText = 'Edit Karyawan';
            inputId.value = emp.id;
            inputNama.value = emp.nama_lengkap;
            inputUsername.value = emp.username;
            inputEmail.value = emp.email;
            
            labelPassword.innerText = 'Password Baru (Opsional)';
            helpPassword.style.display = 'block';
            inputPassword.required = false;
        } else {
            modalTitle.innerText = 'Tambah Karyawan';
            inputId.value = '';
            
            labelPassword.innerText = 'Password';
            helpPassword.style.display = 'none';
            inputPassword.required = true;
        }
        
        modal.style.display = 'flex';
    };

    const closeModal = () => {
        modal.style.display = 'none';
    };

    openAddModalBtn.addEventListener('click', () => openModal(false));
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Form Submission (Add or Update)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        modalError.style.display = 'none';

        const id = inputId.value;
        const payload = {
            nama_lengkap: inputNama.value.trim(),
            username: inputUsername.value.trim().toLowerCase(),
            email: inputEmail.value.trim().toLowerCase(),
            password: inputPassword.value
        };

        const isEdit = id !== '';
        const url = isEdit ? `/api/admin/karyawan/${id}` : '/api/admin/karyawan';
        const method = isEdit ? 'PUT' : 'POST';

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || 'Operasi gagal.');
            }

            closeModal();
            loadEmployees();
        } catch (err) {
            modalError.innerText = err.message;
            modalError.style.display = 'block';
        }
    });

    // Delegate Edit/Delete clicks
    document.addEventListener('click', async (e) => {
        const btnEdit = e.target.closest('.btn-edit');
        const btnDelete = e.target.closest('.btn-delete');

        if (btnEdit) {
            const empId = parseInt(btnEdit.dataset.id);
            const employee = allEmployees.find(emp => emp.id === empId);
            if (employee) openModal(true, employee);
        }

        if (btnDelete) {
            const empId = parseInt(btnDelete.dataset.id);
            if (confirm('Apakah Anda yakin ingin menghapus karyawan ini? Seluruh riwayat absensi juga akan dihapus.')) {
                try {
                    const res = await fetch(`/api/admin/karyawan/${empId}`, { method: 'DELETE' });
                    if (!res.ok) {
                        const data = await res.json();
                        throw new Error(data.error || 'Gagal menghapus karyawan');
                    }
                    loadEmployees();
                } catch (err) {
                    alert(err.message);
                }
            }
        }
    });
}


// ==========================================
// 5. KARYAWAN ABSEN PORTAL CONTROLLER
// ==========================================
let activeStream = null;
let currentAbsenType = 'masuk'; // 'masuk' or 'keluar'

async function checkKaryawanStatus() {
    if (!document.body.classList.contains('karyawan-absen')) return;

    const badge = document.getElementById('status-badge-today');
    const rowMasuk = document.getElementById('row-log-masuk');
    const timeMasuk = document.getElementById('time-masuk');
    const btnViewMasuk = document.getElementById('btn-view-masuk');

    const rowKeluar = document.getElementById('row-log-keluar');
    const timeKeluar = document.getElementById('time-keluar');
    const btnViewKeluar = document.getElementById('btn-view-keluar');

    const statusSelector = document.getElementById('checkin-status-selector');
    const btnMasuk = document.getElementById('btn-submit-masuk');
    const btnKeluar = document.getElementById('btn-submit-keluar');
    const completeAlert = document.getElementById('msg-absen-complete');

    // Default resets
    rowMasuk.style.display = 'none';
    rowKeluar.style.display = 'none';
    btnViewMasuk.style.display = 'none';
    btnViewKeluar.style.display = 'none';
    statusSelector.style.display = 'none';
    btnMasuk.style.display = 'none';
    btnKeluar.style.display = 'none';
    completeAlert.style.display = 'none';

    try {
        const res = await fetch('/api/karyawan/status');
        if (!res.ok) return;
        const status = await res.json();

        // 1. Not checked in yet
        if (!status.checked_in) {
            badge.innerText = 'Belum Absen';
            badge.className = 'status-badge badge-neutral';
            
            statusSelector.style.display = 'block';
            btnMasuk.style.display = 'block';
            currentAbsenType = 'masuk';
        }
        // 2. Checked in but not check out
        else if (status.checked_in && !status.checked_out) {
            // Check if status is sakit or izin (which means no checkout needed)
            if (status.status !== 'hadir') {
                badge.innerText = status.status;
                badge.className = `status-badge badge-${status.status}`;
                completeAlert.style.display = 'block';
            } else {
                badge.innerText = 'Sudah Masuk';
                badge.className = 'status-badge badge-hadir';
                
                rowMasuk.style.display = 'flex';
                timeMasuk.innerText = status.jam_masuk;
                if (status.foto_masuk) {
                    btnViewMasuk.style.display = 'inline-block';
                    btnViewMasuk.onclick = () => {
                        const modal = document.getElementById('photo-modal');
                        document.getElementById('modal-img-element').src = status.foto_masuk;
                        document.getElementById('modal-img-caption').innerText = `Foto Masuk Anda (${status.jam_masuk})`;
                        modal.style.display = 'flex';
                    };
                }
                
                btnKeluar.style.display = 'block';
                currentAbsenType = 'keluar';
            }
        }
        // 3. Already check out
        else {
            badge.innerText = 'Absensi Lengkap';
            badge.className = 'status-badge badge-hadir';

            rowMasuk.style.display = 'flex';
            timeMasuk.innerText = status.jam_masuk;
            if (status.foto_masuk) {
                btnViewMasuk.style.display = 'inline-block';
                btnViewMasuk.onclick = () => {
                    const modal = document.getElementById('photo-modal');
                    document.getElementById('modal-img-element').src = status.foto_masuk;
                    document.getElementById('modal-img-caption').innerText = `Foto Masuk Anda (${status.jam_masuk})`;
                    modal.style.display = 'flex';
                };
            }

            rowKeluar.style.display = 'flex';
            timeKeluar.innerText = status.jam_keluar;
            if (status.foto_keluar) {
                btnViewKeluar.style.display = 'inline-block';
                btnViewKeluar.onclick = () => {
                    const modal = document.getElementById('photo-modal');
                    document.getElementById('modal-img-element').src = status.foto_keluar;
                    document.getElementById('modal-img-caption').innerText = `Foto Keluar Anda (${status.jam_keluar})`;
                    modal.style.display = 'flex';
                };
            }

            completeAlert.style.display = 'block';
        }
    } catch (err) {
        console.error('Failed checking attendance status:', err);
    }
}

function initWebcamAttendance() {
    if (!document.body.classList.contains('karyawan-absen')) return;

    const btnMasuk = document.getElementById('btn-submit-masuk');
    const btnKeluar = document.getElementById('btn-submit-keluar');
    const selectStatus = document.getElementById('select-status');

    const cameraModal = document.getElementById('camera-modal');
    const closeCamBtn = document.getElementById('close-camera-modal');
    const video = document.getElementById('webcam-stream');
    const canvas = document.getElementById('photo-canvas');
    const previewImg = document.getElementById('captured-preview');
    const camLoading = document.getElementById('camera-loading');

    const btnCapture = document.getElementById('btn-capture-photo');
    const btnRetake = document.getElementById('btn-retake-photo');
    const btnConfirm = document.getElementById('btn-confirm-photo');

    let capturedBase64 = null;

    const stopWebcam = () => {
        if (activeStream) {
            activeStream.getTracks().forEach(track => track.stop());
            activeStream = null;
        }
        video.srcObject = null;
    };

    const startWebcam = async () => {
        camLoading.style.display = 'flex';
        video.style.display = 'none';
        previewImg.style.display = 'none';
        
        btnCapture.style.display = 'inline-flex';
        btnRetake.style.display = 'none';
        btnConfirm.style.display = 'none';

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'user',
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                },
                audio: false
            });
            activeStream = stream;
            video.srcObject = stream;
            
            // Wait for video load metadata to show it
            video.onloadedmetadata = () => {
                camLoading.style.display = 'none';
                video.style.display = 'block';
            };
        } catch (err) {
            alert('Gagal mengakses kamera. Pastikan izin kamera sudah diberikan!');
            closeCameraModalFunc();
        }
    };

    const closeCameraModalFunc = () => {
        stopWebcam();
        cameraModal.style.display = 'none';
        capturedBase64 = null;
    };

    // Trigger Camera Modal or instant submit (for Sick/Permit)
    const handleAbsenMasukTrigger = async () => {
        const attendanceStatus = selectStatus.value;
        if (attendanceStatus === 'hadir') {
            cameraModal.style.display = 'flex';
            startWebcam();
        } else {
            // Sick/Permit - direct submit
            if (confirm(`Apakah Anda yakin ingin mengajukan absen dengan status: ${attendanceStatus.toUpperCase()}?`)) {
                try {
                    btnMasuk.disabled = true;
                    btnMasuk.innerText = 'Mengirim...';
                    
                    const res = await fetch('/api/karyawan/absen', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            type: 'masuk',
                            status: attendanceStatus,
                            foto: null
                        })
                    });
                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Absen gagal');
                    
                    alert(data.message);
                    checkKaryawanStatus();
                } catch (err) {
                    alert(err.message);
                } finally {
                    btnMasuk.disabled = false;
                    btnMasuk.innerText = 'Absen Masuk';
                }
            }
        }
    };

    btnMasuk.addEventListener('click', handleAbsenMasukTrigger);
    btnKeluar.addEventListener('click', () => {
        cameraModal.style.display = 'flex';
        startWebcam();
    });

    closeCamBtn.addEventListener('click', closeCameraModalFunc);

    // Capture Picture
    btnCapture.addEventListener('click', () => {
        if (!activeStream) return;
        
        // Draw frame onto canvas
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        
        // Mirror context draw since video is mirrored
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        ctx.setTransform(1, 0, 0, 1, 0, 0); // reset transform

        capturedBase64 = canvas.toDataURL('image/jpeg', 0.85);
        
        // Stop camera stream
        stopWebcam();

        // Update preview source and display
        previewImg.src = capturedBase64;
        video.style.display = 'none';
        previewImg.style.display = 'block';

        // Toggle button displays
        btnCapture.style.display = 'none';
        btnRetake.style.display = 'inline-flex';
        btnConfirm.style.display = 'inline-flex';
    });

    // Retake Photo
    btnRetake.addEventListener('click', () => {
        startWebcam();
    });

    // Submit Captured Photo
    btnConfirm.addEventListener('click', async () => {
        if (!capturedBase64) return;
        
        btnConfirm.disabled = true;
        btnConfirm.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Mengirim...';

        try {
            const res = await fetch('/api/karyawan/absen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: currentAbsenType,
                    status: currentAbsenType === 'masuk' ? selectStatus.value : 'hadir',
                    foto: capturedBase64
                })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Pengiriman absensi gagal.');

            alert(data.message);
            closeCameraModalFunc();
            checkKaryawanStatus();
        } catch (err) {
            alert(err.message);
        } finally {
            btnConfirm.disabled = false;
            btnConfirm.innerText = 'Konfirmasi & Kirim';
        }
    });
}


// ==========================================
// 6. KARYAWAN HISTORY CONTROLLER
// ==========================================
async function loadKaryawanHistory(bulan, tahun) {
    const tbody = document.querySelector('#table-history tbody');
    if (!tbody) return;

    try {
        const res = await fetch(`/api/karyawan/history?bulan=${bulan}&tahun=${tahun}`);
        if (!res.ok) throw new Error('Gagal memuat riwayat');
        const history = await res.json();

        if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-8 text-light">Tidak ada data absensi pada periode ini.</td></tr>';
            return;
        }

        tbody.innerHTML = history.map(item => {
            const photoMasukHtml = item.foto_masuk 
                ? `<img src="${item.foto_masuk}" class="img-thumb" data-caption="Foto Masuk (${item.tanggal})" alt="Masuk">` 
                : '<span class="text-light">-</span>';
                
            const photoKeluarHtml = item.foto_keluar 
                ? `<img src="${item.foto_keluar}" class="img-thumb" data-caption="Foto Keluar (${item.tanggal})" alt="Keluar">` 
                : '<span class="text-light">-</span>';
                
            const jamMasuk = item.jam_masuk || '-';
            const jamKeluar = item.jam_keluar || '-';
            
            return `
                <tr>
                    <td data-label="Tanggal"><strong>${item.tanggal}</strong></td>
                    <td data-label="Status"><span class="badge badge-${item.status}">${item.status}</span></td>
                    <td data-label="Jam Masuk">${jamMasuk}</td>
                    <td data-label="Foto Masuk">${photoMasukHtml}</td>
                    <td data-label="Jam Keluar">${jamKeluar}</td>
                    <td data-label="Foto Keluar">${photoKeluarHtml}</td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-red">Error: ${err.message}</td></tr>`;
    }
}

function initKaryawanHistory() {
    if (!document.body.classList.contains('karyawan-riwayat')) return;

    const selectBulan = document.getElementById('filter-bulan');
    const selectTahun = document.getElementById('filter-tahun');
    const applyBtn = document.getElementById('btn-apply-filters');

    const now = new Date();
    const currentMonth = now.getMonth() + 1; // 1-indexed
    const currentYear = now.getFullYear();

    // Populate Year dropdown (current year down to 5 years ago)
    selectTahun.innerHTML = '';
    for (let yr = currentYear; yr >= currentYear - 5; yr--) {
        const opt = document.createElement('option');
        opt.value = yr;
        opt.innerText = yr;
        selectTahun.appendChild(opt);
    }

    // Set selectors default
    selectBulan.value = currentMonth;
    selectTahun.value = currentYear;

    // Load initial
    loadKaryawanHistory(currentMonth, currentYear);

    // Apply filter trigger
    applyBtn.addEventListener('click', () => {
        loadKaryawanHistory(selectBulan.value, selectTahun.value);
    });
}


// ==========================================
// DOM CONTENT LOADED - APPLICATION ROUTER
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // 1. Check Session & Guards (Excluding specific public assets inside login)
    checkSession();
    
    // 2. Global Utilities
    startLiveClock();
    initMobileSidebar();
    initPhotoViewer();
    initLogout();

    // 3. Controller Handlers
    initLoginPage();
    initResetPasswordPage();
    initAdminDashboard();
    initAdminKaryawanCRUD();
    checkKaryawanStatus();
    initWebcamAttendance();
    initKaryawanHistory();
});