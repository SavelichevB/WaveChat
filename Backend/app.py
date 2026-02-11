from flask import Flask, request, jsonify
from config import GetData

app = Flask(__name__)
config_file = GetData()

@app.route('/api/', methods=['GET'])
def GetMess():
 data = config_file.GetMessage()
 return jsonify({'Info': data}), 200  

if __name__ == '__main__':
  app.run(debug=True, port=7777)