from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from flask_socketio import SocketIO, emit
from datetime import timedelta
from collections import defaultdict
import datetime

from config import cookie_token
from models.auth import Auth
from models.message import GetMessage, PostMessage
from models.users import UserData

#Create app:
app = Flask(__name__)
app.config['SECRET_KEY'] = 'WaveMini'

#Cors:
CORS(app, 
     supports_credentials=True, 
     origins=["http://localhost:5173", "http://192.168.0.18:5173", "http://192.168.0.25:5173", "http://192.168.0.28:5173"],
     allow_headers=["Content-Type", "Authorization", "Cookie", "X-Requested-With"],
     expose_headers=["Set-Cookie"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
protocol = False  #HTTPS or HTTP, if HTTPS => true

#JWT Config:
app.config['JWT_SECRET_KEY'] = 'WaveMini'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

#Objects:
auth = Auth()
gm = GetMessage()
pm = PostMessage()
ud = UserData()

#====Endpoints====: 
@app.route('/', methods=['GET'])
def Home():
 return jsonify({
   'service': 'WaveChat API',
   'status': 'online',
   'version': '1.0.0.0'
 }), 200  


#====Point==Auth=====:
@app.route('/auth/reg', methods=['POST'])
def registr_users():
  try:
    client_username = request.json.get('username')
    client_password = request.json.get('password')
    if not client_username or not client_password: return jsonify({'Info': 'Username or Password not found'}), 400

    data_reg, log = auth.Registation(client_username, client_password)
    if not data_reg: return jsonify({'Info': 'Username or Password incorrect for the registation', 'Log': log}), 400
    access_token = create_access_token(identity=str(log))
    if not access_token: return jsonify({'Info': 'Error app for regisration'}), 400

    response = make_response(jsonify({'Success': True}))
    response.set_cookie(
      'token',
      access_token,
      httponly=True,
      secure=protocol,
      samesite='Lax',
      max_age=timedelta(days=7),
      path='/',
      domain='localhost' 
    )

    return response, 200
    
  except Exception as e:
    return jsonify({
      'Info': 'Error app for regisration'
    }), 500
  
@app.route('/auth/login', methods=['POST'])
def login_user():
  try:
    client_username = request.json.get('username')
    client_password = request.json.get('password')
    if not client_username or not client_password: return jsonify({'Info': 'Username or Password not found'}), 400

    data_reg, log = auth.Login(client_username, client_password)
    if not data_reg: return jsonify({'Info': 'Username or Password incorrect for the login', 'Log': log}), 400
    if int(log) < 0: return jsonify({'Info': 'Server Error for the login'})
    access_token = create_access_token(identity=str(log))
    if not access_token: return jsonify({'Info': 'Error app for login'}), 400

    response = make_response(jsonify({'Success': True}))
    response.set_cookie(
      'token',
      access_token,
      httponly=True,
      secure=protocol,
      samesite='Lax',
      max_age=timedelta(days=7),
      path='/',
      domain='localhost' 
    )

    return response, 200

  except Exception as e:
    return jsonify({
      'Info': 'Error app for login'
    }), 500

@app.route('/auth/check', methods=['GET'])
@cookie_token
def verify_token():
  try:
    client_id = request.client_id
    if not client_id or int(client_id) < 0: return jsonify({'Info': 'Error verify token'}), 403
    return jsonify({'Success': True, 'Client_id': client_id}), 200
  except Exception as e:
    print(e)
    return jsonify({'Info': 'Fatal error verify token'}), 500

@app.route('/auth/logout', methods=['POST'])
def logout():
  try:
    if request.method == 'OPTIONS':
      return '', 200
    
    responce = make_response(jsonify({'Success': True}))
    responce.set_cookie(
      'token',
      '',
      httponly=True,
      secure=protocol,
      samesite='Lax',
      max_age=0,
      path='/',
      domain='localhost'      
    )
    return responce, 200
    
  except Exception as e:
    return jsonify({'Success': False, 'Info': 'Server Error logout'})

  
  
  
#====Point==Message====:

@app.route('/message/send/id', methods=['POST'])
@cookie_token
def send_message():
  try:
    sender_id = request.client_id
    receiver_id = request.json.get('from')
    text = request.json.get('text')  

    if int(sender_id) == int(receiver_id): return jsonify({'Info': 'Error send message', 'Log': 'Error send message yourself'}), 400

    check, log = pm.send_private_message(receiver_id, sender_id, text)  

    if not check: return jsonify({'Info': 'Error send message', 'Log': log}), 400

    return jsonify({
      'Success': True,
      'Info': 'Message was senden'
    }), 200
  
  except:
    return jsonify({'Info': 'Fatal error send message'}), 500

@app.route('/message/send/chat', methods=['POST'])
@cookie_token
def send_message_chat():
  try:
     sender_id = request.client_id
     chat_id = request.json.get('chat_id')
     text = request.json.get('text')

     check, log = pm.send_chat_message(chat_id, sender_id, text)
     if not check: return jsonify({'Info': 'Error send message', 'Log': log}), 400
     if log == False: return jsonify({'Info': 'Error send message', 'Log': log}), 400

     return jsonify({
      'Success': True,
      'Info': 'Message was senden'
     }), 200
  except:
     return jsonify({'Info': 'Fatal error send message'}), 500
  
@app.route('/message/get', methods=['POST'])
@cookie_token
def get_message():
  try:
    client_id = request.client_id
    chat_id = request.json.get('chat_id')

    check, data = gm.get_private_message(chat_id, client_id) 
    if not check: return jsonify({'Info': 'Error get messages'}), 400
    if not data: return jsonify({'Success': False}), 200

    return jsonify({
      'Success': True,
      'Data': data,
      'Count': len(data)
    }), 200
  except:
    return jsonify({'Info': 'Fatal error get message'}), 500
  
#====Point==Chats====:

@app.route('/chat/info', methods=['POST'])
@cookie_token
def get_chat_info():
    try:
        client_id = request.client_id
        chat_id = request.json.get('chat_id')
        
        if not client_id or not chat_id:
            return jsonify({'Info': 'Forbidden'}), 403
        
        check, info = gm.get_chat_info(chat_id, client_id)
        if not check:
            return jsonify({'Info': 'Error get chat info'}), 400
        
        return jsonify({
            'Success': True,
            'Data': info
        }), 200
    except:
        return jsonify({'Info': 'Fatal error'}), 500

@app.route('/chat/get', methods=['GET'])
@cookie_token
def get_chat():
  try:
    client_id = request.client_id

    if not client_id: return jsonify({'Info': 'Forbidden'}), 403

    check, chats = gm.get_users_chats(client_id)
    if not check: return jsonify({'Info': 'Error Get user chats', 'Log': chats}), 400
    
    if not chats: return jsonify({'Success': True, 'Data': [], 'Count': 0}), 200
    return jsonify({
      'Success': True, 
      'Data': chats,
      'Count': len(chats)
    }), 200
  except:
    return jsonify({'Info': 'Fatal error get chats'}), 500
  
@app.route('/chat/username', methods=['POST'])
@cookie_token
def get_chat_id():
  try:
      client_id = int(request.client_id)
      username = request.json.get('username')

      if not client_id: return jsonify({'Info': 'Forbidden'}), 403
      if not username: return jsonify({'Success': False, 'Info': 'Data not found'}), 400

      username = username.strip().lower()

      status, data = ud.get_id_username(username)
      if not status: return jsonify({'Info': f'Error, {data}'}), 500
  
      if not data: return jsonify({
        'Success': False,
        'Data': 0
        }), 200
      client_two = int(data)

      status, data = gm.get_private_chats(client_id, client_two)
      if not status: return jsonify({'Info': f'Error, {data}'}), 500
      if not data: 
        return jsonify({
          'Success': True,
          'Data': {
            'client_id': client_two,
            'chat_id': None
          }
        })
      
      return jsonify({
        'Success': True,
        'Data': {
          'client_id': client_two,
          'chat_id': int(data)
        }
      }), 200      

  except Exception:
       return jsonify({'Info': 'Error get id, data: username'}), 500
  
#====Point==User====:

@app.route('/users/me', methods=['GET'])
@cookie_token
def get_users_me():
  try:
    client_id = request.client_id
    if not client_id: return jsonify({'Info': 'Forbidden'}), 403

    check, data = ud.get_all_data(client_id)
    if not check: return jsonify({'Info': 'Error Get user data', 'Log': data}), 400

    return jsonify({
      'Success': True, 
      'Data': data
    }), 200    
  except:
    return jsonify({'Info': 'Fatal error get chats'}), 500
  
@app.route('/users/username/get', methods=['POST'])
def get_username_user():
  try:
    username = request.json.get('username')
    if not username: return jsonify({'Info': 'Not username, data not found'}), 400

    status, data = ud.get_id_username(username)
    if status: 

      return jsonify({
        'Success': True, 
        'Data': int(data)
      }), 200   

    else: return jsonify({'Info': f'Data error, {data}'}), 400

  except:
      return jsonify({'Info': 'Fatal error get user id (username)'}), 500

@app.route('/users/get', methods=['POST'])
def get_users_open():
  try:
    client_id = request.json.get('id')
    if not client_id: return jsonify({'Info': 'Forbidden'}), 403

    check, data = ud.get_open_data(client_id)
    if not check: return jsonify({'Info': 'Error Get user data', 'Log': data}), 400

    return jsonify({
      'Success': True, 
      'Data': data
    }), 200    
  except:
    return jsonify({'Info': 'Fatal error get users'}), 500
  

#WebSocket :
socket = SocketIO(app, cors_allowed_origins='*')

connected_users = defaultdict(list)

@socket.on('connect')
def socket_connect():
  print(f'Client connected: {request.sid}')

@socket.on('disconnect')
def socket_disconnect():
  print(f'Client disconnected: {request.sid}')
  for uid, sid_list in list(connected_users.items()):
     if request.sid in sid_list:
        sid_list.remove(request.sid)
        if not sid_list:
          del connected_users[uid]
     break
    

@socket.on('join')
@cookie_token
def socket_join(data):
  user_id = request.client_id
  if user_id:
    if request.sid not in connected_users[user_id]:
       connected_users[user_id].append(request.sid)
    print(f'User {user_id} join, ID: {request.sid}')
 

@socket.on('send_message')
def socket_message_send(data):
   try:
        token = request.cookies.get('token')
        if not token:
            socket.emit('ws_error', {'error': 'Not authorized'}, room=request.sid)
            return   
        decoded = decode_token(token)
        from_id = int(decoded.get('sub'))
        if not from_id: 
            socket.emit('ws_error', {'error': 'Not authorized'}, room=request.sid)
            return           

        chat_id = data.get('chat_id')
        to_id = data.get('to_id')
        text = data.get('text')
        temp_id = data.get('temp_id')

        if not chat_id and not to_id: 
            socket.emit('ws_error', {'error': 'None chat_id or to_id', 'temp_id': temp_id}, room=request.sid)
            return
        if not text or not text.strip():
            socket.emit('ws_error', {'error': 'Empty message', 'temp_id': temp_id}, room=request.sid)
            return

        if to_id:
            check, log, db_chat_id  = pm.send_private_message(to_id, from_id, text)  
            if not db_chat_id: 
              socket.emit('ws_error', {
                'error': log,
                'temp_id': temp_id
              }, room=request.sid)
              return     
            chat_id_res = db_chat_id
        else:
            check, log = pm.send_chat_message(chat_id, from_id, text)
            chat_id_res = chat_id

        if check:
             if not to_id:
                res = pm.db.query('''SELECT user_id
                FROM chat_participants 
                WHERE chat_id=%s AND user_id !=%s
                ''', (chat_id, from_id))

                for user_data in res:
                  user_id_str = str(user_data['user_id'])
                  if user_id_str in connected_users:
                   for sid in connected_users[user_id_str]:
                    socket.emit('ws_message', {
                      'id': log if isinstance(log, int) else None,
                      'from_id': from_id,
                      'text': text,
                      'time': datetime.datetime.now().isoformat(),
                      'chat_id': chat_id_res
                    }, room=sid) 
                    print('ws message sender')
             else:
                to_id_str = str(to_id)
                if to_id_str in connected_users:
                 for sid in connected_users[to_id_str]:
                  socket.emit('ws_message', {
                    'id': log if isinstance(log, int) else None,
                    'from_id': from_id,
                    'text': text,
                    'time': datetime.datetime.now().isoformat(),
                    'chat_id': chat_id_res
                  }, room=sid)   
             socket.emit('ws_log', {
              'success': True,
              'temp_id': temp_id,
              'message_id': log,
              'chat_id': chat_id_res
            }, room=request.sid)             
        else:
            socket.emit('ws_error', {
                'error': log,
                'temp_id': temp_id
            }, room=request.sid)

   except Exception as e:
      print(f'Error WebSockets : send_message ({e})')
      emit('ws_error', {'error': 'Server Error'}, room=request.sid)
      return
   
@socket.on('read_message')
def chat_read_message(data):
   try:
    token = request.cookies.get('token')
    if not token:
      socket.emit('ws_read_error', {'error': 'Not authorized'}, room=request.sid)
      return   
    decoded = decode_token(token)
    client_id = int(decoded.get('sub'))
    if not client_id: 
      socket.emit('ws_read_error', {'error': 'Not authorized'}, room=request.sid)
      return   

    chat_id = data.get('chat_id') 

    if not chat_id: 
      socket.emit('ws_read_error', {'error': 'Not found chat_id'}, room=request.sid)
      return    

    check, data = pm.read_message_chat(client_id, chat_id)     

    if check:
       res = pm.db.query('''SELECT user_id
        FROM chat_participants 
        WHERE chat_id=%s AND user_id !=%s''', (chat_id, client_id))
       
       if res: 
          for users in res:
            user_id = str(users['user_id'])
            if user_id in connected_users:  
              for sid in connected_users[user_id]:                          
                socket.emit('ws_chat_read', {
                   'chat_id': chat_id,
                   'count': data
                })

   except Exception as e:
      emit('ws_read_error', {'error': 'Server Error'}, room=request.sid)
      print(f"Error read message, web socket: {e}")
      return
   
@socket.on('del_message')
def socket_del_message(data):
  try:
    token = request.cookies.get('token')
    if not token:
      socket.emit('ws_del_error', {'error': 'Not authorized'}, room=request.sid)
      return   
    decoded = decode_token(token)
    from_id = int(decoded.get('sub'))
    if not from_id: 
      socket.emit('ws_del_error', {'error': 'Not authorized'}, room=request.sid)
      return   

    message_id = data.get('message_id')
    if not message_id:
       socket.emit('ws_del_error', {'error': 'Not message id'}, room=request.sid)
       return

    check, log = pm.delete_message(from_id, message_id)
    if not check:
       socket.emit('ws_del_error', {'error': log}, room=request.sid)
       return
    
    chat_id = int(log)

    all_users = pm.db.query('''SELECT user_id
      FROM chat_participants WHERE chat_id=%s''', (chat_id,))
    
    if all_users:
       for user_data in all_users:
          user_id = str(user_data['user_id'])
          if user_id in connected_users:
             for sid in connected_users[user_id]:
                socket.emit('ws_del_message', {
                   'message_id': message_id,
                   'chat_id': chat_id
                }, room=sid)

    socket.emit('ws_del_log', {
      'success': True,
      'message_id': message_id,
    }, room=request.sid)        

  except Exception as e:
    print(f'Error WebSockets : del_message ({e})')
    emit('ws_error', {'type': 'Server Error'}, room=request.sid)
    return      

if __name__ == '__main__':
    socket.run(app, debug=False, port=3333)