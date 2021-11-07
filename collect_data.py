import requests
import json
import pandas as pd
from matplotlib import pyplot
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import plot_confusion_matrix


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

def getData(pos, ssn):
	url = 'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=' + str(pos) + '&PlusMinus=N&Rank=N&Season=' + str(ssn) + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight='

	json = requests.get(url, headers=headers).json()
	data = json['resultSets'][0]['rowSet']
	columns = json['resultSets'][0]['headers']
	index = []
	for player in data:
		index.append(player[0])
	df = pd.DataFrame.from_records(data, index = index, columns=columns) 

	return df


def filterGameData(playerStats, gameStats, ssn):
	df = getData("", ssn)
	df = df.query('MIN > 300')

	df = df[playerStats + gameStats]
	df['POS'] = 'fill'
	df['COL'] = 'Gray'
	for stat in gameStats:
		df[stat] = df[stat] / df.MIN * 36

	positions = ['C', 'F', 'G']
	color_map = {
		'C': 'Red',
		'F': 'Blue',
		'G': 'Green',
	}

	for pos in positions:
		pos_df = getData(pos, ssn)
		for player in df.index.intersection(pos_df.index):
			# df['POS'][player] = pos
			# df['COL'][player] = color_map[pos]
			df.at[player, 'POS'] = pos
			df.at[player, 'COL'] = color_map[pos]
			# if player in df.index:
				# if df['POS'][player] != 'fill':
					# df.drop([player])
				# else:
					# df['POS'][player] = pos
					# df['COL'][player] = color_map[pos]

	# print(df)
	return df

def getBioData(df, ssn):
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

	df_bio = df_bio.loc[list(df.index)]
	df['HEIGHT'] = df_bio['PLAYER_HEIGHT_INCHES']
	df['WEIGHT'] = df_bio['PLAYER_WEIGHT']

	# bah.write(df.to_string())

	# for player in index:
		# df['HEIGHT'] = df_bio['PLAYER_HEIGHT_INCHES']
		# df['HEIGHT'][player] = df_bio['PLAYER_HEIGHT_INCHES'][player]
	
def makeGraph(df, xVal, yVal):
	plot = df.plot.scatter(x = xVal, y = yVal, c = 'COL', s = 'SZ')
	pyplot.show() 

def getModel(df, totalGameStats):
	dataX = df[totalGameStats]
	dataY = df['POS']

	trainX, testX, trainY, testY = train_test_split(
		dataX, dataY, test_size = 0.2, shuffle = True
	)

	classifier = LogisticRegression(max_iter = 10000)
	classifier.fit(trainX, trainY)
	preds = classifier.predict(testX)

	positions = classifier.classes_
	coefDf = pd.DataFrame(classifier.coef_, index = positions, columns = totalGameStats)

	for i, pos in enumerate(positions):
		coefDf = abs(coefDf)
		coefDf.sort_values(by = [positions[i]], axis = 1, inplace = True)
		# print(coefDf.iloc[:, 0])
		cols = coefDf.columns
		# print("For %s, the weakest indicators are %s, %s, %s" % (pos, cols[0], cols[1], cols[2]))
		# print("The strongest indicators are %s, %s, %s" % (cols[-1], cols[-2], cols[-3]))

	correct = 0
	incorrect = 0
	i = 0
	for pred, gt in zip(preds, testY):
		if pred == gt: 
			correct += 1
		else: 
			incorrect += 1
			# print(i)
		i += 1
			
	print(f"Correct: {correct}, Incorrect: {incorrect}, % Correct: {correct/(correct + incorrect): 5.2}")

	# plot_confusion_matrix(classifier, testX, testY)
	pyplot.show()

def solve(ssn):
	playerStats = ['PLAYER_NAME','AGE','GP','MIN']
	gameStats = ['FGM','FGA','FG3M','FG3A','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','BLKA','PF','PFD','PTS'];
	# gameStats = ['FG3M', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK']
	totalGameStats = gameStats + ['HEIGHT', 'WEIGHT']

	df = filterGameData(playerStats, gameStats, ssn)
	getBioData(df, ssn)
	df['SZ'] = (df['MIN'] - 250) ** (0.75) / 3

	bah = open('output.txt', 'w')
	bah.write(df.to_string())

	index = df.index

	std_scaler = StandardScaler()
	df_scaled_game = std_scaler.fit_transform(df[totalGameStats])
	df_scaled_game = pd.DataFrame(df_scaled_game, index = index, columns = totalGameStats)

	df_scaled = df_scaled_game
	for stat in playerStats + ['POS']:
		df_scaled[stat] = 0
	for player in index:
		for stat in playerStats + ['POS']:
			df_scaled[stat] = df[stat]
			# df_scaled[stat][player] = df[stat][player]
			# df_scaled[stat][player] = df[stat][player]

	# makeGraph(df, 'REB', 'AST')
	# makeGraph(df, 'HEIGHT', 'WEIGHT')
	# makeGraph(df, 'FGM', "FG3M")
	# makeGraph(df, 'AGE', 'PTS')
	# makeGraph(df, 'STL', 'BLK')

	getModel(df_scaled, totalGameStats)	

def main():
	ssn = '2020-21'
	seasons = ['2004-05', '2009-10', '2014-15', '2019-20']
	for ssn in seasons:
		solve(ssn)

	# playerStats = ['PLAYER_NAME','AGE','GP','MIN']
	# gameStats = ['FGM','FGA','FG3M','FG3A','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','BLKA','PF','PFD','PTS'];
	# # gameStats = ['FG3M', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK']
	# totalGameStats = gameStats + ['HEIGHT', 'WEIGHT']

	# df = filterGameData(playerStats, gameStats)
	# getBioData(df)
	# df['SZ'] = (df['MIN'] - 250) ** (0.75) / 3

	# bah = open('output.txt', 'w')
	# bah.write(df.to_string())

	# index = df.index

	# std_scaler = StandardScaler()
	# df_scaled_game = std_scaler.fit_transform(df[totalGameStats])
	# df_scaled_game = pd.DataFrame(df_scaled_game, index = index, columns = totalGameStats)

	# df_scaled = df_scaled_game
	# for stat in playerStats + ['POS']:
	# 	df_scaled[stat] = 0
	# for player in index:
	# 	for stat in playerStats + ['POS']:
	# 		df_scaled[stat] = df[stat]
	# 		# df_scaled[stat][player] = df[stat][player]
	# 		# df_scaled[stat][player] = df[stat][player]

	# # makeGraph(df, 'REB', 'AST')
	# # makeGraph(df, 'HEIGHT', 'WEIGHT')
	# # makeGraph(df, 'FGM', "FG3M")
	# # makeGraph(df, 'AGE', 'PTS')
	# # makeGraph(df, 'STL', 'BLK')

	# getModel(df_scaled, totalGameStats)	

main()
