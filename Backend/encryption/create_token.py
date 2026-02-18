#This file create token for the encryption 
import secrets, base64
bytes_key = secrets.token_bytes(32)
key = base64.b64encode(bytes_key).decode('utf-8')
print(key)