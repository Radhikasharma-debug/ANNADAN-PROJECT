import os
import base64
from datetime import datetime
from pathlib import Path

class ImageUploadService:
    """Service for handling food donation image uploads"""
    
    # Configuration
    UPLOAD_PATH = 'uploads/donations'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def ensure_upload_directory():
        """Create upload directory if it doesn't exist"""
        try:
            Path(ImageUploadService.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            return False
    
    @staticmethod
    def validate_image(file_data):
        """Validate image file"""
        try:
            # Check if file exists
            if not file_data:
                return {'valid': False, 'error': 'No file provided'}
            
            # Check file size
            if len(file_data) > ImageUploadService.MAX_FILE_SIZE:
                return {'valid': False, 'error': f'File too large (max {ImageUploadService.MAX_FILE_SIZE / 1024 / 1024}MB)'}
            
            # Check file extension
            filename = getattr(file_data, 'filename', '')
            if not filename:
                return {'valid': False, 'error': 'Invalid filename'}
            
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if ext not in ImageUploadService.ALLOWED_EXTENSIONS:
                return {'valid': False, 'error': f'Invalid file type. Allowed: {", ".join(ImageUploadService.ALLOWED_EXTENSIONS)}'}
            
            return {'valid': True}
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    @staticmethod
    def save_image_base64(file_data):
        """Save image as base64 string (for embedded storage)"""
        try:
            # Read file bytes
            if hasattr(file_data, 'read'):
                file_bytes = file_data.read()
            else:
                file_bytes = file_data
            
            # Convert to base64
            base64_string = base64.b64encode(file_bytes).decode('utf-8')
            
            return {
                'success': True,
                'data': base64_string,
                'size': len(file_bytes)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def save_image_file(file_data, donation_id):
        """Save image to filesystem"""
        try:
            # Ensure directory exists
            ImageUploadService.ensure_upload_directory()
            
            # Generate filename
            ext = file_data.filename.rsplit('.', 1)[1].lower() if '.' in file_data.filename else 'jpg'
            filename = f"{donation_id}_{datetime.utcnow().timestamp()}.{ext}"
            filepath = os.path.join(ImageUploadService.UPLOAD_PATH, filename)
            
            # Save file
            file_data.save(filepath)
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'url': f'/uploads/donations/{filename}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_image(filename):
        """Delete image file"""
        try:
            filepath = os.path.join(ImageUploadService.UPLOAD_PATH, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return {'success': True}
            return {'success': False, 'error': 'File not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
