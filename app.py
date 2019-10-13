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
    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
    print data['entry'][0]['messaging'][0]['message']['text']
    # get_response(data['entry'][0]['messaging'][0]['message']['text'])
    send_response(sender_id, get_response(data['entry'][0]['messaging'][0]['message']['text']))
    return 'success'


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
