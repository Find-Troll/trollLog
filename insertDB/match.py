import requests
from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, RIOT_API_KEY
import time
import pandas as pd
import pymysql
import json

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, 
                       password=MYSQL_PASSWORD, db='find_troll', charset='utf8')
curs = conn.cursor()
selectSql = "SELECT  accountId FROM user WHERE JSON_EXTRACT(league,'$.rank') = 'IV'"
checkSql = "SELECT gameId from `match` WHERE gameId = (%s)"
insertSql = "INSERT INTO `match` (gameId,matches,timelines) VALUES (%s, %s, %s) "

RECENTMATCHCNT = 10
SEASON = 13
QUEUE = 420
initURL = 'https://kr.api.riotgames.com'

curs.execute(selectSql)
selectRes = json.dumps(curs.fetchall())[1:-1].split(", ")

for row in selectRes: 
    accountId = row[2:-2]
    while(True):
        res = requests.get(initURL + '/lol/match/v4/matchlists/by-account/{0}?queue={1}&season={2}&api_key={3}'.format(
            accountId,QUEUE,SEASON,RIOT_API_KEY
        ))
        if res.status_code == 200 : break
        time.sleep(1)
    matchlists = res.json()

    for row in matchlists['matches'][:RECENTMATCHCNT]:
        gameId = row['gameId']
        curs.execute(checkSql,(gameId))
        if len(curs.fetchall()) != 0 : continue

        while(True):
            res = requests.get(initURL + '/lol/match/v4/matches/{0}?api_key={1}'.format(gameId,RIOT_API_KEY))
            if res.status_code == 200 : break
            time.sleep(1)
        matches = res.json()

        while(True):
            res = requests.get(initURL + '/lol/match/v4/timelines/by-match/{0}?api_key={1}'.format(gameId,RIOT_API_KEY))
            if res.status_code == 200 : break
            time.sleep(1)
        timelines = res.json()

        curs.execute(insertSql,(gameId,json.dumps(matches),json.dumps(timelines)))
        conn.commit()

