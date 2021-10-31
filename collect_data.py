import requests
import json
from pprint import pprint
import pandas as pd
from matplotlib import pyplot
from matplotlib.colors import ListedColormap
import sklearn.linear_model
import sklearn.datasets
import sklearn.preprocessing
import sklearn.model_selection
import sklearn.metrics
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import plot_confusion_matrix

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
# print(columns)
index = []
for player in data:
    index.append(player[0])
df = pd.DataFrame.from_records(data, index = index, columns=columns) 
df = df.query('MIN > 150')
# df.drop(['PLAYER_ID'], axis = 1)
# df = pd.DataFrame.from_records(data, columns=columns) 
# print(df)

# print(df)
# for key in df.iloc[0]:
	# print(key)
# print(df.iloc[0]["PTS"])

playerStats = ['PLAYER_NAME','AGE','GP','MIN']
gameStats = ['FGM','FGA','FG3M','FG3A','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','BLKA','PF','PFD','PTS'];
df = df[playerStats + gameStats]
df['POS'] = 'C'
for stat in gameStats:
	df[stat] = df[stat] / df.MIN * 36

positions = ['C', 'F', 'G']
color_map = {
	'C': 'Red',
	'F': 'Blue',
	'G': 'Green',
}

for pos in positions:
    url = 'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=' + str(pos) + '&PlusMinus=N&Rank=N&Season=' + str(ssn) + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight='
    json = requests.get(url, headers=headers).json()
    data = json['resultSets'][0]['rowSet']
    columns = json['resultSets'][0]['headers']
    pos_df = pd.DataFrame.from_records(data, columns=columns) 
    # print(pos_df)
    # print(pos_df['PLAYER_NAME'])
    for player in pos_df['PLAYER_ID']:
        # print(player)
        df['POS'][player] = color_map[pos]
        # df[player]['POS'] = pos

# bah = open('output.txt', 'w')
# for thing in index:
    # bah.write(df.to_string())

url = 'https://stats.nba.com/stats/leaguedashplayerbiostats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=&LeagueID=00&Location=&Month=&OpponentTeamID=&Outcome=&PORound=&PerMode=Totals&Period=&PlayerExperience=&PlayerPosition=&Season=' + ssn + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=&VsConference=&VsDivision=&Weight='

json = requests.get(url, headers=headers).json()
data = json['resultSets'][0]['rowSet']
columns = json['resultSets'][0]['headers']
index = []
for player in data:
    index.append(player[0])
df_bio = pd.DataFrame.from_records(data, index = index, columns=columns) 
name = ['PLAYER_NAME']
bio_stats = ['PLAYER_HEIGHT_INCHES', 'PLAYER_WEIGHT']
df_bio = df_bio[name + bio_stats]

df['HEIGHT'] = 0
df['WEIGHT'] = 0
for player in index:
	df['HEIGHT'][player] = df_bio['PLAYER_HEIGHT_INCHES'][player]
	df['WEIGHT'][player] = df_bio['PLAYER_WEIGHT'][player]
	
# bah = open('output.txt', 'w')
# for thing in index
    # bah.write(df.to_string())

plot = df.plot.scatter(x = 'HEIGHT', y = 'WEIGHT', c = 'POS')
pyplot.show()

dataX = df[gameStats + ['HEIGHT', 'WEIGHT']]
dataY = df['POS']

trainX, testX, trainY, testY = sklearn.model_selection.train_test_split(
    dataX, dataY, test_size = 0.2, shuffle = True
)

classifier = LogisticRegression(max_iter = 10000)
classifier.fit(trainX, trainY)
preds = classifier.predict(testX)


bah = open('output.txt', 'w')
bah.write(testY.to_string())

correct = 0
incorrect = 0
i = 0
for pred, gt in zip(preds, testY):
	if pred == gt: 
		correct += 1
	else: 
		incorrect += 1
		print(i)
	i += 1
		


print(f"Correct: {correct}, Incorrect: {incorrect}, % Correct: {correct/(correct + incorrect): 5.2}")

plot_confusion_matrix(classifier, testX, testY)
pyplot.show()
