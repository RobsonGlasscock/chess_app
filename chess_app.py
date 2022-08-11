%reset -f
import os
import pandas as pd
import requests 

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

# Define the player's name.
pn= 'RichardShtivelband' 
# The chess.com player name in the url path is lowercase. Convert to lower here. 
player_name= pn.lower()

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

os.chdir("./game_lib")

for file in os.listdir():
    print(file)


for i, j in enumerate(os.listdir()):
    if i==0:
        games= pd.read_csv(j, names=['data'])
        games.reset_index(drop=True, inplace=True)
        # remove header ????? 
    else: 
        games_temp= pd.read_csv(j, names= ['data'])
        # remove header ?????
        games= pd.concat([games, games_temp])
        games.reset_index(drop=True, inplace=True) 
        del games_temp

games.shape
games.info()


games.head(25)
games.tail()

# Scafolding to identify patterns 
'''
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 2].lower()
    ):
        print(i, games["data"][i], games["data"][i + 2], games["data"][i + 11], games['data'][i+13])

for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 3].lower()
    ):
        print(i, games["data"][i], games["data"][i + 3], games["data"][i + 12], games['data'][i+13])
'''

# Create an empty dataframe
df = pd.DataFrame(
    data=[],
    columns=["date", "player", "rating", "time_control"],
    index=[i for i in range(0, len(games) - 1)],
)

df.head()


# Populate the dataframe with the games data for white games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 2].lower()
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 2]
        df["rating"].iloc[i] = games["data"][i + 11]
        df["time_control"].iloc[i]= games['data'][i+13]

# Populate the datafrme with the games data for black games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 3].lower()
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 3]
        df["rating"].iloc[i] = games["data"][i + 12]
        df["time_control"].iloc[i]= games['data'][i+13]


df.dropna(how="all", inplace=True)

df.head()


# drop the non-elo obs. 

df['dropper']= 'Elo' in df['rating']
'Elo' in df['rating'].iloc[0]

df['dropper']= df['rating'].apply(lambda x: 'Elo' not in x)

df.head()

df['dropper'].value_counts()

df.drop(df[df['dropper']==1].index, inplace=True)

df['dropper'].value_counts()
df.drop(columns=['dropper'], inplace=True)

df.head()

df.shape

# Figure out what these time controls are... 
df['time_control'].value_counts()

'''
Time control definitions: http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm#c9.6

The third Time control field kind is formed as two positive integers separated by a solidus ("/") character. The first integer is the number of moves in the period and the second is the number of seconds in the period. Thus, a time control period of 40 moves in 2 1/2 hours would be represented as "40/9000".

.
.
.

"The fifth TimeControl field kind is used for an "incremental" control period. It should only be used for the last descriptor in a TimeControl tag value and is usually the only descriptor in the value. The format consists of two positive integers separated by a plus sign ("+") character. The first integer gives the minimum number of seconds allocated for the period and the second integer gives the number of extra seconds added after each move is made. So, an incremental time control of 90 minutes plus one extra minute per move would be given by "4500+60" in the TimeControl tag value."
'''

# 

900/60
300/60
660/60
900/60
# below is for one move per day. 
86400/60
1440/60

# Overwrite the data variable with just the data component
df["date"] = df["date"].apply(lambda x: x[-12:-2])
# Overwrite the player variabele to just contain the name.
df["player"] = df["player"].apply(lambda x: x[8:-2])

df.head()

# Retain the numeric portion of the rating.
df["rating"] = df["rating"].apply(lambda x: x[-6:-2])

# Ratings under < 1,000 have a leading "
# Define a function to remove the leading "
def stripper(x):
    if x[0] == '"':
        return x[1:]
    else:
        return x


# Apply the function to the dataframe to deal with the sub 1,000 ratings.
df["rating"] = df["rating"].apply(stripper)

df["rating"] = df["rating"].astype(int)

df.head()
df.tail()

# Remove the unnecessary components of the string. 
df['time_control']= df['time_control'].apply(lambda x: x.replace('TimeControl', ''))
df['time_control']= df['time_control'].apply(lambda x: x.replace('"', ''))
df['time_control']= df['time_control'].apply(lambda x: x.replace('[', ''))
df['time_control']= df['time_control'].apply(lambda x: x.replace(']', ''))

# Create a year variable.
df["year"] = df["date"].apply(lambda x: x[:4])

df.head()

df["year"].value_counts()

# Create an annual count variable for each year-time_control. 
df['ann_count']= df.groupby(['year', 'time_control'])['rating'].transform('count')

df.head(30)

# sort the dataframe
df.sort_values(by=['year', 'time_control'], inplace=True)

df.head()
df.tail()

df.reset_index(drop=True, inplace=True)


df['ann_count'].value_counts()

# Judgement call to remove any time control with less than 12 games per year. 

df.drop(df[df['ann_count']<12].index, inplace=True)
df.shape

df['time_control'].value_counts()

df.groupby(['year', 'time_control'])['rating'].describe()

df_export= df.groupby(['year', 'time_control'])['rating'].describe().round()
df_export.head()
df_export.info()
df_export= df_export.astype(int)
df_export.to_excel('richard.xlsx')

##############################
# Single example. 

game_year_month= requests.get('https://api.chess.com/pub/player/raekwan/games/2022/05/pgn')

with open("games.txt", "w") as f:
    f.write(game_year_month.text)

df= pd.read_csv('games.txt')

df.head(30)

df.tail(30)