import sys
import os
sys.path.append(os.pardir) #현재 경로 폴더 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) #상위 폴더 path추가
import pandas as pd
import json
import pymysql
import pickle
import time
import numpy as np
import requests
from bs4 import BeautifulSoup
from auth import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD

conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, 
                       password=MYSQL_PASSWORD, db='FindTroll', charset='utf8')


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
    return most7PicksWinRate

sql = (
    "select JSON_EXTRACT(matches,'$.gameDuration') as `gameDuration`,"
    "JSON_EXTRACT(matches,'$.participants[*].stats.win') as win, "
    "JSON_EXTRACT(matches,'$.teams[*].firstBaron') as `firstBaron`,"
    "JSON_EXTRACT(matches,'$.participants[*].stats.goldEarned') as `goldEarned`,"
    "JSON_EXTRACT(matches,'$.participants[*].stats.champLevel') as champLevel, "
    "JSON_EXTRACT(matches,'$.participants[*].stats.kills') as `kill`, "
    "JSON_EXTRACT(matches,'$.participants[*].stats.assists') as `assist` , "
    "JSON_EXTRACT(matches,'$.participants[*].stats.deaths') as `death`,"
    "JSON_EXTRACT(matches,'$.participantIdentities[*].player.accountId') as `id`,"
    "JSON_EXTRACT(matches,'$.participantIdentities[*].player.summonerName') as `name` from `match`"
);

cursor = conn.cursor()
cursor.execute(sql)
result = cursor.fetchall()
N = 20
M = 10

s_name = []
ret = np.zeros(N*10*M).reshape(N*10,M)
trollAccount = '1rsGJq_S2kSTQ-I3myielZCe1aW-avXTlQ_2-hC1v5WF-7d9bC2-6tLo'
for i in range(0,N):
    for j in range(0,M):       
        retl = result[i][j][1:-1].split(", ")
        killassistTeam = np.arange(2)
        killassistTeam[0] = killassistTeam[1] = 0

        if j == 0 : 
            for k in range(0,10):
                ret[i*10+k][j] = result[i][j]

        elif j <=1:
            for k in range(0,10):
                if retl[k] == 'false': ret[i*10+k][j] = 0
                else : ret[i*10+k][j] = 1

        elif j <= 2 : 
            for k in range(0,10):
                if retl[int(k>=5)] == 'false' : ret[i*10+k][j] = 0
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

        elif j<=8:
            for k in range(0,10):
                ret[i*10+k][j] = int(retl[k][1:-1] == trollAccount)
        elif j==9:
            for k in range(0,10):
                killassistTeam[int(k<5)]+=ret[i*10+k][5]
            for k in range(0,10):
                ret[i*10+k][9] = (ret[i*10+k][5] + ret[i*10+k][6]) / max(killassistTeam[int(k<5)],1)
            for k in range(0,10):
                s_name.append(retl[k][1:-1])
            

idx=0
# 트롤러, 행패
tmp = np.zeros((N)*(M-1)).reshape((N),(M-1))

for i in range(0,10*N):
    if ret[i][8] == 1.0 and ret[i][1] == 0.0:
        for j in range(0,M-1):
            if j==M-2 : tmp[idx][j] = ret[i][j+1]
            else : tmp[idx][j] = ret[i][j]
        idx+=1

# 진또배기
r_data = np.zeros(N*10*(M-1)).reshape((N*10), (M-1))

for i in range(0, 10*N):
    for j in range(0, M-1):
        if j==M-2 : r_data[i][j] = ret[i][j+1]
        else : r_data[i][j] = ret[i][j]


#한 소환사이름에 대해 1픽 당 승률, 판 수를 한 짝으로 총 7개의 짝을 구성, 최종적으로 1차원 배열(14개의 index)로 만드는 과정
winRate = np.zeros(N*10*(14)).reshape((N*10), (14))
is_exist = np.zeros(N*10).reshape(N*10)

count_exist = 0 # 실제 존재하는 소환사 갯수 = 진짜 데이터 수
for i in range(len(s_name)):
    w_tmp = Trim(s_name[i])
    dist = []
    for j in range(len(w_tmp)):
        for k in range(0, 2):
            dist.append(w_tmp[j][k])
    if(dist[1] != 0):
        is_exist[i] = True
        count_exist += 1
    print(s_name[i])
    print(len(dist))
    print(dist)
    for j in range(0, 14):
        if(j%2==0): dist[j] = (dist[j])/100.0
        winRate[i][j] = dist[j]

#트롤 결정 feature들을 담은 r_data에 winRate column 추가
addedArray = np.hstack((r_data,winRate))
for_train = np.array([(is_exist[i] == 1) for i in range(len(is_exist)) ]) # True , False ...

last_data = addedArray[for_train] # 진짜 데이터 feature 23개

last_len = len(last_data) # 진짜 데이터 길이


# X = last_data
# feature_num = len(X[0]) # feature 갯수
# # list to pandas, list to pandas series
# panda_X = pd.DataFrame(X)
# # print(panda_X)
# print("panda_X Shape :", panda_X.shape)

# print("X dataShape : ", X.shape)
# print("Troll dataShape : ", X_troll.shape)
# data = StandardScaler().fit_transform(X)  # normalize 기능
# print("DataShape : ", data.shape)
# n_samples, n_features = data.shape
# print("n_sample :", n_samples, end=" / ")
# print("n_features :", n_features)

# pca = PCA(n_components=feature_num)
# pca.fit(X)
# print("singular value :", pca.singular_values_)
# print("singular vector :\n", pca.components_.T)
# print("eigen_value :", pca.explained_variance_)
# print("explained variance ratio :", pca.explained_variance_ratio_)
# pca = PCA(n_components=0.99999)
# X_reduced = pca.fit_transform(X)
# print("X_redu Shape : ", X_reduced.shape)
# print("explained variance ratio :", pca.explained_variance_ratio_)
# print("선택한 차원수 :",pca.n_components_)
# print(X_reduced.shape)

# plt.figure(figsize=(9, 8))
# n_clusters = 6            # 클러스터 수

# X_reduced = StandardScaler().fit_transform(X_reduced)
# X = StandardScaler().fit_transform(X)
# two_means = MiniBatchKMeans(n_clusters=n_clusters)
# dbscan = DBSCAN(eps=0.6)  # 밀도 기반 클러스터링
# spectral = SpectralClustering(n_clusters=n_clusters, affinity="nearest_neighbors")
# ward = AgglomerativeClustering(n_clusters=n_clusters)
# affinity_propagation = AffinityPropagation(damping=0.9, preference=-200)    # 매우 느림
# clustering_algorithms = (
#     ('K-Means', two_means),
#     ('DBSCAN', dbscan),
#     ('Hierarchical Clustering', ward),
#     ('Spectral Clustering', spectral),
#     # ('Affinity Propagation', affinity_propagation),
# )

# plot_num = 1

# for j, (name, algorithm) in enumerate(clustering_algorithms):
#     with ignore_warnings(category=UserWarning):
#         algorithm.fit(X_reduced)
#     if hasattr(algorithm, 'labels_'):
#         y_pred = algorithm.labels_.astype(np.int)
#     else:
#         y_pred = algorithm.predict(X_reduced)
#     y_pred += 1
#     plt.subplot(len(clustering_algorithms), 2, plot_num)
#     print("y_pred :", y_pred)
#     print("len :", len(y_pred))
#     y_max = np.max(y_pred)
#     print("maxnum :", np.max(y_pred))
#     colors = plt.cm.tab10(np.arange(20, dtype=int))
#     print("color : ", colors.shape)
#     # s 포인트 크기, color 배열
#     y_reduced = y_pred[:N*10]
#     y_troll = []
#     for i in range (0, len(X_troll)):
#         y_troll.append(0)
#     print("Y 트롤 : ")
#     print(y_reduced)
#     plt.scatter(X_reduced[:last_len,0], X_reduced[:last_len,1], s=2, color=colors[y_reduced])
#     plt.scatter(X_reduced[lase_len:,0], X_reduced[last_len:,1], s=2, color=colors[y_troll])
#     plt.xticks(())
#     plt.yticks(())
#     plot_num += 1

# plt.tight_layout()
# plt.show()