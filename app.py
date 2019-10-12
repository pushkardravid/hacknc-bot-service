from flask import Flask, request
import requests
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def handle_verification():
    
    if (request.args.get('hub.verify_token', '') == os.environ['VERIFY_TOKEN']):
        print("Verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong token")
        return "Error, wrong validation token"

@app.route('/', methods=['POST'])
def handle_message():
	data = request.get_json()
	print(data)
	sender_id = data['entry'][0]['messaging'][0]['sender']['id']
	send_response(sender_id, 'thnx bro')
	return 'success'

def send_response(sender_id, message_text):
	url = "https://graph.facebook.com/v4.0/me/messages"
	params = {'access_token': os.environ['PAGE_ACCESS_TOKEN']}
	headers = {'Content-Type': 'application/json'}
	data = { 'recipient': {'id': sender_id}, 'message': {'text': message_text}}
	response = requests.post(url, params=params, headers=headers,json=data)
	return response

if __name__ == '__main__':
    app.run(debug=True)