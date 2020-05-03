import requests
from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, RIOT_API_KEY
import time
import pandas as pd
import pymysql
import json

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, 
                       password=MYSQL_PASSWORD, db='find_troll', charset='utf8')

curs = conn.cursor()
sql = "REPLACE INTO `user` (accountId,summoner,league) VALUES (%s, %s, %s)"

initURL = 'https://kr.api.riotgames.com'

def foo(page):
    res = requests.get(initURL+'/lol/league/v4/entries/RANKED_SOLO_5x5/IRON/IV?&page={0}&api_key={1}'.format(page,RIOT_API_KEY))
    while res.status_code != 200 :
        time.sleep(5)
        res = requests.get(initURL+'/lol/league/v4/entries/RANKED_SOLO_5x5/IRON/IV?&page={0}&api_key={1}'.format(page,RIOT_API_KEY))

    if len(res.json()) == 0 : return False

    for leagueJson in res.json():
        summonerRes = requests.get(initURL+'/lol/summoner/v4/summoners/{0}?api_key={1}'.format(leagueJson['summonerId'],RIOT_API_KEY))
        while summonerRes.status_code != 200 :
            time.sleep(5)
            summonerRes = requests.get(initURL+'/lol/summoner/v4/summoners/{0}?api_key={1}'.format(leagueJson['summonerId'],RIOT_API_KEY))

        summonerJson = summonerRes.json()

        if 'accountId' in summonerJson: 
            curs.execute(sql,(summonerJson['accountId'],json.dumps(summonerJson),json.dumps(leagueJson)))
            conn.commit()
    return True

page = 1
while(True): 
    if foo(page)==False : break
    page+=1