import requests
import json
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

headers = {
		'Host': 'stats.nba.com',
		'Connection': 'keep-alive',
		'Accept': 'application/json, text/plain, */*',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
		'Referer': 'https://stats.nba.com/',
		"x-nba-stats-origin": "stats",
		"x-nba-stats-token": "true",
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9',
	}

parameters = {
	'GameIDs': '0021700807',
	'LeagueID': '00',
	'PlayerID': '2544',
	'Season': "2019-20",
	'SeasonType': 'Regular Season',
}


url = 'https://stats.nba.com/stats/leaguedashplayerbiostats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=&LeagueID=00&Location=&Month=&OpponentTeamID=&Outcome=&PORound=&PerMode=Totals&Period=&PlayerExperience=&PlayerPosition=&Season=' + ssn + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=&VsConference=&VsDivision=&Weight='

json = requests.get(url, headers=headers).json()
data = json['resultSets'][0]['rowSet']
columns = json['resultSets'][0]['headers']
# print(columns)
index = []
for player in data:
    index.append(player[0])
df = pd.DataFrame.from_records(data, index = index, columns=columns) 
useful_stats = ['PLAYER_NAME', 'PLAYER_HEIGHT_INCHES', 'PLAYER_WEIGHT']
df = df[useful_stats]

bah = open('output.txt', 'w')
for thing in index:
    bah.write(df.to_string())