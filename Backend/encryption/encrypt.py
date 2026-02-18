import os, base64
from dotenv import load_dotenv
from Crypto.Cipher import AES

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
       
       while len(text) % 16 != 0:
          text += ' '
       
       encrypt = cipher.encrypt(text.encode('utf-8'))
       res = iv + encrypt

       return base64.b64encode(res).decode('utf-8')
     
     except Exception as e:
        print(f"Error encryption text: {e}")
        return False

