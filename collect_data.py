import requests
import json
from pprint import pprint
import pandas as pd

url_base = 'https://stats.nba.com/stats/cumestatsplayer'
# url = 'https://stats.nba.com/stats/cumestatsplayer?GameIDs=0021700807&LeagueID=00&PlayerID=2544&Season=2019-20&SeasonType=Regular+Season'

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


# response = requests.get(url_base, params=parameters, headers=headers)
# content = json.loads(response.content)
# lbjStats = content['resultSets'][1]
# # pprint(lbjStats['headers'])
# # pprint(lbjStats['rowSet'][0])
# for i in range(len(lbjStats['headers'])):
# 	print(lbjStats['headers'][i], lbjStats['rowSet'][0][i])


ssn = '2020-21'
url = 'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=' + str(ssn) + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight='

json = requests.get(url, headers=headers).json()
data = json['resultSets'][0]['rowSet']
columns = json['resultSets'][0]['headers']
df = pd.DataFrame.from_records(data, columns=columns) 

# print(df)
# for key in df.iloc[0]:
	# print(key)
# print(df.iloc[0]["PTS"])

playerStats = ['PLAYER_NAME','AGE','GP','MIN']
gameStats = ['FGM','FGA','FG3M','FG3A','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','BLKA','PF','PFD','PTS'];
df = df[playerStats + gameStats]
for stat in gameStats:
	df[stat] = df[stat] / df.MIN * 36

print(df)

positions = ['C', 'F', 'G']

for pos in positions:
	url = 'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=' + str(pos) + '&PlusMinus=N&Rank=N&Season=' + str(ssn) + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight='

	json = requests.get(url, headers=headers).json()
	data = json['resultSets'][0]['rowSet']
	columns = json['resultSets'][0]['headers']
	df_c = pd.DataFrame.from_records(data, columns=columns) 
	print(df_c)