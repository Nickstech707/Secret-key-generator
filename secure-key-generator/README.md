# Secure Key Generator

A web-based cryptographically secure key generator built with Flask and OpenSSL. Generate secure keys for various applications with support for multiple output formats and QR code sharing.

## Features

- **Multiple Output Formats**
  - Alphanumeric (A-Z, a-z, 0-9)
  - Hexadecimal
  - Base64

- **Security Features**
  - OpenSSL-based secure random generation
  - Strength analysis and scoring
  - Configurable key length
  - Entropy measurement

- **User Interface**
  - Clean, modern design
  - Mobile-responsive layout
  - Copy to clipboard functionality
  - Toggle key visibility
  - QR code generation for easy sharing

- **Use Cases**
  - API Authentication Keys
  - Encryption Keys
  - Password Reset Tokens
  - Session Keys
  - JWT Secrets
  - OAuth Client Secrets

## Installation

1. Clone the repository: 
```bash
git clone https://github.com/yourusername/secure-key-generator.git
cd secure-key-generator
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```
## Dependencies

- Flask
- OpenSSL
- qrcode
- Pillow
- Other requirements listed in requirements.txt

## Usage
  1. Start the server:
```bash
python app.py
```
2. Open your browser and navigate to:
```
http://127.0.0.1:5000
```
## API Endpoints

### Generate Key
- **URL**: `/generate`
- **Method**: `POST`
- **Request Body**:

```json
{
"length": 32,
"format": "alphanumeric"
{
"key": "generated_key",
"metrics": {
"strength_score": 85,
"strength_label": "Strong",
"length": 32
},
"qr_code": "base64_encoded_qr_image"
}
```

## Security Features

### Rate Limiting
- 50 requests per hour per IP address
- Configurable window and request limits

### Key Generation
- Uses Python's `secrets` module for cryptographically secure generation
- Supports various output formats with appropriate security measures
- Key strength analysis based on length and character composition

## Development

### Project Structure
```
secure-key-generator/
├── app.py
├── static/
│ ├── css/
│ │ └── styles.css
│ └── js/
│ └── script.js
├── templates/
│ └── index.html
└── requirements.txt
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenSSL for secure random number generation
- Flask for the web framework
- QRCode.js for QR code generation

## Support

For support, please open an issue in the GitHub repository or contact [your-email].

## Author

[Nicholas Muturi](https://github.com/Nickstech707)
