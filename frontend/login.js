// Konfigurasi API Backend
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api', // Ganti dengan URL backend Anda
    ENDPOINTS: {
        LOGIN: '/auth/login',
        LOGOUT: '/auth/logout',
        FORGOT_PASSWORD: '/auth/forgot-password',
        RESET_PASSWORD: '/auth/reset-password'
    }
};

// Utility Functions
const Utils = {
    // Show/Hide loading state pada button
    setLoading(button, isLoading) {
        if (isLoading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    },

    // Show error message
    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        errorElement.textContent = message;
        errorElement.classList.add('show');
        
        // Auto hide setelah 5 detik
        setTimeout(() => {
            errorElement.classList.remove('show');
        }, 5000);
    },

    // Clear error message
    clearError() {
        const errorElement = document.getElementById('errorMessage');
        errorElement.classList.remove('show');
        errorElement.textContent = '';
    },

    // Validate form input
    validateForm(formData) {
        const errors = [];
        
        if (!formData.username || formData.username.trim().length === 0) {
            errors.push('Username harus diisi');
        }
        
        if (!formData.password || formData.password.length === 0) {
            errors.push('Password harus diisi');
        }
        
        return errors;
    },

    // Simpan data ke localStorage (untuk remember me)
    saveToStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    },

    // Ambil data dari localStorage
    getFromStorage(key) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : null;
        } catch (error) {
            console.error('Error getting from localStorage:', error);
            return null;
        }
    },

    // Hapus data dari localStorage
    removeFromStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    },

    // Simpan token autentikasi
    saveAuthToken(token, userData) {
        this.saveToStorage('auth_token', token);
        this.saveToStorage('user_data', userData);
    },

    // Ambil token autentikasi
    getAuthToken() {
        return this.getFromStorage('auth_token');
    },

    // Ambil data user
    getUserData() {
        return this.getFromStorage('user_data');
    },

    // Logout - hapus semua data auth
    logout() {
        this.removeFromStorage('auth_token');
        this.removeFromStorage('user_data');
        window.location.href = 'login.html';
    }
};

// API Service untuk komunikasi dengan backend
const ApiService = {
    // Fungsi helper untuk membuat request
    async request(endpoint, options = {}) {
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // Tambahkan token auth jika ada
        const token = Utils.getAuthToken();
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {}),
            },
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || data.error || 'Terjadi kesalahan');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Login function
    async login(username, password) {
        return await this.request(API_CONFIG.ENDPOINTS.LOGIN, {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
    },

    // Forgot password function
    async forgotPassword(email) {
        return await this.request(API_CONFIG.ENDPOINTS.FORGOT_PASSWORD, {
            method: 'POST',
            body: JSON.stringify({ email }),
        });
    },

    // Reset password function
    async resetPassword(token, newPassword) {
        return await this.request(API_CONFIG.ENDPOINTS.RESET_PASSWORD, {
            method: 'POST',
            body: JSON.stringify({ token, new_password: newPassword }),
        });
    },

    // Logout function
    async logout() {
        return await this.request(API_CONFIG.ENDPOINTS.LOGOUT, {
            method: 'POST',
        });
    }
};

// Login Form Handler
class LoginHandler {
    constructor() {
        this.form = document.getElementById('loginForm');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.rememberCheckbox = document.getElementById('remember');
        this.loginButton = this.form.querySelector('.btn-login');
        
        this.init();
    }

    init() {
        // Load saved username jika ada
        this.loadSavedCredentials();
        
        // Bind event listeners
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Clear error saat user mulai mengetik
        this.usernameInput.addEventListener('input', () => Utils.clearError());
        this.passwordInput.addEventListener('input', () => Utils.clearError());
    }

    loadSavedCredentials() {
        const savedData = Utils.getFromStorage('saved_credentials');
        if (savedData && savedData.remember) {
            this.usernameInput.value = savedData.username || '';
            this.rememberCheckbox.checked = true;
        }
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        // Clear previous errors
        Utils.clearError();

        // Get form data
        const formData = {
            username: this.usernameInput.value.trim(),
            password: this.passwordInput.value,
            remember: this.rememberCheckbox.checked
        };

        // Validate form
        const errors = Utils.validateForm(formData);
        if (errors.length > 0) {
            Utils.showError(errors.join(', '));
            return;
        }

        // Set loading state
        Utils.setLoading(this.loginButton, true);

        try {
            // Call login API
            const response = await ApiService.login(formData.username, formData.password);
            
            // Handle successful login
            await this.handleLoginSuccess(response, formData.remember);
            
        } catch (error) {
            // Handle login error
            Utils.showError(error.message || 'Login gagal. Silakan coba lagi.');
        } finally {
            // Remove loading state
            Utils.setLoading(this.loginButton, false);
        }
    }

    async handleLoginSuccess(response, remember) {
        console.log('Login successful:', response);
        
        // Simpan auth token dan user data
        // Sesuaikan dengan struktur response dari backend Anda
        const token = response.token || response.access_token;
        const userData = response.user || response.data;
        
        if (token) {
            Utils.saveAuthToken(token, userData);
        }

        // Simpan credentials jika remember me dicentang
        if (remember) {
            Utils.saveToStorage('saved_credentials', {
                username: this.usernameInput.value,
                remember: true
            });
        } else {
            Utils.removeFromStorage('saved_credentials');
        }

        // Redirect ke dashboard atau halaman utama
        // Ganti dengan URL dashboard Anda
        setTimeout(() => {
            window.location.href = 'dashboard.html'; // atau halaman lain
        }, 500);
    }
}

// Forgot Password Handler (Optional - untuk future implementation)
class ForgotPasswordHandler {
    constructor() {
        this.link = document.querySelector('.forgot-password');
        if (this.link) {
            this.link.addEventListener('click', (e) => this.handleClick(e));
        }
    }

    handleClick(event) {
        event.preventDefault();
        const email = prompt('Masukkan email Anda untuk reset password:');
        
        if (email && email.trim()) {
            this.sendResetEmail(email.trim());
        }
    }

    async sendResetEmail(email) {
        try {
            const response = await ApiService.forgotPassword(email);
            alert('Link reset password telah dikirim ke email Anda.');
        } catch (error) {
            alert('Gagal mengirim link reset: ' + error.message);
        }
    }
}

// Initialize ketika DOM sudah loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize login handler
    new LoginHandler();
    
    // Initialize forgot password handler
    new ForgotPasswordHandler();
    
    // Check jika user sudah login (optional)
    const existingToken = Utils.getAuthToken();
    if (existingToken) {
        // User sudah login, bisa redirect ke dashboard
        // Uncomment baris berikut jika ingin auto-redirect
        // window.location.href = 'dashboard.html';
        console.log('User sudah login sebelumnya');
    }
});

// Export functions untuk digunakan di halaman lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Utils, ApiService, LoginHandler };
}
