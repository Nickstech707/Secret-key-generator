from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
import subprocess
import base64
import re
import logging
from functools import wraps
import time
import hashlib
import math
import qrcode
import io
import secrets
import string

app = Flask(__name__, static_folder='static', template_folder='templates')
# CORS(app)

# Configure logging
logging.basicConfig(
    filename='key_generator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Rate limiting configuration
RATE_LIMIT = {
    'window': 3600,  # 1 hour in seconds
    'max_requests': 50  # maximum requests per window
}
request_history = {}

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        current_time = time.time()
        
        # Clean up old entries
        request_history[ip] = [t for t in request_history.get(ip, []) 
                             if current_time - t < RATE_LIMIT['window']]
        
        if len(request_history.get(ip, [])) >= RATE_LIMIT['max_requests']:
            logging.warning(f"Rate limit exceeded for IP: {ip}")
            return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
        
        request_history.setdefault(ip, []).append(current_time)
        return f(*args, **kwargs)
    return decorated_function

def generate_secure_random_key(length=64):
    """
    Generate a secure random key using OpenSSL.
    
    :param length: Length of the key in bytes
    :return: tuple (key, entropy_estimate)
    """
    try:
        # Generate random bytes using OpenSSL
        result = subprocess.run(
            ['openssl', 'rand', '-base64', str(length)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        
        # Get the raw key
        key = result.stdout.decode('utf-8').strip()
        
        # Calculate entropy estimate
        entropy = calculate_entropy(key)
        
        # Format key for better readability
        formatted_key = format_key(key)
        
        return formatted_key, entropy
    except subprocess.CalledProcessError as e:
        logging.error(f"OpenSSL error: {e.stderr.decode('utf-8')}")
        return None, 0
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return None, 0

def calculate_entropy(key):
    """Calculate Shannon entropy of the key"""
    if not key:
        return 0
    
    entropy = 0
    for x in range(256):
        p_x = key.count(chr(x))/len(key)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy

def format_key(key):
    """Format key into groups for better readability"""
    # Remove any existing whitespace
    key = re.sub(r'\s+', '', key)
    # Group into chunks of 4 characters
    return '-'.join([key[i:i+4] for i in range(0, len(key), 4)])

def analyze_key_strength(key):
    """
    Analyze the strength of the generated key
    Returns a dictionary with various strength metrics
    """
    format_type = request.get_json().get('format', 'alphanumeric')
    
    metrics = {
        'length': len(key),
        'has_uppercase': bool(re.search(r'[A-Z]', key)),
        'has_lowercase': bool(re.search(r'[a-z]', key)),
        'has_numbers': bool(re.search(r'[0-9]', key)),
        'has_special': bool(re.search(r'[^A-Za-z0-9]', key)) if format_type != 'alphanumeric' else False,
        'unique_chars': len(set(key)),
    }
    
    # Calculate overall strength score (0-100)
    score = 0
    score += min(50, metrics['length'])  # Up to 50 points for length
    
    if format_type == 'alphanumeric':
        # For alphanumeric, only consider letters and numbers
        score += 15 if metrics['has_uppercase'] else 0
        score += 15 if metrics['has_lowercase'] else 0
        score += 20 if metrics['has_numbers'] else 0
    else:
        # For other formats, include special characters in scoring
        score += 10 if metrics['has_uppercase'] else 0
        score += 10 if metrics['has_lowercase'] else 0
        score += 15 if metrics['has_numbers'] else 0
        score += 15 if metrics['has_special'] else 0
    
    metrics['strength_score'] = score
    metrics['strength_label'] = get_strength_label(score)
    
    return metrics

def get_strength_label(score):
    if score >= 90:
        return "Very Strong"
    elif score >= 70:
        return "Strong"
    elif score >= 50:
        return "Moderate"
    else:
        return "Weak"

@app.route('/')
def home():
    app.logger.info('Serving index.html')
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@rate_limit
def generate_key():
    try:
        data = request.get_json()
        length = int(data.get('length', 32))
        format_type = data.get('format', 'alphanumeric')
        
        if length < 8:
            return jsonify({'error': 'Length must be at least 8 bytes'}), 400
        if length > 128:
            return jsonify({'error': 'Length must not exceed 128 bytes'}), 400
        
        if format_type == 'alphanumeric':
            # Generate alphanumeric string (A-Z, a-z, 0-9)
            alphabet = string.ascii_letters + string.digits  # This includes both upper and lowercase letters
            key = ''.join(secrets.choice(alphabet) for _ in range(length))
        elif format_type == 'hex':
            # Generate hex string with hyphens for readability
            raw_hex = secrets.token_hex(length)
            key = '-'.join([raw_hex[i:i+4] for i in range(0, len(raw_hex), 4)])
        elif format_type == 'base64':
            # Generate base64 string without hyphens
            key = base64.b64encode(secrets.token_bytes(length)).decode('utf-8')
        else:
            return jsonify({'error': 'Invalid format'}), 400
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(key)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Analyze key strength
        strength_metrics = analyze_key_strength(key)
        
        return jsonify({
            'key': key,
            'metrics': strength_metrics,
            'qr_code': f'data:image/png;base64,{qr_base64}',
            'format': format_type
        })
        
    except ValueError as e:
        logging.error(f"Value error: {str(e)}")
        return jsonify({'error': 'Invalid input parameters'}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print(f"Server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)  