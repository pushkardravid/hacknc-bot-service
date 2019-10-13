from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
def handle_verification():
    if (request.args.get('hub.verify_token', '') == 'verification_token_for_facebook_chatbot'):
        print("Verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong token")
        return "Error, wrong validation token"


@app.route('/', methods=['POST'])
def handle_message():
    data = request.get_json()
    print(data)

    message = data['entry'][0]['messaging'][0]['message']
    # check if attachment is there
    if message.has_key('attachments'):
        attachments = message['attachments'][0]
        if attachments['type'] == 'images':
            img_url = attachments['payload']
            get_image_attr(img_url)

    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
    print data['entry'][0]['messaging'][0]['message']['text']
    # get_response(data['entry'][0]['messaging'][0]['message']['text'])
    send_response(sender_id, get_response(data['entry'][0]['messaging'][0]['message']['text']))
    return 'success'


@app.route('/dummy/', methods=['POST'])
def dummy_call():
    image_url = 'https://scontent.xx.fbcdn.net/v/t1.15752-9/72404461_2374600332609020_2060756206615527424_n.jpg?_nc_cat=110&_nc_oc=AQlyM1OIamsAE7YTjBT7ruSL9ZWLsohLfuUVIfy3sFPUOHnbW2HSXGQEX-Nxci9RFDv6CUxGBG_rGgXUkh3wy-G0&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.xx&oh=c09ee506ab3804996bf8e320701697e7&oe=5E63E6A7'
    get_image_attr(image_url)
    return 'success'


def get_image_attr(image_url):
    url = 'https://api.kairos.com/detect'
    data = {"image": "%s" % image_url, "selector": "ROLL"}
    headers = {'Content-Type': 'application/json', 'app_id': os.environ['app_id'], 'app_key': os.environ['app_key']}
    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()
    images = resp_json['images'][0]
    faces = images['faces'][0]
    attributes = faces['attributes']
    return attributes


def send_response(sender_id, message_text):
    url = "https://graph.facebook.com/v4.0/me/messages"
    params = {
        'access_token': 'EAAIMDU43nkMBAExoHtqBMPv4Oo43PreEZAoKZC5dz4efq3S595VNDgfjhbhp5TGLhkm0mbS6rBHdeabUysA0bkkhP3gYvhsqU8mdZCupWUSq8bkZA1xvD35dhToUTQcOlK0MV5doxNhg6oqDKEZBhiSMBS4Ikw26NgPDaVnOAZCAZDZD'}
    headers = {'Content-Type': 'application/json'}
    data = {'recipient': {'id': sender_id}, 'message': {'text': message_text}}
    response = requests.post(url, params=params, headers=headers, json=data)
    return response


@app.route('/test', methods=['POST'])
def get_response(msg):
    url = "https://api.dialogflow.com/v1/query"
    querystring = {"v": "20150910"}
    payload = {
        "contexts": [
            "shop"
        ],
        "lang": "en",
        "query": msg,
        "sessionId": "12345"
    }
    headers = {
        'Authorization': "Bearer 1fe26cdd1cec4d86a8ae4aba8a5364aa",
        'Content-Type': "application/json",
        'User-Agent': "PostmanRuntime/7.17.1",
        'Accept': "/",
        'Cache-Control': "no-cache",
        'Postman-Token': "3bac8bbc-3124-4ae1-b92b-0199b063cf51,0a869ef2-d273-4a2e-9b6b-a58058c6cdaa",
        'Host': "api.dialogflow.com",
        'Accept-Encoding': "gzip, deflate",
        'Content-Length': "112",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers, params=querystring).json()
    t = response['result']['fulfilment']['speech']
    print(t)
    return t


if __name__ == '__main__':
    app.run(debug=True)
