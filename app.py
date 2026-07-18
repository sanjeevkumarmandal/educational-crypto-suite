import streamlit as st
import hashlib
from PIL import Image
import io

# Setup web page configuration
st.set_page_config(page_title="Educational Crypto Suite", page_icon="🔐", layout="wide")

st.title("🔐 Educational Cryptography & Steganography Sandbox")
st.write("""
Welcome! This tool is designed to help you visualize core security concepts: **Data Integrity (Hashing)**, 
**Symmetric Encryption (XOR)**, and **Information Hiding (Steganography)**. 
Explore the tabs below to see how data changes at the binary level.
""")

# --- Core Cryptographic Logic ---
def generate_sha256(message: str) -> str:
    return hashlib.sha256(message.encode()).hexdigest()

def xor_cipher(data: str, key: str) -> str:
    extended_key = (key * (len(data) // len(key) + 1))[:len(data)]
    return "".join(chr(ord(c) ^ ord(k)) for c, k in zip(data, extended_key))

def encode_image(img, secret_text, secret_key):
    encrypted_text = xor_cipher(secret_text, secret_key)
    data_to_hide = encrypted_text + "###END###"
    binary_data = ''.join(format(ord(char), '08b') for char in data_to_hide)
    
    img = img.convert('RGB')
    pixels = img.load()
    width, height = img.size
    
    data_index = 0
    data_len = len(binary_data)
    
    for y in range(height):
        for x in range(width):
            if data_index < data_len:
                r, g, b = pixels[x, y]
                r = (r & ~1) | int(binary_data[data_index])
                data_index += 1
                pixels[x, y] = (r, g, b)
            else:
                break
        if data_index >= data_len:
            break
    return img

def decode_image(img, secret_key):
    pixels = img.load()
    width, height = img.size
    
    binary_bits = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_bits += str(r & 1)
            
    all_chars = ""
    for i in range(0, len(binary_bits), 8):
        byte = binary_bits[i:i+8]
        if len(byte) == 8:
            all_chars += chr(int(byte, 2))
            
    if "###END###" in all_chars:
        encrypted_payload = all_chars.split("###END###")[0]
        return xor_cipher(encrypted_payload, secret_key)
    return "Error: No structural hidden message markers detected!"

# --- UI Tab Layout ---
tab1, tab2, tab3 = st.tabs(["🔒 SHA-256 Hashing", "🔑 Symmetric XOR", "🖼️ LSB Steganography"])

# Tab 1: Hashing
with tab1:
    st.header("Data Integrity via One-Way Hashing")
    st.info("💡 **Educational Note:** A cryptographic hash is a unique digital fingerprint. Changing even a single letter completely changes the hash value, proving the data was altered.")
    
    hash_input = st.text_input("Enter text to hash:", value="Hello World")
    if hash_input:
        result_hash = generate_sha256(hash_input)
        st.success(f"**SHA-256 Hash Output:** `{result_hash}`")

# Tab 2: XOR Cipher
with tab2:
    st.header("Symmetric Encryption Concepts")
    st.info("💡 **Educational Note:** Symmetric encryption uses the same secret key to encrypt and decrypt. Try encrypting a message, copying the output, and using the same key to decrypt it!")
    
    col1, col2 = st.columns(2)
    with col1:
        msg = st.text_input("Plaintext Message:", value="Top Secret Message")
        key = st.text_input("Secret Key:", value="MySecretKey", type="password")
        if st.button("Encrypt"):
            enc = xor_cipher(msg, key)
            st.code(f"Ciphertext (Scrambled string): {repr(enc)}")
            
    with col2:
        cipher_input = st.text_input("Ciphertext to Decrypt (Paste value here):")
        decrypt_key = st.text_input("Decryption Key:", value="MySecretKey", type="password")
        if st.button("Decrypt"):
            try:
                # Evaluating raw string representation safely for educational display
                raw_cipher = eval(cipher_input) if cipher_input.startswith("'") or cipher_input.startswith('"') else cipher_input
                dec = xor_cipher(raw_cipher, decrypt_key)
                st.success(f"Decrypted Plaintext: `{dec}`")
            except Exception as e:
                st.error("Please enter a valid scrambled ciphertext string format.")

# Tab 3: Steganography
with tab3:
    st.header("LSB Steganography (Hiding Data inside Pixels)")
    st.info("💡 **Educational Note:** This technique alters the **Least Significant Bit** of the image's red color channels. The changes are so small that the human eye cannot see any difference between the original and the secure carrier image.")
    
    stmode = st.radio("Choose Operation Mode:", ["Encode (Hide Data)", "Decode (Extract Data)"])
    
    if stmode == "Encode (Hide Data)":
        uploaded_file = st.file_uploader("Upload a cover PNG image:", type=["png"])
        secret_msg = st.text_input("Secret Message to Hide:", value="Hidden Data Entry")
        stego_key = st.text_input("Stego Passphrase:", value="SecureKey123", type="password")
        
        if uploaded_file and st.button("Generate Stego Image"):
            image = Image.open(uploaded_file)
            stego_img = encode_image(image, secret_msg, stego_key)
            
            # Save to byte stream for immediate download
            buf = io.BytesIO()
            stego_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.image(stego_img, caption="Generated Stego Image (Looks identical!)", width=300)
            st.download_button(label="📥 Download Stego Image", data=byte_im, file_name="stego_output.png", mime="image/png")
            
    else:
        uploaded_stego = st.file_uploader("Upload a protected Stego PNG image:", type=["png"])
        decode_key = st.text_input("Enter Extraction Passphrase:", type="password")
        
        if uploaded_stego and st.button("Extract Hidden Message"):
            stego_image = Image.open(uploaded_stego)
            extracted_secret = decode_image(stego_image, decode_key)
            st.success(f"**Extracted Plaintext Payload:** `{extracted_secret}`")