from flask import Flask, request
import requests
import os
import json

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

	#add code for image attachments
	message = data['entry'][0]['messaging'][0]['message']
	#check if attachment is there
	if message.has_key('attachments'):
		attachments = message['attachments'][0]
		if attachments['type'] == 'images':
			img_url = attachments['payload']
			get_image_attr(img_url)

	sender_id = data['entry'][0]['messaging'][0]['sender']['id']
	send_response(sender_id, 'thnx bro')
	return 'success'

@app.route('/dummy/', methods=['POST'])
def dummy_call():
	image_url = 'https://scontent.xx.fbcdn.net/v/t1.15752-9/72404461_2374600332609020_2060756206615527424_n.jpg?_nc_cat=110&_nc_oc=AQlyM1OIamsAE7YTjBT7ruSL9ZWLsohLfuUVIfy3sFPUOHnbW2HSXGQEX-Nxci9RFDv6CUxGBG_rGgXUkh3wy-G0&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.xx&oh=c09ee506ab3804996bf8e320701697e7&oe=5E63E6A7'
	get_image_attr(image_url)
	return 'success'

def send_response(sender_id, message_text):
	url = "https://graph.facebook.com/v4.0/me/messages"
	params = {'access_token': os.environ['PAGE_ACCESS_TOKEN']}
	headers = {'Content-Type': 'application/json'}
	data = { 'recipient': {'id': sender_id}, 'message': {'text': message_text}}
	response = requests.post(url, params=params, headers=headers,json=data)
	return response

def get_image_attr(image_url):
	url = 'https://api.kairos.com/detect'
	data = { "image": "%s" % image_url, "selector": "ROLL"}
	headers = {'Content-Type': 'application/json', 'app_id': os.environ['app_id'], 'app_key': os.environ['app_key']}
	response = requests.post(url, headers=headers, json=data)
	resp_json = response.json()
	images = resp_json['images'][0]
	faces = images['faces'][0]
	attributes = faces['attributes']
	return attributes

if __name__ == '__main__':
    app.run(debug=True, port=80, host="0.0.0.0")
