from config import WorkData
from db import GetConnect
from werkzeug.security import generate_password_hash, check_password_hash

class Auth:

  def __init__(self):
    self.db = GetConnect()
    self.wd = WorkData()
  
  def Registation(self, username, password):
     try:  
       if not username or not password: return False, "Username or Password not found"
       if self.wd.ValidationData(1, data=[username]) == False or self.wd.ValidationData(2, data=[password]) == False: return False, "Invalid username or password"  

       username_crypt = self.wd.encrypt_meta(username) #Encrypt username

       check_auth = self.db.query("SELECT id FROM accounts WHERE username=%s", (username_crypt,))
       if len(check_auth) > 0: return False, "Username already exists"

       hash_password = generate_password_hash(password)

       request_data = self.db.execute("""INSERT INTO accounts
       (username, password) VALUES (%s, %s)""", (username_crypt, hash_password))
       if request_data == False: return False, "Very Good"

       return True, request_data

     except Exception as e:
        print(f"Fatal Error for registation: {e}")
        return False, "Fatal Error"
     
  def Login(self, username, password):
     try:
        if not username or not password: return False, "Username or Password not found"
        if self.wd.ValidationData(1, data=[username]) == False or self.wd.ValidationData(2, data=[password]) == False: return False, "Invalid username or password"  

        username_crypt = self.wd.encrypt_meta(username) #Encrypt username

        search_user = self.db.query("SELECT id, password FROM accounts WHERE username=%s", (username_crypt,))
        if len(search_user) < 1: return False, "User not found"
        search_user = search_user[0]

        if check_password_hash(search_user['password'], password):
           return True, search_user['id']
        
        return False, "Invalid password"
     
     except Exception as e:
        print(f"Fatal Error for login: {e}")
        return False, "Fatal Error"
     