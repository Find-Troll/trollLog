import pandas as pd
import json
import pymysql
import pickle
import time
import numpy as np
import sys
import os

from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, 
                       password=MYSQL_PASSWORD, db='find_troll', charset='utf8')

sql = (
    "select JSON_EXTRACT(matches,'$.gameDuration') as `gameDuration`,"
    "JSON_EXTRACT(matches,'$.teams[*].win') as win, "
    "JSON_EXTRACT(matches,'$.teams[*].firstBaron') as `firstBaron`,"
    "JSON_EXTRACT(matches,'$.participants[*].stats.goldEarned') as `goldEarned`,"
    "JSON_EXTRACT(matches,'$.participants[*].stats.champLevel') as champLevel, "
    "JSON_EXTRACT(matches,'$.participants[*].stats.kills') as `kill`, "
    "JSON_EXTRACT(matches,'$.participants[*].stats.assists') as `assist` , "
    "JSON_EXTRACT(matches,'$.participants[*].stats.deaths') as `death` from `match` LIMIT 0,1"
);
cursor = conn.cursor()
cursor.execute(sql)
result = cursor.fetchall()

N = 10000
M = 9

ret = np.zeros(N*10*M).reshape(N*10,M)

for i in range(0,N):
    for j in range(0,M):       
        if j!=M-1 : retl = result[i][j][1:-1].split(", ")
        killassistTeam = np.arange(2)
        killassistTeam[0] = killassistTeam[1] = 0
        if j == 0 : 
            for k in range(0,10):
                ret[i*10+k][j] = result[i][j]
        elif j <= 2 : 
            for k in range(0,10):
                if retl[int(k<5)] == 'false' or retl[int(k<5)] == '"Fail"': ret[i*10+k][j] = 0
                else : ret[i*10+k][j] = 1
        elif j <= 4:
            tmp = np.arange(2)
            tmp[0] = tmp[1] = 0
            for k in range(0,10):
                tmp[int(k<5)]+=int(retl[k])
            for k in range(0,10):
                ret[i*10+k][j] = int(retl[k]) - (tmp[int(k<5)]/5.0)
        elif j<=7:
            for k in range(0,10):
                ret[i*10+k][j] = int(retl[k])
        else:
            for k in range(0,10):
                killassistTeam[int(k<5)]+=(ret[i*10+k][5] + ret[i*10+k][6])
            for k in range(0,10):
                ret[i*10+k][M-1] = (ret[i*10+k][5] + ret[i*10+k][6]) / max(killassistTeam[int(k<5)],1)

with open('data.pkl', 'wb') as f:
    pickle.dump(ret, f)
with open('data.pkl', 'rb') as f:
    params = pickle.load(f)