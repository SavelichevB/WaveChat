import os, base64
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class Encrypt:
  
  def __init__(self):
     try:
       load_dotenv()
       key_64 = os.getenv('ENCRYPTION_KEY')
       self._key = base64.b64decode(key_64)
     except Exception as e:
        print(f'Bytes key not found: {e}')
  
  def encrypt_message(self, text):
     try:
       if not self._key or not text: return False   

       iv = os.urandom(16)
       cipher = AES.new(self._key, AES.MODE_CBC, iv)
       
       text_bytes = text.encode('utf-8')
       padded_text = pad(text_bytes, AES.block_size)
       
       encrypt = cipher.encrypt(padded_text)
       res = iv + encrypt

       return base64.b64encode(res).decode('utf-8')
     
     except Exception as e:
        print(f"Error encryption text: {e}")
        return False
     
  def decrypt_message(self, data):
     try:
        if not self._key or not data: return False
         
        encrypt_text = base64.b64decode(data)
        if len(encrypt_text) < 16: return False

        iv = encrypt_text[:16]
        cipher_text = encrypt_text[16:]

        cipher = AES.new(self._key, AES.MODE_CBC, iv)

        decrypted = cipher.decrypt(cipher_text)
        pad_text = unpad(decrypted, AES.block_size)
        text = pad_text.decode('utf-8')

        if not text: return False
        return text
     
     except Exception as e:
        print(f"Error decryption text: {e}")
        return data     

