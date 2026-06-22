import os
from flask import Flask, request, jsonify
from flask_login import LoginManager
from config import Config
from models import db, User
import cloudinary
import resend

# Import blueprints
from backend.routes.auth import auth_bp
from backend.routes.karyawan import karyawan_bp
from backend.routes.admin import admin_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():
    # Get the base directory (where app.py is located)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, 
                static_folder=os.path.join(base_dir, 'frontend', 'static'),
                template_folder=os.path.join(base_dir, 'frontend', 'templates'))
    app.config.from_object(Config)
    
    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure Cloudinary
    cloudinary.config(url=app.config['CLOUDINARY_URL'])
    
    # Configure Resend
    resend.api_key = app.config['RESEND_API_KEY']
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(karyawan_bp)
    app.register_blueprint(admin_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.errorhandler(404)
    def not_found(e):
        if request.is_json:
            return jsonify({'error': 'Not found'}), 404
        return 'Page not found', 404
    
    @app.errorhandler(500)
    def server_error(e):
        if request.is_json:
            return jsonify({'error': 'Server error'}), 500
        return 'Server error', 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(nama='Administrator', email='admin@kantor.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin default dibuat: admin@kantor.com / admin123')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
