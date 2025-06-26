import hashlib
import base64
from cryptography.fernet import Fernet
from stegano import lsb

# === AES Key Generator ===
def generate_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

# === Encrypt Message ===
def encrypt_message(message, password):
    key = generate_key(password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(message.encode())
    return encrypted.decode()

# === Decrypt Message ===
def decrypt_message(encrypted_message, password):
    key = generate_key(password)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_message.encode())
    return decrypted.decode()

# === Hide message inside image ===
def hide_message_in_image(image_path, message, password, output_path):
    encrypted = encrypt_message(message, password)
    secret_image = lsb.hide(image_path, encrypted)
    secret_image.save(output_path)
    return output_path

# === Reveal and decrypt message from image ===
def reveal_message_from_image(image_path, password):
    hidden = lsb.reveal(image_path)
    if not hidden:
        raise ValueError("No hidden message found.")
    return decrypt_message(hidden, password)
