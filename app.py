from slackclient import SlackClient
import json

with open('key.json') as json_data:
    d = json.load(json_data)
    print(d['token'])

print("start")