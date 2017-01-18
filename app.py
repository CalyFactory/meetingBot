from slackclient import SlackClient
import json
import requests
import time
from datetime import datetime, timedelta
from datetime import date
import re

with open('key.json') as json_data:
    d = json.load(json_data)
    bot_token = d['bot_token']
    ai_token = d['ai_token']

print("start")

    
def getdate(dateString):
    dateObject = datetime.strptime(dateString, "Date(%Y,%m,%d,%H,%M,%S)")
    return dateObject.strftime("%H:%M")

def requestNlp(query):
    result = requests.get(
        "https://api.api.ai/v1/query",
        params = {
            'v' : '20150910',
            'query' : query,
            'lang' : 'kr',
            'sessionId' : '1'
        },
        headers = {
            'Authorization' : ai_token,
            'COntent-Type' : 'application/json; charset=utf-8'
        }
    )
    print(result.text)
    return result.json()

def loadRoom(date):

    nine_hours_from_now = datetime.now() + timedelta(hours=9)
    todayString = nine_hours_from_now.strftime("%Y-%m-%d")

    url = "http://115.68.116.16/swmaestro/admin/getData1.php?dt="+date
    r = requests.get(url).json()

    roomData = {}
    for row in r['rows']:
        if bool(re.match("\d회의실",row['c'][0]['v'])):
            if row['c'][1]['v'] != "": 
                stTime = getdate(row['c'][2]['v'])
                edTime = getdate(row['c'][3]['v'])
                roomNum = row['c'][0]['v'] 
                manName = row['c'][1]['v']

                schedule = [manName, stTime, edTime]

                if roomNum not in roomData:
                    roomData[roomNum] = []
                roomData[roomNum].append(schedule)

    result = "*<" + date + " 회의실 예약내역>*\n"
    for row in roomData:
        string = row + " : " 
        for row2 in roomData[row]:
            string = string + row2[1] + "~" + row2[2] + "(" + row2[0] + ") "
        result += string+"\n"
    return result 

slackClient = SlackClient(bot_token)
#curl 'https://api.api.ai/api/query?v=20150910&query=%EC%95%88%EB%85%95&lang=ko&sessionId=4147bc78-87f6-407d-84f5-ef63a0c4c596&timezone=2017-01-18T14:31:34+0900' -H 'Authorization:Bearer 78e4f20c78c240eca6527b6fe31cbbcf'

print("try connect")
if slackClient.rtm_connect():
    print("connected")

    while True:
        response = slackClient.rtm_read()
        if len(response) == 0:  
            continue

        for data in response:
            if data['type'] == "message" and 'subtype' not in data:
                if data['text'][0] == '/':
                    continue
                if "<@U3GUQSAR3>" in data['text']:
                    text = data['text']
                    text = text.replace("<@U3GUQSAR3>","").strip()

                    responseJson = requestNlp(text)

                    intentName = responseJson['result']['metadata']['intentName']
                    speech = responseJson['result']['fulfillment']['messages'][0]['speech']
                    parameters = responseJson['result']['parameters']
                    if intentName == "book":
                        bookDate = parameters['date']
                        if parameters['date-period'] == "":
                            bookStartTime = parameters['time-period']
                            bookEndTime = parameters['time-period']
                        else:
                            bookStartTime = parameters['date-period']
                            bookEndTime = parameters['date-period']
                        bookRoomNo = parameters['roomnum']
                        
                        speech = "예약" + bookDate + " " + bookStartTime + " " + bookEndTime + " " + bookRoomNo
                    elif intentName == "inquiry":
                        inquiryDate = parameters['date']
                        speech = loadRoom(inquiryDate)

                    slackClient.api_call(
                        "chat.postMessage",
                        channel=data['channel'],
                        text=speech
                    )
                    print(text)

