import pandas as pd
import json
import pickle
import numpy as np
import requests
import json
import os
import sys

from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD

API_HOST = 'http://52.78.119.98:4000'
TROLL_NAME = '행복한패배'

N = 10 #게임 갯수
M = 9 #feature 갯수

accountId = json.loads(requests.get(API_HOST + '/api/user/riotSummoner',params={'summonerName' : TROLL_NAME}).json())['accountId']
gameIndex = {'accountId' : accountId, 'queue' : '420', 'season' : '13', 'beginIndex' : '0', 'endIndex' : '10'}

matches = json.loads(requests.get(API_HOST+'/api/user/riotMatchlist',params=gameIndex).json())['matches']

ret = np.zeros(N*M).reshape(N,M)

i = 0
j = 0

for row in matches:
    j = 0
    match = json.loads(requests.get(API_HOST+'/api/match/riotMatches',params={'gameId' : row['gameId']}).json())

    ret[i][j] = match['gameDuration']
    j+=1

    # 몇 번째 인원인지
    idx = 0
    for p in match['participantIdentities']:
        if p['player']['accountId'] == accountId : break
        idx+=1
    
    stats = match['participants'][idx]['stats']
    
    ret[i][j] = int(stats['win'])
    j+=1

    ret[i][j] = int(match['teams'][int(idx>=5)]['firstBaron'])
    j+=1

    # goldEarned, championLevel, teamKillAssists
    start = 0 if idx < 5 else 5
    teamGold = teamLevel = teamKillAssists = 0
    for k in range(start,start+5):
        teamGold += int(match['participants'][k]['stats']['goldEarned'])
        teamLevel += int(match['participants'][k]['stats']['champLevel'])
        teamKillAssists += int(match['participants'][k]['stats']['kills'])

    ret[i][j] = int(stats['goldEarned']) - (teamGold/5.0)
    j+=1

    ret[i][j] = int(stats['champLevel']) - (teamLevel/5.0)
    j+=1

    ret[i][j] = int(stats['kills'])
    j+=1

    ret[i][j] = int(stats['assists'])
    j+=1

    ret[i][j] = int(stats['deaths'])
    j+=1

    ret[i][j] = (int(stats['kills']) + int(stats['assists'])) / max(1,teamKillAssists)
    j+=1

    i+=1


