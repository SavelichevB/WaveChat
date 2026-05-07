from config import WorkData
from db import GetConnect
from encryption.encrypt import Encrypt
import datetime

limit_message_chat = 1000 #Limit get message
limit_user_chats = 800 #Limit get chats

class GetMessage:
 def __init__(self):
    self.db = GetConnect()
    self.wd = WorkData()
    self.em = Encrypt()

 def get_private_chats(self, client_one, client_two): #Function for the GET PERSON CHATS 
   try:
     if not client_one or not client_two: return False, False

     chats_data = self.db.query('''SELECT rq1.chat_id
     FROM chat_participants rq1
     INNER JOIN chat_participants rq2 ON rq1.chat_id = rq2.chat_id
      WHERE rq1.user_id = %s AND
        rq2.user_id = %s AND
        rq1.user_id != rq2.user_id''', (client_one, client_two))
    
     
     if not chats_data or len(chats_data) < 1: return True, False

     return True, chats_data[0]['chat_id']
     
   except Exception as e:
     print(f"Error Get Private Chats -- {e}")
     return False, False
   
 def get_private_message(self, chat_id, client_id): #Function for the GET PERSON MESSAGES 
   try:
     if not chat_id or not client_id: return False, "Error Chat or Client not found"

     check = self.check_user_chat(client_id, chat_id)
     if not check: return False, 'User not found in chat'

     chat_message = self.db.query('''SELECT id, from_id, text, time, is_read, is_edit
      FROM chat_message WHERE chat_id=%s 
      ORDER BY time ASC
      LIMIT %s''', (chat_id, limit_message_chat)) 
     if not chat_message: return True, []

     for msg in chat_message:
       if msg['text']:
         msg['text'] = self.em.decrypt_message(msg['text'])

     return True, chat_message
   except:
     return False, "Server Error"   
   
 def get_users_chats(self, client_id): #Function for the GET USER CHATS
   try:
     if not client_id: return False, "Client_ID not found"

     id_chats = self.db.query('''SELECT chat_id
       FROM chat_participants WHERE user_id=%s
        ORDER BY joined_at DESC
        LIMIT %s''', (client_id, limit_user_chats))
     if not id_chats or len(id_chats) < 1: return True, []

     user_chats = []

     for chat in id_chats: 
       chat_id = chat['chat_id']

       chat_info = self.db.query('''SELECT type, created_at, name 
          FROM chats WHERE id=%s
       ''', (chat_id,))

       if not chat_info: continue

       chat_type = chat_info[0]['type']
       created_at = chat_info[0]['created_at']
       chat_name = chat_info[0]['name']

       if chat_type == 0:
         other_user = self.db.query('''SELECT user_id
          FROM chat_participants WHERE chat_id=%s AND user_id !=%s
             LIMIT 1''', (chat_id, client_id))
         if not other_user: chat_name = 'Unknown'

         other_id = other_user[0]['user_id']
         user_data = self.db.query('''SELECT username, name 
            FROM accounts WHERE id=%s''', (other_id,))
         if not user_data[0]['name']: chat_name = user_data[0]['username']

         chat_name = user_data[0]['name'] or user_data[0]['username'] or 'Unknown'
         chat_username = user_data[0]['username']
         clean_username = self.wd.decrypt_meta(chat_username)
         chat_name = self.wd.decrypt_meta(chat_name)

       last_message = self.db.query('''SELECT from_id, text, time 
         FROM chat_message 
         WHERE chat_id=%s 
          ORDER BY time DESC 
            LIMIT 1''', (chat_id,))
         
       last_message_text = None
       last_message_time = None
       last_message_sender = None

       if last_message:
            if last_message[0]['text']: 
              last_message_text = self.em.decrypt_message(last_message[0]['text']) if last_message[0]['text'] else "File"
            last_message_time = last_message[0]['time']
            if not last_message_time:
               last_message_time = created_at
            last_message_sender = last_message[0]['from_id']

       notification = 0

       notific_res = self.db.query('''SELECT COUNT(*) as count
        FROM chat_message
          WHERE chat_id=%s AND is_read=%s AND from_id !=%s''', 
          (chat_id, 0, client_id))
       
       notification = notific_res[0]['count'] if notific_res else 0
     
       user_chats.append({
              'chat_id': chat_id,
              'name': chat_name,
              'username': clean_username or '',
              'type': chat_type,
              'last_message': last_message_text,
              'last_sender_id': last_message_sender or None,
              'last_message_time': last_message_time or None,
              'unread': notification or 0
          })
       user_chats.sort(key=lambda x: x['last_message_time'] or datetime.datetime.min, reverse=True)
        
     return True, user_chats
   except Exception as e:
     print(e)
     return False, "Server Error"
   
 def get_client_messages(self, client_one, client_two): #Function for the GET MESSAGES
   try:
     if not client_one or not client_two: return False
     if client_one == client_two: return False

     log, chat_id = self.get_private_chats(client_one, client_two)
     if log == False or chat_id == False: return False
     chat_id = int(chat_id)

     log, messages = self.get_private_message(chat_id)
     if log == False: return False
     if messages == False: return []
     return messages
   except:
     return False
   
 def check_user_chat(self, client_id, chat_id):
   try:
     if not client_id or not chat_id: return False
     check = self.db.query('''SELECT 1
     FROM chat_participants WHERE chat_id=%s AND user_id=%s''', (chat_id, client_id))
     if not check: return False
     return True
   except:
     return False
   
 def get_chat_info(self, chat_id, client_id):
    try:
        if not self.check_user_chat(client_id, chat_id):
            return False, "Access not found"
        
        chat = self.db.query('SELECT type, name FROM chats WHERE id=%s', (chat_id,))
        if not chat:
            return False, "Chat not found"
        
        chat_type = chat[0]['type']
        chat_name = chat[0]['name']
        
        if chat_type == 0:
            other_user = self.db.query('''
                SELECT user_id FROM chat_participants 
                WHERE chat_id=%s AND user_id != %s
                LIMIT 1
            ''', (chat_id, client_id))
            
            if other_user:
                user_data = self.db.query('''
                    SELECT username, name FROM accounts WHERE id=%s
                ''', (other_user[0]['user_id'],))
                
                if user_data:
                    chat_name = user_data[0]['name'] or user_data[0]['username']
                    if chat_name:
                        chat_name = self.wd.decrypt_meta(chat_name)
        
        return True, {
            'chat_id': chat_id,
            'name': chat_name or 'Unknown',
            'user_id': other_user[0]['user_id'] or None, 
            'type': chat_type
        }
        
    except Exception as e:
        print(f"Error get chat info: {e}")
        return False, "Server Error"
    

class PostMessage(GetMessage):
  def __init__(self):
    super().__init__()

  def send_chat_message(self, chat_id, client_id, text):
    try:
       if not client_id or not chat_id or not text: return False, "ID or TEXT not found"
       if len(text) <= 0: return False, 'Text < 1 len'

       participants = self.db.query('''SELECT user_id FROM chat_participants 
                                        WHERE chat_id=%s''', (chat_id,))
       if len(participants) == 1 and participants[0]['user_id'] == client_id:
           return False, "Error, send message to yourself"
       
       if self.check_user_chat(client_id, chat_id) == False: return False, "Client not found in chat"

       encrypt_text = self.em.encrypt_message(text)
       if not encrypt_text: return False, 'Encryption Error'

       send_data = self.db.execute('''INSERT INTO chat_message
       (chat_id, from_id, text) VALUES (%s, %s, %s)''', (chat_id, client_id, encrypt_text))
       if not send_data: return False, 'Not send data'

       return True, send_data
    except Exception as e:
      return False, 'Server Error'
    
  def create_private_chat(self, client_one, client_two):
    try:
      if not client_one or not client_two: return False, "Client One/Two not found"
      if client_one == client_two: return False, "Incorrect user, you"

      log, chat_id = self.get_private_chats(client_one, client_two)
      if log == False: return False, "Server Error"
      if chat_id != False: return False, "Chat was already created"

      new_chat_id = self.db.execute('''INSERT INTO chats 
        (type) VALUES (%s)''', (0,))
      
      if not new_chat_id: return False, "Server Error" 
      new_client = self.db.execute('''INSERT INTO chat_participants 
        (chat_id, user_id) VALUES (%s, %s)''', (new_chat_id, client_one))
      if not new_client: return False, "Server Error"
      new_client = self.db.execute('''INSERT INTO chat_participants 
        (chat_id, user_id) VALUES (%s, %s)''', (new_chat_id, client_two))
      if not new_client: return False, "Server Error"  

      return True, new_chat_id 
    except:
      return False, 'Server Error'

  def send_private_message(self, receiver_id, sender_id, text):
    try:
      if not receiver_id or not sender_id or not text: return False, "ID or TEXT not found"
      if sender_id == receiver_id: return False, "Incorrect user, you", None

      log, chat_id = self.get_private_chats(receiver_id, sender_id)
      if log == False: return False, "Server Error", None

      if chat_id == False: 
        new_chat, chat_id = self.create_private_chat(receiver_id, sender_id)
        if not new_chat: return False, "Server Error", None
        if not chat_id: return False, "Chat ID not found", None
        chat_id = int(chat_id)

      res, id =  self.send_chat_message(chat_id, sender_id, text)
      if not res: return False, id, None

      return True, id, chat_id

    except Exception as e:
      return False, "Server Error", None
    
  def read_message_chat(self, client_id, chat_id): 
     try:
        if not client_id or not chat_id: return False, 'Data not found'

        res = self.db.execute('''UPDATE chat_message 
          SET is_read=%s WHERE
            chat_id=%s AND from_id !=%s AND is_read=%s''', 
              (1, chat_id, client_id, 0))
        return True, res
     except Exception as e:
        print(f"Error read message: {e}")
        return False, 'Server Error'
     
    
  def delete_message(self, client_id, message_id):
      try:
         if not client_id or not message_id: return False, 'Data not found'
         
         try:
           res = self.db.query('''SELECT chat_id FROM
            chat_message WHERE from_id=%s AND id=%s''', (client_id, message_id))
           if not res: return False, 'Message not found' 
           chat_id = int(res[0]['chat_id'])
           res = self.db.execute('''DELETE FROM chat_message
             WHERE id=%s AND from_id=%s''', (message_id, client_id))
           if not res: return False, 'DB data not found'
         except:
            return False, 'Valid delete message'
         
         return True, chat_id
      
      except Exception as e:
         print(f"Error deleted message: {e}")
         return False, 'Server Error'
