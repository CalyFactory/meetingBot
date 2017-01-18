from slackclient import SlackClient
import json
import requests
import time

with open('key.json') as json_data:
    d = json.load(json_data)
    bot_token = d['bot_token']
    ai_token = d['ai_token']

print("start")

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

slackClient = SlackClient(bot_token)


data = slackClient.api_call(
    "users.info",
    bot="hotsan"
)

print(data)
print("try connect")
if slackClient.rtm_connect():
    print("connected")

    slackClient.api_call(
        "chat.postMessage",
        channel="#testbed",
        text="Hello from Python! :tada:"
    )
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
                    slackClient.api_call(
                        "chat.postMessage",
                        channel=data['channel'],
                        text=responseJson['result']['fulfillment']['messages'][0]['speech']
                    )
                    print(text)

