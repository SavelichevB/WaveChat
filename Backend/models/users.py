from config import WorkData
from db import GetConnect

class UserData:
    def __init__(self):
        self.db = GetConnect()
        self.wd = WorkData()
    
    def get_all_data(self, client_id):
        try:
         if not client_id: return False, 'Client id not found'

         data = self.db.query('''SELECT username, name, email, created_at 
          FROM accounts WHERE id=%s''', (client_id,)) 
         if not data: return False, 'Data not found'
         data = data[0]

         if data['username']:
             data['username'] = self.wd.decrypt_meta(data['username'])
         if data['email']: 
             data['email'] = self.wd.decrypt_meta(data['email'])

         return True, data
        except Exception as e:
           print(f"Error get user data: {e}")
           return False, 'Server Error'
    
    def get_id_username(self, username):
       try:
          if not username: return False, 'Data not found'

          username = username.strip().lower()
          encrypt_username = self.wd.encrypt_meta(username)
          if not encrypt_username: return False, 'Encrypt error'

          data = self.db.query('''SELECT id FROM accounts
            WHERE username=%s''', (encrypt_username,))
          if not data or len(data) == 0:
            return False, 'Account not found'

          return True, data[0]['id']

       except Exception as e:
          print(f"Error get id (username): {e}")
          return False, 'Server Error'
    
    def get_open_data(self, client_id):
       try:
          if not client_id: return False,  'Client not found'

          data = self.db.query('''SELECT id, username, name 
           FROM accounts WHERE id=%s''', (client_id,)) 
          
          if not data: return False, 'Data not found'
          data = data[0]   

          if data['username']:
            data['username'] = self.wd.decrypt_meta(data['username'])
          if data['name']:
            data['name'] = self.wd.decrypt_meta(data['name'])

          return True, data
       except Exception as e:
           print(f"Error get open data: {e}")
           return False, 'Server Error'     
        
    def edit_email(self, client_id, email):
       try:
          if not client_id or not email: return False, 'Client or Email not found'
          if self.wd.ValidationData(3, data=[email]) == False: return False, 'Email incorrect' 

          encrypt_email = self.wd.encrypt_meta(email)
          if not encrypt_email: return False, 'Server Error'

          data = self.db.execute('UPDATE accounts SET email=%s WHERE id=%s', (encrypt_email, client_id))
          
          return True, data
       except Exception as e:
           print(f"Error edit email: {e}")
           return False, 'Server Error'     
  