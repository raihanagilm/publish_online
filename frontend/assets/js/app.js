// === LOGIN HANDLER ===
function handleLogin(event) {
    event.preventDefault(); // Mencegah form submit default (reload halaman)
    
    const usernameInput = document.getElementById('input-username');
    const passwordInput = document.getElementById('input-password');
    const errorMsg = document.getElementById('error-msg');
    const submitBtn = document.getElementById('btn-login');

    const username = usernameInput.value.trim().toLowerCase();
    const password = passwordInput.value;

    // Reset error state
    errorMsg.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.innerText = 'Memproses...';

    // Simulasi delay network (1 detik)
    setTimeout(() => {
        // Validasi sederhana untuk prototype
        if (!username || !password) {
            showError("Username dan Password wajib diisi!");
            return;
        }

        // Simulasi routing berdasarkan role (Nanti ini akan diganti dengan fetch ke API Flask)
        if (username === 'admin') {
            // Redirect ke halaman admin
            window.location.href = 'admin/dashboard.html'; 
        } else if (username === 'karyawan' || username.includes('@')) {
            // Redirect ke halaman karyawan
            window.location.href = 'karyawan/absen.html';
        } else {
            showError("Username atau Password salah!");
        }
        
        // Reset button state jika ada error
        submitBtn.disabled = false;
        submitBtn.innerText = 'Masuk';
    }, 1000);
}

function showError(message) {
    const errorMsg = document.getElementById('error-msg');
    const submitBtn = document.getElementById('btn-login');
    
    errorMsg.innerText = message;
    errorMsg.style.display = 'block';
    submitBtn.disabled = false;
    submitBtn.innerText = 'Masuk';
}

// === INISIALISASI HALAMAN ===
document.addEventListener('DOMContentLoaded', () => {
    // Cek apakah ada form login di halaman ini
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Nanti kita tambahkan logic untuk jam, chart, dll di sini
});