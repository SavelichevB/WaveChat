from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from models.auth import Auth

#Create app:
app = Flask(__name__)

#JWT Config:
app.config['JWT_SECRET_KEY'] = 'TestToken'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=30)
jwt = JWTManager(app)

#Objects:
auth = Auth()

#Endpoints: 
@app.route('/', methods=['GET'])
def Home():
 return jsonify({
   'service': 'WaveChat API',
   'status': 'online',
   'version': '1.0.0.0'
 }), 200  

@app.route('/auth/reg', methods=['POST'])
def registr_users():
  try:
    client_username = request.json.get('username')
    client_password = request.json.get('password')
    if not client_username or not client_password: return jsonify({'Info': 'Username or password not found'}), 500
    #Request to auth.py (SOON)
    data_reg, log = auth.Registation(client_username, client_password)
    if not data_reg: return jsonify({'Info': 'Username or Password incorrect for the registation', 'Log': log}), 400
    access_token = create_access_token(identity=str(log))
    if not access_token: return jsonify({'Info': 'Error app for regisration'}), 400
    return jsonify({
      'Success': True,
      'Token': access_token
      }), 200
    
  except Exception as e:
    print(e)
    return jsonify({
      'Info': 'Error app for regisration'
    }), 500

if __name__ == '__main__':
  app.run(debug=True, port=3333)