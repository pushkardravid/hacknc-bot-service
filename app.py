from flask import Flask, request
import requests
import json
import os
import pymongo
import re
from pymongo import MongoClient
import random

app = Flask(__name__)
cluster = MongoClient("mongodb+srv://User1:User1@cluster1-ltlxk.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["Database1"]
posts = db.posts

location_utterences = ['Can you share your location?', 'Please share your location!', 'Where are you located?']
height_utterences = ['How tall are you in inches? (1 feet is 12 inches)', 'What is your height? (in inches)']
weight_utterences = ['How much do you weigh (in pounds) ?', 'May I have your weight please (in pounds)?']

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
        print(request)
        height = 72
        weight = 189
        zipCode = 27606
        coverage = 1000000
        duration = 10
        data = request.get_json()
        print(data)
        sender_id = data['entry'][0]['messaging'][0]['sender']['id']

        message = None
        if "message" in data['entry'][0]['messaging'][0]:
        	message = data['entry'][0]['messaging'][0]['message']
        payload = None
        if "postback" in data['entry'][0]['messaging'][0] and "payload" in data['entry'][0]['messaging'][0]['postback']:
        	payload = data['entry'][0]['messaging'][0]['postback']['payload']
        #print(message)
        #print("payload = " + str(payload))
        # check if attachment is there
        if message is not None and 'attachments' in message:
            attachments = message['attachments'][0]
            if attachments['type'] == 'image':
                img_url = attachments['payload']['url']
                kairos_response = get_image_attr(img_url)
                if kairos_response is None:
                	send_response(sender_id, 'Can you try one more time?')
                	am_i_a_joke(sender_id)
                	return 'failure'
                data = {'age': kairos_response['age'], 'gender': getGender(kairos_response['gender'])}
                replaceInDB(data, sender_id)
                responseMessage = askForRemaining(data)
                send_response(sender_id, responseMessage)
                #premium = getQuote(kairos_response['age'], getGender(kairos_response['gender']), height, weight, zipCode, coverage, duration)
                ##print(kairos_response)
                #print(premium)
                #send_response(sender_id, 'Your ' + str(kairos_response['age']) + ' years old')
                #You'll be paying a premium of _ dollars per month for the next _ years against a coverage of _ dollars
                #send_response(sender_id, 'You\'ll be paying a premium of $' + str(premium) + ' per month for the next ' + str(duration) + ' years against a coverage of $' + str(coverage))
            elif attachments['type'] == 'location':
                latitude, longitude = attachments['payload']['coordinates']['lat'], attachments['payload']['coordinates']['long']
                zip_code = get_zip(latitude, longitude)
                updateToDB({"zipCode": zip_code}, sender_id)
                newData = getFromDB(sender_id)
                responseMessage = askForRemaining(newData)
                if (responseMessage != None):
                    send_response(sender_id, responseMessage)
                else:
                    premium = getPremium(newData)
                    send_response(sender_id, 'You\'ll be paying a premium of $' + str(premium) + ' per month for the next ' + str(duration) + ' years against a coverage of $' + str(coverage))
                    get_typing_dots(sender_id)
                    send_response(sender_id, 'Hold on, I have something more for you!')
                    get_typing_dots(sender_id)
                    generate_plan_buttons(sender_id)
        elif isButton(payload):
        	print(payload)
        	myDuration = getButton(payload)
        	data = getFromDB(sender_id)
        	highestPrority = getHighestPriorityRemaining(data)
        	if duration is not None and highestPrority is None:
        		premium = getPremium(data, myDuration)
        		send_response(sender_id, 'You\'ll be paying a premium of $' + str(premium) + ' per month for the next ' + str(myDuration) + ' years against a coverage of $' + str(coverage))
        	else:
        		responseMessage = askForRemaining(data)
        		send_response(sender_id, responseMessage)
        else:
            data = getFromDB(sender_id)
            highestPref = getHighestPriorityRemaining(data)
            applicable = True
            if (highestPref != None):
                if (highestPref == "IMAGE" or highestPref == "LOCATION"):
                    applicable = False
                else:
                    num = getNum(message['text'])
                    if (num != None):
                        if (highestPref == "HEIGHT"):
                            key = "height"
                        else:
                            key = "weight"
                        updateToDB({key: num}, sender_id)
                        newData = getFromDB(sender_id)
                        responseMessage = askForRemaining(newData)
                        if (responseMessage != None):
                            send_response(sender_id, responseMessage)
                        else:
                            premium = getPremium(newData)
                            send_response(sender_id, 'You\'ll be paying a premium of $' + str(premium) + ' per month for the next ' + str(duration) + ' years against a coverage of $' + str(coverage))
                            get_typing_dots(sender_id)
                            send_response(sender_id, 'Hold on, I have something more for you!')
                            get_typing_dots(sender_id)
                            generate_plan_buttons(sender_id)
                    else:
                        applicable = False
                if (applicable == False):
                    send_response(sender_id, get_response(message['text']))
            else:
                send_response(sender_id, get_response(message['text']))
        return 'success'
    except Exception as e:
        print('fail bc')
        print(e)
        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
        send_response(sender_id, 'Sorry, I couldn\'t get you. Could you please rephrase')
        return 'failure'


@app.route('/dummy/', methods=['POST'])
def dummy_call():
    image_url = 'https://scontent.xx.fbcdn.net/v/t1.15752-9/72404461_2374600332609020_2060756206615527424_n.jpg?_nc_cat=110&_nc_oc=AQlyM1OIamsAE7YTjBT7ruSL9ZWLsohLfuUVIfy3sFPUOHnbW2HSXGQEX-Nxci9RFDv6CUxGBG_rGgXUkh3wy-G0&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.xx&oh=c09ee506ab3804996bf8e320701697e7&oe=5E63E6A7'
    get_image_attr(image_url)
    return 'success'

def getGender(gender):
    if (gender['type'] == 'M'):
        return "Male"
    else:
        return "Female"


def get_image_attr(image_url):
    url = 'https://api.kairos.com/detect'
    data = {"image": "%s" % image_url, "selector": "ROLL"}
    headers = {'Content-Type': 'application/json', 'app_id': '9d749141', 'app_key': '5c6e1d1671afb0845147870ac7ce3446'}
    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()
    if 'Errors' in resp_json.keys():
    	return None
    images = resp_json['images'][0]
    faces = images['faces'][0]
    attributes = faces['attributes']
    return attributes


def send_response(sender_id, message_text):
	get_typing_dots(sender_id)
	url = "https://graph.facebook.com/v4.0/me/messages"
	params = {'access_token': 'EAAIMDU43nkMBAMsTVVOJwAJYmje3ycxvyTFRENPoRs8ZB2Q2ji15RwY5MMuGBbWWywyVNrJQR2E29YEVcpa41dBvouHe23MS4nanceH2UZBsiJZBO8hDoEq2VFFryqweHD8RuOgO65v3JfS7Ial56cKPZC1IG0Iymafid9eTqgZDZD'}
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


#def getQuote():
def getQuote(age, gender, height, weight, zipCode, coverage, duration):
    feet = height / 12
    inches = height % 12
    typeValue = "term" + str(duration)
    params = {"valid":"true","id":0,"name":"assessment_new","funeral":{"amount":20000},"debt":{"amount":0},"collegeExpenses":{"numberOfChildren":1,"collegeType":"COLLEGE4PUBLIC","amount":0},"income":{"annually":"true","amount":"","wagePerHour":"","hoursPerWeek":"","years":duration},"asset":{"savings":"","payout":""},"insured":{"age":age,"gender":gender,"zip":zipCode,"weight":weight,"feet":feet,"inches":inches,"tobacco":"never"},"coverage":{"type":typeValue,"amount":coverage},"isTermProduct":"true","isPermanentProduct":"false"}
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

def getFromDB(sender_id):
    return posts.find_one(sender_id)

def updateToDB(data, sender_id):
    only_id = {
        '_id': sender_id
    }
    result = posts.update_one(only_id, {"$set": data}, upsert=True)

def replaceInDB(data, sender_id):
    only_id = {
        '_id': sender_id
    }
    result = posts.replace_one(only_id, data, upsert=True)

def getHighestPriorityRemaining(data):
    if (data == None or ("age" not in data) or ("gender" not in data)):
        return "IMAGE"
    if ("zipCode" not in data):
        return "LOCATION"
    if ("height" not in data):
        return "HEIGHT"
    if ("weight" not in data):
        return "WEIGHT"
    return None

def askForRemaining(data):
    remaining = getHighestPriorityRemaining(data)
    if (remaining == "IMAGE"):
        return "Selfie bhej"
    if (remaining == "LOCATION"):
        return location_utterences[random.randint(0,2)]
    if (remaining == "HEIGHT"):
        return height_utterences[random.randint(0,1)]
    if (remaining == "WEIGHT"):
        return weight_utterences[0]
    return None

def getPremium(data, duration = None):
    coverage = 1111111
    if duration is None:
        duration = 10
    return getQuote(data['age'], data['gender'], data['height'], data['weight'], data['zipCode'], coverage, duration)

def getNum(string):
    match = re.search(r'\d+', string)
    if (match != None):
        return int(match.group())

def generate_plan_buttons(sender_id):
	url = "https://graph.facebook.com/v4.0/me/messages"

	querystring = {"access_token":"EAAIMDU43nkMBAMsTVVOJwAJYmje3ycxvyTFRENPoRs8ZB2Q2ji15RwY5MMuGBbWWywyVNrJQR2E29YEVcpa41dBvouHe23MS4nanceH2UZBsiJZBO8hDoEq2VFFryqweHD8RuOgO65v3JfS7Ial56cKPZC1IG0Iymafid9eTqgZDZD"}

	payload = "{\n  \"recipient\":{\n    \"id\":\"%s\"\n  },\n  \"message\":{\n    \"attachment\":{\n      \"type\":\"template\",\n      \"payload\":{\n        \"template_type\":\"button\",\n        \"text\":\"Please choose one of the following options\",\n        \"buttons\":[\n          {\n  \"type\": \"postback\",\n  \"title\": \"10 Year Term Plan\",\n  \"payload\": \"button-10\"\n},{\n  \"type\": \"postback\",\n  \"title\": \"20 Year Term Plan\",\n  \"payload\": \"button-20\"\n},{\n  \"type\": \"postback\",\n  \"title\": \"30 Year Term Plan\",\n  \"payload\": \"button-30\"\n}\n        ]\n      }\n    }\n  }\n}" % sender_id
	headers = {
	    'Content-Type': "application/json",
	    'User-Agent': "PostmanRuntime/7.17.1",
	    'Accept': "*/*",
	    'Cache-Control': "no-cache",
	    'Postman-Token': "b58e3a22-1724-4235-84ea-9dd0cf0f4571,8f69cec1-85af-4230-9968-3bc9f23693d3",
	    'Host': "graph.facebook.com",
	    'Accept-Encoding': "gzip, deflate",
	    'Content-Length': "545",
	    'Connection': "keep-alive",
	    'cache-control': "no-cache"
	    }

	response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
	return 'success'

def get_typing_dots(sender_id):
	url = "https://graph.facebook.com/v2.6/me/messages"

	querystring = {"access_token":"EAAIMDU43nkMBAMsTVVOJwAJYmje3ycxvyTFRENPoRs8ZB2Q2ji15RwY5MMuGBbWWywyVNrJQR2E29YEVcpa41dBvouHe23MS4nanceH2UZBsiJZBO8hDoEq2VFFryqweHD8RuOgO65v3JfS7Ial56cKPZC1IG0Iymafid9eTqgZDZD"}

	payload = "{\n  \"recipient\":{\n    \"id\":\"%s\"\n  },\n  \"sender_action\":\"typing_on\"\n}" % sender_id
	headers = {
	    'Content-Type': "application/json",
	    'Accept': "*/*",
	    'Cache-Control': "no-cache",
	    'Host': "graph.facebook.com",
	    'Accept-Encoding': "gzip, deflate",
	    'Content-Length': "82",
	    'Connection': "keep-alive",
	    'cache-control': "no-cache"
	    }

	response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

	print(response.text)

def am_i_a_joke(sender_id):
	url = "https://graph.facebook.com/v2.6/me/messages"
	querystring = {"access_token":"EAAIMDU43nkMBAMsTVVOJwAJYmje3ycxvyTFRENPoRs8ZB2Q2ji15RwY5MMuGBbWWywyVNrJQR2E29YEVcpa41dBvouHe23MS4nanceH2UZBsiJZBO8hDoEq2VFFryqweHD8RuOgO65v3JfS7Ial56cKPZC1IG0Iymafid9eTqgZDZD"}
	payload = "{\n  \"recipient\":{\n    \"id\":\"%s\"\n  },\n  \"message\":{\n    \"attachment\": {\n      \"type\": \"template\",\n      \"payload\": {\n         \"template_type\": \"media\",\n         \"elements\": [\n            {\n               \"media_type\": \"image\",\n               \"url\": \"https://www.facebook.com/100745301348385/photos/p.100897881333127/100897881333127/?type=3&theater\"\n            }\n         ]\n      }\n    }    \n  }\n}" % sender_id
	headers = {'Content-Type': "application/json",'User-Agent': "PostmanRuntime/7.17.1",'Accept': "*/*",'Cache-Control': "no-cache",'Postman-Token': "20da8710-9a1a-4a95-96bc-638a4704f43e,0e568397-73db-464e-999d-f007997037bb",'Host': "graph.facebook.com",'Accept-Encoding': "gzip, deflate",'Content-Length': "410",'Connection': "keep-alive",'cache-control': "no-cache"}
	response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

def getButton(string):
    if (string == "button-10"):
        return 10
    if (string == "button-20"):
        return 20
    if (string == "button-30"):
        return 30
    return None

def isButton(string):
	if string is None:
		return False
	button = getButton(string)
	if button is None:
		return False
	else:
		return True

if __name__ == '__main__':
    app.run(debug=True)
