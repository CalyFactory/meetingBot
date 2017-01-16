from slackclient import SlackClient
import json
import requests


with open('key.json') as json_data:
    d = json.load(json_data)
    bot_token = d['bot_token']
    ai_token = d['ai_token']

print("start")


result = requests.get(
    "https://api.api.ai/v1/query",
    params = {
        'v' : '20150910',
        'query' : '오늘 3회의실 3시부터 4시까지 예약해줘',
        'lang' : 'kr',
        'sessionId' : '1'
    },
    headers = {
        'Authorization' : ai_token,
        'COntent-Type' : 'application/json; charset=utf-8'
    }
)
print(result.text)