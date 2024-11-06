document.addEventListener('DOMContentLoaded', () => {
    const lengthInput = document.getElementById('length');
    const generateBtn = document.getElementById('generateBtn');
    const secretKeyInput = document.getElementById('secretKey');
    const toggleVisibilityBtn = document.getElementById('toggleVisibility');
    const copyBtn = document.getElementById('copyBtn');
    const outputSection = document.getElementById('outputSection');
    const formatSelect = document.getElementById('format');

    function updateStrengthMeter(length) {
        const strengthBar = document.getElementById('strengthIndicator');
        const strengthText = document.getElementById('strengthText');
        let percentage, label;
        
        if (length < 16) {
            percentage = 33;
            label = 'Weak';
            strengthBar.style.width = '33%';
            strengthBar.style.backgroundColor = '#ff4444';
        } else if (length < 32) {
            percentage = 66;
            label = 'Medium';
            strengthBar.style.width = '66%';
            strengthBar.style.backgroundColor = '#ffa700';
        } else {
            percentage = 100;
            label = 'Strong';
            strengthBar.style.width = '100%';
            strengthBar.style.backgroundColor = '#00C851';
        }
        
        strengthText.textContent = `${label} (${percentage}%)`;
    }

    function generateQRCode(text) {
        const qrContainer = document.getElementById('qrcode');
        qrContainer.innerHTML = `
            <div class="qr-title">
                <i class="fas fa-qrcode"></i>
                Scan me to get the key
            </div>
        `; // Clear previous QR code and add title
        qrContainer.style.display = 'block';
        
        // Create a new canvas element
        const canvas = document.createElement('canvas');
        qrContainer.appendChild(canvas);
        
        QRCode.toCanvas(canvas, text, {
            width: 200,
            margin: 2,
            color: {
                dark: '#1a73e8',
                light: '#ffffff'
            }
        }, function (error) {
            if (error) console.error(error);
        });
    }

    async function generateKey() {
        try {
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    length: parseInt(lengthInput.value),
                    format: formatSelect.value
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                secretKeyInput.value = data.key;
                outputSection.style.display = 'block';
                updateStrengthMeter(parseInt(lengthInput.value));
                generateQRCode(data.key);
            } else {
                alert(data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the key.');
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-key"></i> Generate Secure Key';
        }
    }

    generateBtn.addEventListener('click', generateKey);

    toggleVisibilityBtn.addEventListener('click', () => {
        const isBlurred = secretKeyInput.classList.toggle('blur');
        toggleVisibilityBtn.querySelector('i').classList.toggle('fa-eye');
        toggleVisibilityBtn.querySelector('i').classList.toggle('fa-eye-slash');
    });

    copyBtn.addEventListener('click', () => {
        secretKeyInput.select();
        document.execCommand('copy');
        
        const icon = copyBtn.querySelector('i');
        icon.className = 'fas fa-check';
        
        setTimeout(() => {
            icon.className = 'fas fa-copy';
        }, 1500);
    });
}); 