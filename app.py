# app.py

from flask import Flask
from flask import request
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid

app = Flask(__name__)
app.config.from_object('config') # config.py

dynamodb = boto3.resource('dynamodb', 
                          region_name='us-east-1',
                          aws_access_key_id=app.config['DYNAMO_KEY'],
		                      aws_secret_access_key=app.config['DYNAMO_SECRET'])

table = dynamodb.Table('generic-crud-items')

@app.route('/')
def hello_world():
  return '<h1>Yeah, that is Zappa! Zappa! Zap! Zap!</h1>'

@app.route('/items', methods=['GET'])
def get_items():
  return table.scan()

@app.route('/items', methods=['POST'])
def add_item():
  json = request.get_json()
  name = json['name']
  item_id = str(uuid.uuid1())
  return table.put_item(Item={ 'id': item_id, 'name': name })

@app.route('/items/<item_id>', methods=['GET'])
def get_item(item_id):
  return table.get_item(Key={ 'id': item_id })

@app.route('/items/<item_id>', methods=['PUT'])
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
def delete_item(item_id):
  return table.delete_item(Key={ 'id': item_id })

if __name__ == '__main__':
  app.run()
