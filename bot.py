import requests
import re
import time
import json
import datetime


cf_url = 'https://codeforces.com/api/contest.list?gym=false'
webhook_url = ''
webhook_txt = 'webhook.txt' # contents must be secret. gitignore it.
headers = {
    'Content-type': 'application/json',
}
timezone = 9 # Korean Standard Timezone
save_txt = 'savedlist.txt'


def initialize():
    global webhook_url
    with open(webhook_txt, 'r') as f:
        webhook_url = f.readline()

def getJson():
    req = requests.get(cf_url)
    return req.json()

def getIdlist():
    info = getJson()
    if info['status'] == 'OK':
        return [x['id'] for x in info['result']]
    else:
        return []

def recentIdlist():
    req = requests.get('https://codeforces.com/contests')
    html = req.text
    html = html.split('<div class="datatable"')[1]
    # print(html)
    return [int(x) for x in re.findall(r'data-contestId="(\d*)"', html)]

def loadIdlist():
    with open(save_txt, 'r') as f:
        return list(map(int, f.readline().split(',')))

def contestInfo(id_):
    info = getJson()
    for x in info['result']:
        if x['id'] == id_:
            return x

def formatMessage(contests):
    return '*{name}* {date} | {HH}:{MM}'.format(
        name=contest['name'],
        date=datetime.datetime.utcfromtimestamp(int(contest['startTimeSeconds']) + 9*3600),
        HH='%02d' % (int(contest['durationSeconds'])//3600),
        MM='%02d' % ((int(contest['durationSeconds'])%3600)//60)
    )

def sendMessage(message):
    data = '{"text":"' + message + '"}'
    resp = requests.post(webhook_url, headers=headers, data=data.encode('utf-8'))

def saveIdlist(idlist):
    with open(save_txt, 'w') as f:
        f.write(','.join([str(x) for x in idlist]))


if __name__ == '__main__':
    initialize()
    while True:
        updated = False
        print('Checking...', end=' ')
        new_idlist = getIdlist()
        old_idlist = loadIdlist()
        for x in new_idlist:
            if x not in old_idlist:
                updated = True
                contest = contestInfo(x)
                message = formatMessage(contest)
                sendMessage(message)
                print(message)

        if updated:
            saveIdlist(new_idlist)
        else:
            print('Up-to-date. %d' % (time.time()))
        time.sleep(10)
