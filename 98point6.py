
# Importing the required libraries
import pandas as pd
import numpy as np
import requests
import json
import csv
import matplotlib.pyplot as plt

# Importing games data into pandas dataframe
games = pd.read_csv("game_data.csv")

# Create a new csv file named 'players' in write mode
f = csv.writer(open("players.csv", "wb+"))
f.writerow(["player_id", "country"])

# Get the data using requests library in json format and write the data into csv file
for i in range(0,524):
    json_data = requests.get("https://x37sv76kth.execute-api.us-west-1.amazonaws.com/prod/users?page=" + str(i))
    data = json_data.json()
    for entry in data:
        f.writerow([entry['id'],entry['data']['nat']])
        
# Importing players data into pandas dataframe
players = pd.read_csv("players.csv")

# Question 1 - Out of all the games, what is the percentile rank of each column used as the 
# first move in a game? That is, when the first player is choosing a column for their first move, 
# which column most frequently leads to that player winning the game?

print("When the first player is choosing a column for their first move,which column most frequently leads to that player winning the game?\n\n")

# Merge 2 dataframes (move_number = 1 and result = win) on field game_id,player_id via inner join 
# and get different columns value counts
wins = (games[games['move_number'] == 1]).merge((games[games['result'] == 'win'][['game_id','player_id','result']]),on=['game_id','player_id'],how='inner')['column'].value_counts()


print(wins)
print("\n\n")

print("Hence column 4 has the majority wins when it is used as a first move during the game.\n\n")

# Question 2 - How many games has each nationality of player played?

print("How many games has each nationality of player played?\n\n")

# Merge 2 dataframes (move_number = 1,2 and players) on field player_id via inner join 
# and get different countries value counts
games_played = (games[games['move_number'].isin([1,2])]).merge(players,on='player_id',how='inner')['country'].value_counts()
print(games_played)
print("\n\n")

print("Hence players coming from Republic of Ireland have played the highest and Brazil players have played the lowest.\n\n")

# Question 3 - Visualize the win percentage by country

# Merge 2 dataframes (result = win and players) on field player_id via inner join 
# and get different countries value counts
wins = (games[games['result'] == 'win']).merge(players,on='player_id',how='inner')['country'].value_counts()

# Construct a dataframe with country names, their wins and the number of games they have played
winper = pd.concat([pd.DataFrame(wins.sort_index().index),pd.DataFrame(wins.sort_index().values),pd.DataFrame(games_played.sort_index().values)],axis=1)
winper.columns = ['country','wins','played']
winper['win%'] = (winper['wins'] / winper['played']) * 100

# Display the dataframe
winper = winper.round(2).sort_values(by='win%')
print(winper)

# Bar-Plot of win percentages
X = np.arange(len(winper['country']))
X_ticks_labels = winper['country']
Y = winper['win%']

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(X,Y,align='center',alpha=0.5)
ax.set_xticks(X)
ax.set_xticklabels(X_ticks_labels,rotation='vertical',fontsize=12)
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
plt.title("Win percentage by country")
plt.xlabel("Countries")
plt.ylabel("Win percentage")


print("Switzerland have the highest win percentage with 27.9% and Denmark have the lowest with 24.89%.\n\n")

# Question 4 - Does the entire game is determined by the first few moves?

print("Does the entire game is determined by the first few moves?\n\n")

print("Hypothesis: Compare first few moves pattern versus the whole game's moves pattern\n\n")

print("First few moves patterns\n\n")

# Merge 2 dataframes (move number = 1-6 and result = draw,win) on field game_id via inner join 
df2 = games.merge(games[games['result'].isin(['draw','win'])][['game_id','result','move_number']],on='game_id',how='inner')
del df2['result_x']

df2['percentage'] = (df2['move_number_x'] / df2['move_number_y']) * 100

first_few_moves = df2[df2['percentage'] <= 40.0]

abc = first_few_moves.groupby(['game_id','result_y'])['column'].apply(list)

dff = pd.concat([pd.DataFrame(abc.index.get_level_values('result_y')),pd.DataFrame(abc.values)],axis=1)

# Column names for the dataframe df
dff.columns = ['result','patterns']

# Function to convert list of numbers into sequence
def list_to_str(lst):
    ss = ""
    for i in lst:
        ss += str(i)
    return ss  

# Create a new column namd 'pattern' by applying the function list_to_str to every row in df
dff['pattern'] = dff['patterns'].apply(list_to_str)

# Delete the column 'patterns'
del dff['patterns']

# Create a Series grouping by the pattern and the corresponding result for that pattern
print(dff.groupby('pattern')['result'].apply(list)[0:10])
print("\n\n")

print("We can clearly see from the above data that there is no fixed result matching the initial set of moves/patterns. For example if the initial 6 moves are '111143', then we observe the results of 6 games to be 'draw, draw, win, win, draw, draw'. This is the same case with the other patterns as well. Hence we do not have a concrete evidence that initial set of moves decide the results. However, let us dig deep by seeing the whole game's pattern.\n\n")

# Number of unique patterns
print(sum(dff['pattern'].value_counts() == 1))

# Percentage of unique patterns
print(sum(dff['pattern'].value_counts() == 1) / float(len(games['game_id'].unique())) * 100)
print("\n")

print("~16% of the games are different from each other.\n\n")

print("Whole games patterns\n\n")

games_all_moves = games.merge(games[games['result'].isin(['draw','win'])][['game_id','result']],on='game_id',how='inner')

# Construct a dataframe with 2 columns (result and pattern of first 6 moves)
abc = games_all_moves.groupby(['game_id','result_y'])['column'].apply(list)
df3 = pd.concat([pd.DataFrame(abc.index.get_level_values('result_y')),pd.DataFrame(abc.values)],axis=1)

# Colum names for the dataframe df
df3.columns = ['result','patterns']

# Create a new column namd 'pattern' by applying the function list_to_str to every row in df
df3['pattern'] = df3['patterns'].apply(list_to_str)

# Delete the column 'patterns'
del df3['patterns']

# Create a Series grouping by the pattern and the corresponding result for that pattern
print(df3.groupby('pattern')['result'].apply(list)[0:10])
print("\n\n")

# Number of unique patterns
print(sum(df3['pattern'].value_counts() == 1))

# Percentage of unique patterns
print(sum(df3['pattern'].value_counts() == 1) / float(len(games['game_id'].unique())) * 100)
print("\n\n")

print("Conclusions:\n\n")

print("We can see from the first few patterns that the results are not the same (results are the combination of wins and draws).\n")
print("A pattern for intial set of moves can have multiple same victories. However we cannot predict the result only with these as we can see that the result varies after all the moves are handled.\n")
print("There are a total of 9890 unique patterns the way the game is played. This also gives us an indication that the result of the game is not just decided on the initial set of moves.\n")
print("Hence ~99% of the games are different from each other (Have different pattern of moves). This is a strong conclusion that the initial set of moves do not decide on the game.\n")
print("Initially when we considered first few moves (6 moves), we had good 91% of the games which were similar to each other in their moves patterns. It would be so easy to conclude with such a big number that the results could be predicted. However, when we saw the entire set of moves, this number decreased to just 1%!!!\n")

# Show the bar-plot
plt.show()




