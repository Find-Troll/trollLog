import requests
from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, RIOT_API_KEY
import time
import pymysql
import json

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, 
                       password=MYSQL_PASSWORD, db='find_troll', charset='utf8')
curs = conn.cursor()
insertSql = "REPLACE INTO `trollMatch` (gameId,matches,timelines) VALUES (%s, %s, %s) "

RECENTMATCHCNT = 20
SEASON = 13
QUEUE = 420
initURL = 'https://kr.api.riotgames.com'

accountId = '1rsGJq_S2kSTQ-I3myielZCe1aW-avXTlQ_2-hC1v5WF-7d9bC2-6tLo'
while(True):
    res = requests.get(initURL + '/lol/match/v4/matchlists/by-account/{0}?queue={1}&season={2}&api_key={3}'.format(
        accountId,QUEUE,SEASON,RIOT_API_KEY
    ))
    if res.status_code == 200 : break
    time.sleep(2)
matchlists = res.json()

for row in matchlists['matches'][:RECENTMATCHCNT]:
    gameId = row['gameId']
    while(True):
        res = requests.get(initURL + '/lol/match/v4/matches/{0}?api_key={1}'.format(gameId,RIOT_API_KEY))
        if res.status_code == 200 : break
        time.sleep(2)
    matches = res.json()
    while(True):
        res = requests.get(initURL + '/lol/match/v4/timelines/by-match/{0}?api_key={1}'.format(gameId,RIOT_API_KEY))
        if res.status_code == 200 : break
        time.sleep(2)
    timelines = res.json()
    curs.execute(insertSql,(gameId,json.dumps(matches),json.dumps(timelines)))
    conn.commit()
    print("insert !")