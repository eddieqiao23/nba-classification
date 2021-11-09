import requests
import pandas as pd
import numpy as np
from matplotlib import pyplot
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import plot_confusion_matrix
from sklearn.ensemble import RandomForestClassifier


headers = {
		'Host': 'stats.nba.com',
		'Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
		'Referer': 'https://stats.nba.com/',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.5',
	}

def getData(pos, ssn):
	# Gets the basic data such as points, rebounds, assists, field goal percentage, etc.
	# If pos isn't an empty string, then it outputs the info for players of a certain position
	url = 'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=' + str(pos) + '&PlusMinus=N&Rank=N&Season=' + str(ssn) + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight='

	# Gets JSON from the URL and converts it into a DataFrame
	json = requests.get(url, headers = headers).json()
	data = json['resultSets'][0]['rowSet']
	columns = json['resultSets'][0]['headers']
	index = []
	for player in data:
		index.append(player[0])
	df = pd.DataFrame.from_records(data, index = index, columns=columns) 

	return df

def getBioData(df, ssn):
	# Gets the player's name, height, and weight
	url = 'https://stats.nba.com/stats/leaguedashplayerbiostats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=&LeagueID=00&Location=&Month=&OpponentTeamID=&Outcome=&PORound=&PerMode=Totals&Period=&PlayerExperience=&PlayerPosition=&Season=' + ssn + '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=&VsConference=&VsDivision=&Weight='
	json = requests.get(url, headers=headers).json()
	data = json['resultSets'][0]['rowSet']
	columns = json['resultSets'][0]['headers']

	# Changes the index to be the players' IDs
	ids = []
	for player in data:
		ids.append(player[0])
	df_bio = pd.DataFrame.from_records(data, index = ids, columns = columns) 

	# Takes the height and weight columns from the data and puts them into df_bio
	name = ['PLAYER_NAME']
	bio_stats = ['PLAYER_HEIGHT_INCHES', 'PLAYER_WEIGHT']
	df_bio = df_bio[name + bio_stats]

	# Gets rid of the players who are not in df (since some played <300 minutes)
	df_bio = df_bio.loc[list(df.index)]
	# For some reason, the player's weight is an object instead of an int
	df_bio['PLAYER_WEIGHT'] = df_bio['PLAYER_WEIGHT'].astype(np.int64)
	# Puts the data into df
	df['HEIGHT'] = df_bio['PLAYER_HEIGHT_INCHES']
	df['WEIGHT'] = df_bio['PLAYER_WEIGHT']

def filterGameData(playerStats, gameStats, ssn):
	# Filters the data to be only players who played 300 minutes or more 
	df = getData("", ssn)
	df = df.query('MIN > 300')

	# Converts to per 36
	df = df[playerStats + gameStats]
	for stat in gameStats:
		df[stat] = df[stat] / df.MIN * 36

	# Gets the position for each player and a corresponding color (so we can graph later)
	positions = ['C', 'F', 'G']
	color_map = {
		'C': 'Red',
		'F': 'Blue',
		'G': 'Green',
	}

	for pos in positions:
		# pos_df.index has all the players who played a certain position
		pos_df = getData(pos, ssn)
		for player in df.index.intersection(pos_df.index):
			df.at[player, 'POS'] = pos
			df.at[player, 'COL'] = color_map[pos]

	return df
	
def makeGraph(df, xVal, yVal):
	# Makes a graph of the data
	plot = df.plot.scatter(x = xVal, y = yVal, c = 'COL', s = 'SZ')
	pyplot.show() 

def getModel(df, totalGameStats):
	# Gets the model for the data and outputs the results
	dataX = df[totalGameStats]
	dataY = df['POS']

	# Splits data into training and testing
	trainX, testX, trainY, testY = train_test_split(
		dataX, dataY, test_size = 0.2, shuffle = True
	)

	# Uses a logistic regression to predict the results
	classifierLog = LogisticRegression(max_iter = 100)
	classifierLog.fit(trainX, trainY)
	predsLog = classifierLog.predict(testX)

	# Looks through the coefficients to determine the most "important" factors (not perfect measurement)
	positions = classifierLog.classes_
	coefDf = pd.DataFrame(classifierLog.coef_, index = positions, columns = totalGameStats)

	for i, pos in enumerate(positions):
		coefDf = abs(coefDf)
		coefDf.sort_values(by = [positions[i]], axis = 1, inplace = True)
		cols = coefDf.columns
		print("For %s, the weakest indicators are %s, %s, %s" % (pos, cols[0], cols[1], cols[2]))
		print("The strongest indicators are %s, %s, %s" % (cols[-1], cols[-2], cols[-3]))

	classifierRandom = RandomForestClassifier(n_estimators = 100)
	classifierRandom.fit(trainX, trainY)
	predsRandom = classifierRandom.predict(testX)

	# Finds the amount that are correct and wrong
	for i, preds in enumerate([predsLog, predsRandom]):
		correct = 0
		incorrect = 0
		for pred, gt in zip(preds, testY):
			if pred == gt: 
				correct += 1
			else: 
				incorrect += 1
				
		# Outputs the results
		if i == 0: 
			print("\nResults for a Logistic Regression:")
		else:
			print("\nResults for a Random Forest Classifier:")

		print(f"Correct: {correct}, Incorrect: {incorrect}, % Correct: {correct/(correct + incorrect): 5.2}")
		plot_confusion_matrix(classifierLog, testX, testY)
		pyplot.show()

def main():
	ssn = '2020-21'

	playerStats = ['PLAYER_NAME','AGE','GP','MIN']
	gameStats = ['FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 
	'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS']
	totalGameStats = gameStats + ['HEIGHT', 'WEIGHT']

	df = filterGameData(playerStats, gameStats, ssn)
	getBioData(df, ssn)
	# Formula for the size of the dots so it isn't too big or too small, but the difference is noticeable
	df['SZ'] = (df['MIN'] - 250) ** (0.75) / 3
	index = df.index

	# Scales the data 
	std_scaler = StandardScaler()
	df_scaled_game = std_scaler.fit_transform(df[totalGameStats])
	df_scaled_game = pd.DataFrame(df_scaled_game, index = index, columns = totalGameStats)

	df_scaled = df_scaled_game
	for stat in playerStats + ['POS']:
		df_scaled[stat] = 0
	for player in index:
		for stat in playerStats + ['POS']:
			df_scaled[stat] = df[stat]

	# Makes a bunch of graphs
	makeGraph(df, 'REB', 'AST')
	makeGraph(df, 'HEIGHT', 'WEIGHT')
	makeGraph(df, 'FGM', "FG3M")
	makeGraph(df, 'STL', 'BLK')
	makeGraph(df, 'AGE', 'PTS') # A graph that tells you nothing

	getModel(df_scaled, totalGameStats)	

main()
