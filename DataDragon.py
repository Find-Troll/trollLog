from riotwatcher import LolWatcher, ApiError
import pandas as pd

api_key = 'RGAPI-9a7a34c1-a844-42a4-9704-e90fe8fe5e3b'
watcher = LolWatcher(api_key)
my_region = 'kr'

latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
static_champ_list = watcher.data_dragon.champions(latest, False, "ko_KR")
static_item_list = watcher.data_dragon.items(latest, "ko_KR")
static_spell = watcher.data_dragon.summoner_spells(latest ,"ko_KR")

spell_dict = []
champ_dict = []
item_dict = [] 
rune_dict = []

for key in static_champ_list['data']:
    row = static_champ_list['data'][key]
    champ_dict.append([row['key'],row['name']])

df = pd.DataFrame(champ_dict)
df.columns = ['key','name']
df.to_csv("./champion.csv")

for key in static_item_list['data']:
    row = static_item_list['data'][key]
    item_dict.append([key,row['name']])
df = pd.DataFrame(item_dict)
df.columns = ['key','name']
df.to_csv("./item.csv")

for key in static_spell['data']:
    row = static_spell['data'][key]
    spell_dict.append([row['key'],row['name']])

df = pd.DataFrame(spell_dict)
df.columns = ['key','name']
df.to_csv("./spell.csv")