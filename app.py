# app.py

from flask import Flask
from flask import request, jsonify
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from functools import wraps

app = Flask(__name__)
app.config.from_object('config') # config.py
dynamodb = boto3.resource('dynamodb', 
                          region_name='us-east-1',
                          aws_access_key_id=app.config['DYNAMO_KEY'],
		                      aws_secret_access_key=app.config['DYNAMO_SECRET'])
table = dynamodb.Table('generic-crud-items')

# decorator for verifying token
def token_required(f): 
    @wraps(f) 
    def decorated(*args, **kwargs): 
        token = None
        if 'x-access-token' in request.headers: 
            token = request.headers['x-access-token'] 
        if not token: 
            return jsonify({'message' : 'Token is missing'}), 401
        try: 
            s = Serializer(app.config['TOKEN_SECRET'])
            _ = s.loads(token)
        except SignatureExpired:
            return jsonify({'message' : 'Token is expired'}), 401
        except: 
            return jsonify({'message' : 'Token is invalid'}), 401
        # this could return decoded info to the routes 
        return f(*args, **kwargs) 
    return decorated

@app.route('/')
def hello_world():
  return '<h1>Yeah, that is Zappa! Zappa! Zap! Zap!</h1>'

@app.route('/items', methods=['GET'])
@token_required
def get_items():
  return table.scan() # try global secondary indexes for optional query parameters

@app.route('/items', methods=['POST'])
@token_required
def add_item():
  json = request.get_json()
  name = json['name']
  item_id = str(uuid.uuid1())
  return table.put_item(Item={ 'id': item_id, 'name': name })

@app.route('/items/<item_id>', methods=['GET'])
@token_required
def get_item(item_id):
  return table.get_item(Key={ 'id': item_id })

@app.route('/items/<item_id>', methods=['PUT'])
@token_required
def update_item(item_id):
  json = request.get_json()
  name = json['name']
  response = table.update_item(
    Key={ 'id': item_id },
    UpdateExpression="SET #nm = :n",
    ExpressionAttributeValues={':n': name },
    ExpressionAttributeNames={ "#nm": "name" }, # name is a reserved keyword
    ReturnValues="UPDATED_NEW")
  return response

@app.route('/items/<item_id>', methods=['DELETE'])
@token_required
def delete_item(item_id):
  return table.delete_item(Key={ 'id': item_id })

if __name__ == '__main__':
  app.run()
