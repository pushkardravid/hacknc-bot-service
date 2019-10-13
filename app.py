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
	try:
	    data = request.get_json()
	    print(data)
	    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
	    message = data['entry'][0]['messaging'][0]['message']
	    # check if attachment is there
	    if 'attachments' in message:
	        attachments = message['attachments'][0]
	        if attachments['type'] == 'image':
	            img_url = attachments['payload']['url']
	            kairos_response = get_image_attr(img_url)
	            print(kairos_response)
	            send_response(sender_id, 'Your ' + str(kairos_response['age']) + ' years old')
	        elif attachments['type'] == 'location':
	        	latitude, longitude = attachments['payload']['coordinates']['lat'], attachments['payload']['coordinates']['long']
	        	zip_code = get_zip(latitude, longitude)
	        	send_response(sender_id, str(zip_code))
	    else:
	    	send_response(sender_id, get_response(data['entry'][0]['messaging'][0]['message']['text']))
	    return 'success'
	except Exception as e:
		print('fail bc')
		print(e)
		sender_id = data['entry'][0]['messaging'][0]['sender']['id']
		send_response(sender_id, 'sorry, mai chutiya hu')
		return 'failure'


@app.route('/dummy/', methods=['POST'])
def dummy_call():
    image_url = 'https://scontent.xx.fbcdn.net/v/t1.15752-9/72404461_2374600332609020_2060756206615527424_n.jpg?_nc_cat=110&_nc_oc=AQlyM1OIamsAE7YTjBT7ruSL9ZWLsohLfuUVIfy3sFPUOHnbW2HSXGQEX-Nxci9RFDv6CUxGBG_rGgXUkh3wy-G0&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.xx&oh=c09ee506ab3804996bf8e320701697e7&oe=5E63E6A7'
    get_image_attr(image_url)
    return 'success'


def get_image_attr(image_url):
    url = 'https://api.kairos.com/detect'
    data = {"image": "%s" % image_url, "selector": "ROLL"}
    headers = {'Content-Type': 'application/json', 'app_id': '9d749141', 'app_key': '5c6e1d1671afb0845147870ac7ce3446'}
    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()
    images = resp_json['images'][0]
    faces = images['faces'][0]
    attributes = faces['attributes']
    return attributes


def send_response(sender_id, message_text):
    url = "https://graph.facebook.com/v4.0/me/messages"
    params = {
        'access_token': 'EAAIMDU43nkMBAMUZA5SHjZCB4N01MlfkLyuKpSY3me0PZAAZCW8R7vO3g3ZCYlklMaomZBoVYZAnAqm5Vwa6BV3dZCWyu4MZAnaPpgxGv5C2ILiBMebku3Pio1bWN65Ndry0CvAvgeeVyQa2k9dh3HntZCiffungeR2XlDmW75ZAZCQlIQZDZD'}
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
    t = response['result']['fulfillment']['speech']
    print(t)
    return t


#def getQuote(age, gender, height, weight, zipCode, coverage, duration):
def getQuote():
    params = {"valid":"true","id":0,"name":"assessment_new","funeral":{"amount":20000},"debt":{"amount":0},"collegeExpenses":{"numberOfChildren":1,"collegeType":"COLLEGE4PUBLIC","amount":0},"income":{"annually":"true","amount":"","wagePerHour":"","hoursPerWeek":"","years":10},"asset":{"savings":"","payout":""},"insured":{"age":23,"gender":"Male","zip":"12345","weight":189,"feet":6,"inches":1,"tobacco":"never"},"coverage":{"type":"term10","amount":1111111},"isTermProduct":"true","isPermanentProduct":"false"}
    coverageNeeds = {"coverageNeeds": json.dumps(params)}
    headers = {
                "Accept": "application/json",
                "Connection": "keep-alive",
                "CustomHeader": "LifeCalculator",
                "Host": "www.principalcom",
                "Referer": "https://www.principal.com/individuals/life-insurance-calculator/",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
            }
    response = requests.get(
            'https://www.principal.com/ind/api/marketing/life-insurance-calculator/coverage-options', 
            params=coverageNeeds,
            headers=headers
    )
    jsonResponse = response.json()
    duration = 20
    if (duration == 10):
        return str(jsonResponse['tenYrCoveragePremium'])
    elif (duration == 20):
        return str(jsonResponse['twentyYrCoveragePremium'])
    else:
        return str(jsonResponse['thirtyYrCoveragePremium'])

def get_zip(latitude, longitude):
	url = "https://maps.googleapis.com/maps/api/geocode/json"
	querystring = {"latlng":str(latitude) + "," + str(longitude),"key":"AIzaSyA-QIPlustS1vfaRGoxyVAK9R20JU2v20U"}
	headers = {'Accept': "*/*", 'Cache-Control': "no-cache", 'Host': "maps.googleapis.com", 'Accept-Encoding': "gzip, deflate", 'Connection': "keep-alive", 'cache-control': "no-cache"}
	response = requests.request("GET", url, headers=headers, params=querystring)
	address_tuples = json.loads(response.text)['results'][0]['address_components']
	zip_code = [i['long_name'] for i in address_tuples if i['types'][0] == 'postal_code'][0]
	return zip_code

if __name__ == '__main__':
    app.run(debug=True)
