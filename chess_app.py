%reset -f
import os
import pandas as pd
import requests 

# Define the player's name. 
player_name= 'raekwan'

# Use the player name within the url string. 
archives_url_pull= 'https://api.chess.com/pub/player/' + player_name + '/games/archives'

archives_url_pull

# Pull the archives data which will show which YYYY/MM the player had games
archives= requests.get(archives_url_pull)

archives.text

type(archives.text)

type(archives)

# strip off the dictionary structure-like components of the string and other components that aren't necessary. 
stripper_list= ['{"archives":','}', ']','[']
for i, j in enumerate(stripper_list):
    if (i == 0) and type(archives== 'requests.models.Response'):
        archives= archives.text.replace(j, '')
    else: 
        archives= archives.replace(j, '')


archives

# write out to a file. 
with open("archives.txt", "w") as f:
    f.write(archives)

# import the data and transpose the columns into rows. 
df_archives= pd.read_csv('archives.txt', sep=',').transpose()

df_archives 

archives_url_pull

# Modify the original url string to be in accordance with the dataframe elements. This is the first step to stripping off the url and retaining only the YYYY/MM for the player. 
archives_url_mod= archives_url_pull.replace('archives', '')
archives_url_mod


df_archives.info()
# Per above, the data was read in as an index in an empty dataframe. 
df_archives.index

# Below resets the index and retains the original indices. 
df_archives.reset_index(drop=False, inplace=True)
df_archives.info()

# Remove the url part of the strings and retain only YYYY/MM. 
df_archives['index']= df_archives['index'].apply(lambda x: x.replace(archives_url_mod, ''))

df_archives

# Create a list of the archive links. 
year_month_list= df_archives['index'].values.tolist()

year_month_list

for i in year_month_list: 
    print('https://api.chess.com/pub/player/' + player_name + '/games/' + i + '/pgn', i)


# Make a new directory for the player's games. 
os.makedirs("./game_lib", exist_ok=True)

# 
for i in year_month_list: 
    # iterate through the YYYY/MM game databases on chess.com
    game_year_month= requests.get('https://api.chess.com/pub/player/' + player_name + '/games/' + i + '/pgn')

    # below replaces the backslash, which will be interpreted as part of the pather otherwise, with an underscore. 
    games_string= i.replace('/', '_') + '.txt'    
    # define the path to the newly created game folder. 
    pather= './game_lib' 
    print(pather, games_string)
    # create the full path to use below. 
    save_to= os.path.join(pather, games_string)
    # write out the files to the game_lib path. 
    with open(save_to, "w") as f:
        f.write(game_year_month.text)

##############################
# Single example. 

game_year_month= requests.get('https://api.chess.com/pub/player/raekwan/games/2022/05/pgn')

with open("games.txt", "w") as f:
    f.write(game_year_month.text)

df= pd.read_csv('games.txt')

df.head(30)

df.tail(30)