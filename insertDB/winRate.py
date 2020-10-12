import sys,os
sys.path.append(os.pardir) #현재 경로 폴더 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) #상위 폴더 path추가

from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD

import requests
import numpy as np
import pymysql

from bs4 import BeautifulSoup

def Trim(summonerName):
    summonerName = summonerName
    source = requests.get("https://www.op.gg/summoner/userName=" + summonerName).text
    soup = BeautifulSoup(source, "html.parser")
    keywords = soup.select("div.MostChampionContent")

    keywords = [str(each_line.get_text().strip()) for each_line in keywords]
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
    return winRate

def InsertMost7PicksWinRateDb(summonerName):
    conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db='FindTroll', charset='utf8')
    curs = conn.cursor()
    sql = "REPLACE INTO `win_rate` (summonerName, info) VALUES (%s,%s)"
    trimedData = Trim(summonerName) #crawling data가져오기
    info = ""
    for i in range(len(trimedData)):
        winRateNum = trimedData[i][1].split("%")[0]
        played = trimedData[i][2].split(" ")[0]
        info += "[" + trimedData[i][0] + "," + winRateNum + "," + played + "]"
        if(i!=len(trimedData)-1): info+=","

    print(info)
    curs.execute(sql,(summonerName,info))
    print("inserted")
    conn.commit()

InsertMost7PicksWinRateDb("행복한패배")


