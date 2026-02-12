from config import WorkData
from db import GetConnect
from werkzeug.security import generate_password_hash, check_password_hash

class Auth:
  
  def Registation(self, username, password):
     try:  
       db = GetConnect()
       wd = WorkData()

       if not username or not password: return False, "Username or Password not found"
       if wd.ValidationData(1, data=[username]) == False or wd.ValidationData(2, data=[password]) == False: return False, "Invalid username or password"    
       check_auth = db.query("SELECT id FROM accounts WHERE username=%s", (username,))
       if len(check_auth) > 0: return False, "Username already exists"

       hash_password = generate_password_hash(password)

       request_data = db.execute("""INSERT INTO accounts
       (username, password) VALUES (%s, %s)""", (username, hash_password))
       if request_data == False: return False, "Very Good"

       return True, request_data

     except Exception as e:
        print(f"Fatal Error for registation: {e}")
        return False, "Fatal Error"