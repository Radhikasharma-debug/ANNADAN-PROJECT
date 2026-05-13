import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Simple validation for 10+ digit phone numbers
    phone_clean = re.sub(r'\D', '', phone)
    return len(phone_clean) >= 10

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    return True, "Password is valid"

def validate_coordinates(latitude, longitude):
    """Validate geographic coordinates"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True, (lat, lon)
        return False, "Invalid coordinate range"
    except:
        return False, "Invalid coordinate format"
