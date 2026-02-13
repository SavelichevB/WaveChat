from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import base64
from db import GetConnect

class WorkData:  

 def ValidationData(self, type, data):
  
  forbidden_symbols = [
        '<', '>', '&', "'", '"', ';', '--', '=', 
        '/*', '*/', '@@', 'xp_', 'sp_',
        'javascript:', 'onclick=', 'onload=',
        'union select', 'drop table', 'insert into'
    ]

  for item in data:
      if isinstance(item, str):
          for symbol in forbidden_symbols:
              if symbol in item:
                  return False
              
  if int(type) == 1: # USERNAME VALIDATION --
     for item in data:
       if isinstance(item, str):
         if len(item) < 3 or len(item) > 100:
           return False
     return True
  elif int(type) == 2: # PASSWORD VALIDATION --
     for item in data:
       if isinstance(item, str):
         if len(item) < 8 or len(item) > 100:
           return False
     return True
  elif int(type) == 3: # EMAIL VALIDATION --
     for item in data:
       if isinstance(item, str):
         if len(item) < 3 or len(item) > 100:
           return False
         parts = item.split('@')
         if len(parts) != 2:
           return False
     return True
  elif int(type) == 4: # OTHER VALIDATION --
     for item in data:
       if isinstance(item, str):
         if len(item) < 8 or len(item) > 300:
           return False
     return True
  elif int(type) == 5: # OTHER VALIDATION --
     for item in data:
       if isinstance(item, str):
         if len(item) < 3 or len(item) > 400:
           return False
     return True
  else: # OTHER VALIDATION --
     for item in data:
       if isinstance(item, str):
         if len(item) < 3 or len(item) > 1000:
           return False
     return True
  
 def encrypt_meta(self, data):
   if not data: return False
   try:
     data_byte = data.encode('utf-8')
     data_crypt = base64.b64encode(data_byte).decode('utf-8')
     if data_crypt: return data_crypt
   except:
     print("Error Encrypt meta data")
     return False

 def decrypt_meta(self, data):
   if not data: return False
   try:
     decoded = base64.b64decode(data).decode('utf-8')
     return decoded
   except:
     print("Error Decrypt meta data")
     return False
    