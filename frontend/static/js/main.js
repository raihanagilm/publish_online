// Main JavaScript untuk Sistem Absensi

// Utility function untuk menampilkan notifikasi
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto dismiss setelah 5 detik
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Format tanggal ke format Indonesia
function formatDateIndonesian(dateString) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('id-ID', options);
}

// Format waktu
function formatTime(timeString) {
    if (!timeString) return '-';
    return timeString;
}

// Export functions untuk digunakan di template lain
window.showNotification = showNotification;
window.formatDateIndonesian = formatDateIndonesian;
window.formatTime = formatTime;

console.log('Sistem Absensi Kantor - Loaded');
