import pandas as pd
import json
import pickle
import numpy as np
import requests
import json
import os
import sys
sys.path.append(os.pardir) #현재 경로 폴더 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) #상위 폴더 path추가
from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD
from bs4 import BeautifulSoup
#소환사 이름으로 op.gg에서 crawling
def Trim(summonerName):
    summonerName = summonerName
    source = requests.get("https://www.op.gg/summoner/userName=" + summonerName).text
    soup = BeautifulSoup(source, "html.parser")
    keywords = soup.select("div.MostChampionContent")

    keywords = [str(each_line.get_text().strip()) for each_line in keywords]
    if(len(keywords) == 0 ): return np.zeros(7*2).reshape(7,2)
    keywords = keywords[1].split('\n')

    tmp = []
    #replace("찾을값", "바꿀값", [바꿀횟수])
    for i in range(len(keywords)):
        keywords[i] = keywords[i].replace('\t', '').replace('\n', '')
        if(len(keywords[i])>0):
            tmp.append(keywords[i])
    keywords = tmp
    tmp = []
    tmp2 = []
    cnt = 0
    for i in range(len(keywords)):
        tmp.append(keywords[i])
        cnt+=1
        if(cnt%11==0 and i!=0): 
            tmp2.append(tmp)
            tmp = []
            cnt = 0
    keywords = tmp2

    winRate = []
    for i in range(len(keywords)):
        tmp = []
        tmp.append(keywords[i][0]) #op.gg champ명
        tmp.append(keywords[i][9]) #해당 챔피언 승률
        tmp.append(keywords[i][10]) #해당 챔피언 플레이 판 수
        winRate.append(tmp)

    #0번째 인덱스 : 승률
    #1번째 인덱스 : 판 수
    most7PicksWinRate = []
    for i in range(len(winRate)):
        most7PicksWinRate.append([float(winRate[i][1].split("%")[0]),float(winRate[i][2].split(" ")[0])])
    if(len(winRate) < 7):
        for i in range(0,7 - len(winRate)): most7PicksWinRate.append([0.,0.])
    return most7PicksWinRate

API_HOST = 'http://52.78.119.98:4000'
TROLL_NAME = '행복한패배'
most7PicksWinRate = Trim(TROLL_NAME)
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

tmp = np.zeros(N*14).reshape(N,14)
for i in range(N):
    idx = 0
    for k in range(0,7):
        for j in range(0,2):
            tmp[i][idx] = most7PicksWinRate[k][j]
            idx+=1
addedArray = np.hstack((ret,tmp))
print(addedArray.shape)
print(addedArray)
