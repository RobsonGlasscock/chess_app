%reset -f
import matplotlib.pyplot as plt
import os
import pandas as pd
import requests
import time

start = time.time()

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# Define the player's name.
pn = "RichardShtivelband"
# The chess.com player name in the url path is lowercase. Convert to lower here.
player_name = pn.lower()

# Use the player name within the url string.
archives_url_pull = (
    "https://api.chess.com/pub/player/" + player_name + "/games/archives"
)

archives_url_pull

# Pull the archives data which will show which YYYY/MM the player had games
archives = requests.get(archives_url_pull)

archives.text

type(archives.text)

type(archives)

# strip off the dictionary structure-like components of the string and other components that aren't necessary.
stripper_list = ['{"archives":', "}", "]", "["]
for i, j in enumerate(stripper_list):
    if (i == 0) and type(archives == "requests.models.Response"):
        archives = archives.text.replace(j, "")
    else:
        archives = archives.replace(j, "")


archives

# write out to a file.
with open("archives.txt", "w") as f:
    f.write(archives)

# import the data and transpose the columns into rows.
df_archives = pd.read_csv("archives.txt", sep=",").transpose()

df_archives

archives_url_pull

# Modify the original url string to be in accordance with the dataframe elements. This is the first step to stripping off the url and retaining only the YYYY/MM for the player.
archives_url_mod = archives_url_pull.replace("archives", "")
archives_url_mod


df_archives.info()
# Per above, the data was read in as an index in an empty dataframe.
df_archives.index

# Below resets the index and retains the original indices.
df_archives.reset_index(drop=False, inplace=True)
df_archives.info()

# Remove the url part of the strings and retain only YYYY/MM.
df_archives["index"] = df_archives["index"].apply(
    lambda x: x.replace(archives_url_mod, "")
)

df_archives

# Create a list of the archive links.
year_month_list = df_archives["index"].values.tolist()

year_month_list

for i in year_month_list:
    print(
        "https://api.chess.com/pub/player/"
        + player_name
        + "/games/"
        + i
        + "/pgn",
        i,
    )


# Make a new directory for the player's games.
os.makedirs("./game_lib", exist_ok=True)


for i in year_month_list:
    # iterate through the YYYY/MM game databases on chess.com
    game_year_month = requests.get(
        "https://api.chess.com/pub/player/"
        + player_name
        + "/games/"
        + i
        + "/pgn"
    )

    # below replaces the backslash, which will be interpreted as part of the pather otherwise, with an underscore.
    games_string = i.replace("/", "_") + ".txt"
    # define the path to the newly created game folder.
    pather = "./game_lib"
    print(pather, games_string)
    # create the full path to use below.
    save_to = os.path.join(pather, games_string)
    # write out the files to the game_lib path.
    with open(save_to, "w") as f:
        f.write(game_year_month.text)

os.chdir("./game_lib")

for file in os.listdir():
    print(file)


for i, j in enumerate(os.listdir()):
    if i == 0:
        games = pd.read_csv(j, names=["data"])
        games.reset_index(drop=True, inplace=True)
        # remove header ?????
    else:
        games_temp = pd.read_csv(j, names=["data"])
        # remove header ?????
        games = pd.concat([games, games_temp])
        games.reset_index(drop=True, inplace=True)
        del games_temp

games.shape
games.info()


games.head(25)
games.tail()

# Scaffolding to retain only the rows that matter. Keeping this subset,
# instead of iterating through every row which contains lots of rows
# I don't care about, is being done to save processing time. RichardShtivelband's
# games too a long time to iterate through since he had so many so I am
# trying to consider the speed of the web app in the future here.
"""
games[
    (games["data"].str.contains("[Date", regex=False))
    | (games["data"].str.contains("[White", regex=False))
    | (games["data"].str.contains("[Black", regex=False))
    | (games["data"].str.contains("[TimeControl", regex=False))
].head(20)

"""
# Scafolding to identify patterns
"""
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
"""

# Create an empty dataframe
df = pd.DataFrame(
    data=[],
    columns=["date", "player", "rating", "time_control", "eco", "eco_desc", "result", "color"],
    index=[i for i in range(0, len(games) - 1)],
)

df.head()


# Retain only the useful rows, which contain date, white name, black name,
# white elo, black elo, and timecontrol.
games = games[
    (games["data"].str.contains("[Date", regex=False))
    | (games["data"].str.contains("[White", regex=False))
    | (games["data"].str.contains("[Black", regex=False))
    | (games["data"].str.contains("[TimeControl", regex=False))
    | (games["data"].str.contains("[ECO ", regex=False))
    | (games["data"].str.contains("[ECOUrl", regex=False))
    | (games["data"].str.contains("[Result", regex=False))
]

games.reset_index(drop=True, inplace=True)
games.head(20)

# Populate the dataframe with the games data for white games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 1].lower()
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 1]
        df["rating"].iloc[i] = games["data"][i + 6]
        df["time_control"].iloc[i] = games["data"][i + 8]
        df["eco"].iloc[i] = games["data"][i + 4]
        df["eco_desc"].iloc[i] = games["data"][i + 5]
        df["result"].iloc[i] = games["data"][i + 3]
        df["color"].iloc[i]= "white"

# Populate the datafrme with the games data for black games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 2].lower()
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 2]
        df["rating"].iloc[i] = games["data"][i + 7]
        df["time_control"].iloc[i] = games["data"][i + 8]
        df["eco"].iloc[i] = games["data"][i + 4]
        df["eco_desc"].iloc[i] = games["data"][i + 5]
        df["result"].iloc[i] = games["data"][i + 3]
        df["color"].iloc[i]= "black"
        
df.head(20)

"""
# Populate the dataframe with the games data for white games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 2].lower()
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 2]
        df["rating"].iloc[i] = games["data"][i + 11]
        df["time_control"].iloc[i] = games["data"][i + 13]

# Populate the datafrme with the games data for black games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        player_name in games["data"][i + 3].lower()
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 3]
        df["rating"].iloc[i] = games["data"][i + 12]
        df["time_control"].iloc[i] = games["data"][i + 13]
"""

df.dropna(how="all", inplace=True)

# drop the non-elo obs.

df["dropper"] = "Elo" in df["rating"]
"Elo" in df["rating"].iloc[0]

df["dropper"] = df["rating"].apply(lambda x: "Elo" not in x)

df.head()

df["dropper"].value_counts()

df.drop(df[df["dropper"] == 1].index, inplace=True)

df["dropper"].value_counts()
df.drop(columns=["dropper"], inplace=True)

df.head()

df.shape

# Figure out what these time controls are...
df["time_control"].value_counts()

"""
Time control definitions: http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm#c9.6

The third Time control field kind is formed as two positive integers separated by a solidus ("/") character. The first integer is the number of moves in the period and the second is the number of seconds in the period. Thus, a time control period of 40 moves in 2 1/2 hours would be represented as "40/9000".

.
.
.

"The fifth TimeControl field kind is used for an "incremental" control period. It should only be used for the last descriptor in a TimeControl tag value and is usually the only descriptor in the value. The format consists of two positive integers separated by a plus sign ("+") character. The first integer gives the minimum number of seconds allocated for the period and the second integer gives the number of extra seconds added after each move is made. So, an incremental time control of 90 minutes plus one extra minute per move would be given by "4500+60" in the TimeControl tag value."
"""

#

900 / 60
300 / 60
660 / 60
900 / 60
# below is for one move per day.
86400 / 60
(86400 / 60) / 60

# From RichardShtivelband, looks like he has a game with one more per three days
((259200 / 60) / 60) / 24
((1209600 / 60) / 60) / 24
((172800 / 60) / 60) / 24


# create win/loss for white/black 
# clean out the url portion of the ECO description. 

df.head(10)
df.info()

# Create separate df's from white games and black games where draws are excluded. 
# Use these to create the dummy variables. As shown below, Richard's white_win
# dummy for 2022, D02 shows 0.09 for 84 games, but this 
# is misleading because he was white in 16 of these games and black in 68 of them.
# My win and loss dummies don't actually work for the combined dataframe. One way
# # I wanted to get around this was to create a cumulative count variable that
# increments white wins +1 and decrements for white losses. This would show the 
# "spread" of wins over losses or losses over wins.  

df_white= df[df['color']=='white'].copy(deep=True)
df_black= df[df["color"]=='black'].copy(deep=True)

assert df_white.shape[0] + df_black.shape[0]== df.shape[0]

# Create functions for the following variables: white wins, white losses, black wins,
# black losses, white draws, black draws.                                                                                                                                                                    
def white_wins(df):
    if ('White' in df['player']) and ("1-0" in df['result']):
        return 1 
    else: 
        return 0        

def black_wins(df):
    if ('Black' in df['player']) and ("0-1" in df['result']):
        return 1 
    else: 
        return 0 

def white_losses(df):
    if ('White' in df['player']) and ("0-1" in df['result']):
        return 1 
    else: 
        return 0 

def black_losses(df):
    if ('Black' in df['player']) and ("1-0" in df['result']):
        return 1 
    else: 
        return 0 

def white_draws(df):
    if ('White' in df['player']) and ("1/2-1/2" in df['result']):
        return 1 
    else: 
        return 0 

def black_draws(df):
    if ('Black' in df['player']) and ("1/2-1/2" in df['result']):
        return 1 
    else: 
        return 0 

# Create cumulative counts where wins =+1 and losses =-1

def white_cumul(df):
    if ('White' in df['player']) and ("1-0" in df['result']):
        return 1
    if ('White' in df['player']) and ("0-1" in df['result']):
        return -1 
    else:
        return 0

def black_cumul(df):
    if ('Black' in df['player']) and ("0-1" in df['result']):
        return 1 
    if ('Black' in df['player']) and ("1-0" in df['result']):
        return -1 
    else: return 0

# Create vars for combined df. 
df['white_wins']= df.apply(white_wins, axis=1)
df['black_wins']= df.apply(black_wins, axis=1)
df['white_losses']= df.apply(white_losses, axis=1)
df['black_losses']= df.apply(black_losses, axis=1)
df['white_draws']= df.apply(white_draws, axis=1)
df['black_draws']= df.apply(black_draws, axis=1)

df['white_cumul']= df.apply(white_cumul, axis=1)
df['black_cumul']= df.apply(black_cumul, axis=1)

# Create vars for df's of white and black games only. I think draws should also be included in these datasets and will have 0's for the wins dummies. 

df_white['white_wins']= df_white.apply(white_wins, axis=1)
df_black['black_wins']= df_black.apply(black_wins, axis=1)
df_white['white_losses']= df_white.apply(white_losses, axis=1)
df_black['black_losses']= df_black.apply(black_losses, axis=1)
df_white['white_draws']= df_white.apply(white_draws, axis=1)
df_black['black_draws']= df_black.apply(black_draws, axis=1)

df_white['white_cumul']= df_white.apply(white_cumul, axis=1)
df_black['black_cumul']= df_black.apply(black_cumul, axis=1)


df.head()

df[['player', 'rating', 'result', 'white_wins', 'black_wins', 'white_losses', 'black_losses', 'white_draws', 'black_draws']].head()


df[['player', 'rating', 'result', 'white_wins', 'black_wins', 'white_losses', 'black_losses', 'white_draws', 'black_draws']].tail(25)

df[['player', 'rating', 'result', 'white_wins', 'black_wins', 'white_losses', 'black_losses', 'white_draws', 'black_draws']]

df[df['result'].str.contains('1/2')].head()

# Accuracy checks 
df[df['result'].str.contains('1/2')][['player', 'rating', 'result', 'white_wins', 'black_wins', 'white_losses', 'black_losses', 'white_draws', 'black_draws']].head()

df[df['result'].str.contains('0-1')][['player', 'rating', 'result', 'white_wins', 'black_wins', 'white_losses', 'black_losses', 'white_draws', 'black_draws']].head(20)

df[df['result'].str.contains('1-0')][['player', 'rating', 'result', 'white_wins', 'black_wins', 'white_losses', 'black_losses', 'white_draws', 'black_draws']].head(20)
 
 # No exceptions noted. 

# Overwrite the data variable with just the data component
df["date"] = df["date"].apply(lambda x: x[-12:-2])
df_white['date']= df_white['date'].apply(lambda x: x[-12:-2])
df_black['date']= df_black['date'].apply(lambda x: x[-12:-2])

# Overwrite the player variabele to just contain the name.
df["player"] = df["player"].apply(lambda x: x[8:-2])
df_white["player"] = df_white["player"].apply(lambda x: x[8:-2])
df_black["player"] = df_black["player"].apply(lambda x: x[8:-2])

df.head()

# Retain the numeric portion of the rating.
df["rating"] = df["rating"].apply(lambda x: x[-6:-2])
df_white["rating"] = df_white["rating"].apply(lambda x: x[-6:-2])
df_black["rating"] = df_black["rating"].apply(lambda x: x[-6:-2])

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

# for the white df
df_white["rating"] = df_white["rating"].apply(stripper)
df_white["rating"] = df_white["rating"].astype(int)

# for the black df 
df_black["rating"] = df_black["rating"].apply(stripper)
df_black["rating"] = df_black["rating"].astype(int)

# Remove the unnecessary components of the string.

df["time_control"] = df["time_control"].apply(
    lambda x: x.replace("TimeControl", "")
)
df["time_control"] = df["time_control"].apply(lambda x: x.replace('"', ""))
df["time_control"] = df["time_control"].apply(lambda x: x.replace("[", ""))
df["time_control"] = df["time_control"].apply(lambda x: x.replace("]", ""))

# for the white df 
df_white["time_control"] = df_white["time_control"].apply(
    lambda x: x.replace("TimeControl", "")
)
df_white["time_control"] = df_white["time_control"].apply(lambda x: x.replace('"', ""))
df_white["time_control"] = df_white["time_control"].apply(lambda x: x.replace("[", ""))
df_white["time_control"] = df_white["time_control"].apply(lambda x: x.replace("]", ""))

# For the black df 
df_black["time_control"] = df_black["time_control"].apply(
    lambda x: x.replace("TimeControl", "")
)
df_black["time_control"] = df_black["time_control"].apply(lambda x: x.replace('"', ""))
df_black["time_control"] = df_black["time_control"].apply(lambda x: x.replace("[", ""))
df_black["time_control"] = df_black["time_control"].apply(lambda x: x.replace("]", ""))

# Remove the unnecessary components of the string.
df["eco"] = df["eco"].apply(
    lambda x: x.replace("[ECO", "")
)

df["eco"] = df["eco"].apply(lambda x: x.replace('"', ""))
df["eco"] = df["eco"].apply(lambda x: x.replace(']', ""))
df["eco"] = df["eco"].apply(lambda x: x.strip())

# for the white df 
df_white["eco"] = df_white["eco"].apply(
    lambda x: x.replace("[ECO", "")
)

df_white["eco"] = df_white["eco"].apply(lambda x: x.replace('"', ""))
df_white["eco"] = df_white["eco"].apply(lambda x: x.replace(']', ""))
df_white["eco"] = df_white["eco"].apply(lambda x: x.strip())

# for the black df 
df_black["eco"] = df_black["eco"].apply(
    lambda x: x.replace("[ECO", "")
)

df_black["eco"] = df_black["eco"].apply(lambda x: x.replace('"', ""))
df_black["eco"] = df_black["eco"].apply(lambda x: x.replace(']', ""))
df_black["eco"] = df_black["eco"].apply(lambda x: x.strip())


df["eco_desc"] = df["eco_desc"].apply(
    lambda x: x.strip()
)

df["eco_desc"] = df["eco_desc"].apply(
    lambda x: x.replace('[ECOUrl "https://www.chess.com/openings/', "")
)

df["eco_desc"] = df["eco_desc"].apply(
    lambda x: x.replace('"', "")
)

df["eco_desc"] = df["eco_desc"].apply(
    lambda x: x.replace(']', "")
)

# For the white df 
df_white["eco_desc"] = df_white["eco_desc"].apply(
    lambda x: x.strip()
)

df_white["eco_desc"] = df_white["eco_desc"].apply(
    lambda x: x.replace('[ECOUrl "https://www.chess.com/openings/', "")
)

df_white["eco_desc"] = df_white["eco_desc"].apply(
    lambda x: x.replace('"', "")
)

df_white["eco_desc"] = df_white["eco_desc"].apply(
    lambda x: x.replace(']', "")
)

# for the black df 

df_black["eco_desc"] = df_black["eco_desc"].apply(
    lambda x: x.strip()
)

df_black["eco_desc"] = df_black["eco_desc"].apply(
    lambda x: x.replace('[ECOUrl "https://www.chess.com/openings/', "")
)

df_black["eco_desc"] = df_black["eco_desc"].apply(
    lambda x: x.replace('"', "")
)

df_black["eco_desc"] = df_black["eco_desc"].apply(
    lambda x: x.replace(']', "")
)


# Create a year variable.
df["year"] = df["date"].apply(lambda x: x[:4])
df_white["year"] = df_white["date"].apply(lambda x: x[:4])
df_black["year"] = df_black["date"].apply(lambda x: x[:4])


# Create an annual count variable for each year-time_control.
df["ann_count"] = df.groupby(["year", "time_control"])["rating"].transform(
    len
)

# for white df 
df_white["ann_count"] = df_white.groupby(["year", "time_control"])["rating"].transform(
    len
)

# for black df 
df_black["ann_count"] = df_black.groupby(["year", "time_control"])["rating"].transform(
    len
)

# sort the dataframe
df.sort_values(by=["year", "time_control"], inplace=True)

df.reset_index(drop=True, inplace=True)


df["ann_count"].value_counts()

'''
# Judgement call to remove any time control with less than 12 games per year.
df.drop(df[df["ann_count"] < 12].index, inplace=True)

'''

def time_convert(col):
    if col.strip() == "180":
        return "3 minutes"
    if col.strip() == "60":
        return "1 minute"
    if col.strip() == "600":
        return "10 minutes"
    if col.strip() == "900+10":
        return "15 minutes + 10"
    if col.strip() == "300":
        return "5 minutes"
    if col.strip() == "300+5":
        return "5 minutes + 5"
    if col.strip() == "180+2":
        return "3 minutes + 2"
    if col.strip() == "900":
        return "15 minutes"
    if col.strip() == "300+2":
        return "5 minutes + 2"
    if col.strip() == "1800":
        return "30 minutes"
    if col.strip() == "2700+45":
        return "45 minutes + 45"
    if col.strip() == "2700":
        return "45 minutes"
    if col.strip() == "1/86400":
        return "1 day"
    if col.strip() == "1/259200":
        return "3 days"
    if col.strip() == "1/1209600":
        return "14 days"
    if col.strip() == "1/172800":
        return "2 days"
    if col.strip() == "120+1":
        return "2 minutes + 1"
    if col.strip() == "120":
        return "2 minutes"
    if col.strip() == "180+1":
        return "3 minutes + 1"

    else:
        return col


df["time_control"] = df["time_control"].apply(time_convert)

# for the white df 
df_white["time_control"] = df_white["time_control"].apply(time_convert)

# for the black df
df_black["time_control"] = df_black["time_control"].apply(time_convert)



# rg: box and whiskser plot off the df dataframe?????

df.groupby(["year", "time_control"])["rating"].describe()


# Create cumulative sums for white and black by eco. This uses the +1 for wins and -1 for losses. 
df['white_cumul_sum']= df.groupby(["year", "time_control", "eco"])['white_cumul'].transform('sum')

df['black_cumul_sum']= df.groupby(["year", "time_control", "eco"])['black_cumul'].transform('sum')

# for white df 
df_white['white_cumul_sum']= df_white.groupby(["year", "time_control", "eco"])['white_cumul'].transform('sum')

# for the black df 
df_black['black_cumul_sum']= df_black.groupby(["year", "time_control", "eco"])['black_cumul'].transform('sum')



df['white_cumul_sum'].describe()
df['black_cumul_sum'].describe()

df_white.head()
df_black.head()


df_white[df_white['year']=="2022"].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False)

# Per manual inspection, for 2022, 3 minutes, RichardShtivelband's highest win over # loss spread was for: 
# B01 (11 and 38 games), 
# B00 (11 and 28 games), 
# C10 (10 and 16 games)
# B06 (9 and 41 games), 
# B07 (9 and 34 games). 

# Contrast this to the results below from sorting on white_wins

df_white[df_white['year']=="2022"].groupby(["year", "time_control", 'eco'])["white_wins"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False)

# Per manual inspection, for 2022, 3 minute games for RichardShtivelband:
# A43 (1.0, and 6 games)
# C05 (1.0 and 5 games)
# C64 (1.0 and 5 games)
# A49 (1.0 and 3 games)
# B20 (1.0 and 3 games)
# These are openings he didn't play very much of but had very high win rates. I don't
# think these results are as intersting as the white_cumul_sum results. 

# For RichardShtiveland's worst white openings for 2022, 3 minutes: 
df_white[df_white['year']=="2022"].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=True)

# B50 (-6 and 14 games)
# B76 (-5 and 11 games)
# E61 (-3 and 4 games)
# C40 (-3 and 5 games)
# C45 (-3 and 5 games)

# For RichardShtiveland's best black openings for 2022, 3 minutes: 
df_black[df_black['year']=="2022"].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False)

# C55 (9 and 20 games)
# A00 (8 and 30 games)
# C42 (6 and 7 games)
# E12 (6 and 6 games)
# E20 (5 and 20 games)

# For RichardShtivelband's worst black openings for 2022, 3 minutes:
df_black[df_black['year']=="2022"].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=True)

# D11 (-9 and 26 games)
# D10 (-8 and 33 games)
# B44 (-6 and 13 games)
# A07 (-6 and 20 games)
# B22 (-6 and 22 games)

# Create the weighting Richard recommended:
# (0.5 x (white_cumul_sum / white_cumul_max) ) + (0.5 x (white_wins / white_wins_max) )

# What the above does, conceptually, is gives equal weights of 50% to the cumulative wins over losses and percentage of games won in the opening, then divides by the maximum of each of these variables to figure out a percentage that is then multiplied by the 50% weight to allocate X percent of of the 50% weight to the opening. Note that any opening with the maximum cumulative wins over losses or a 1.0 accuracy will mathematically be 0.5 x 1 and will allocate all 50% of the weight to that particular opening. Openings that are not the max wins over losses or that do not have the maximum win rate, which is probably 100%, will allocate less than that 50% of the weight to that opening. 

# For the white dataframe

# The cumulative wins over losses is over the year-time_control but not also grouped by eco.
df_white['white_cumul_max']= df_white.groupby(['year', 'time_control'])['white_cumul_sum'].transform('max')

# the sum of white wins and the length are with respect to the eco, as well. So the grouping is year, time_control, and eco. 
df_white['white_wins_sum']= df_white.groupby(['year', 'time_control', 'eco'])['white_wins'].transform('sum')

df_white['white_len']= df_white.groupby(['year', 'time_control', 'eco'])['white_wins'].transform(len)

df_white['white_wins_mean']= df_white['white_wins_sum'] / df_white['white_len']

df_white['white_wins_mean_max']= df_white.groupby(['year', 'time_control'])['white_wins_mean'].transform('max')

# For the black dataframe

# The cumulative wins over losses is over the year-time_control but not also grouped by eco.
df_black['black_cumul_max']= df_black.groupby(['year', 'time_control'])['black_cumul_sum'].transform('max')

# the sum of black wins and the length are with respect to the eco, as well. So the grouping is year, time_control, and eco. 
df_black['black_wins_sum']= df_black.groupby(['year', 'time_control', 'eco'])['black_wins'].transform('sum')

df_black['black_len']= df_black.groupby(['year', 'time_control', 'eco'])['black_wins'].transform(len)

df_black['black_wins_mean']= df_black['black_wins_sum'] / df_black['black_len']

df_black['black_wins_mean_max']= df_black.groupby(['year', 'time_control'])['black_wins_mean'].transform('max')

# Accuracy check for 2022, 3 minutes, D02. 
df_white[(df_white['year']=="2022") & (df_white['eco']=="D02") & (df_white['time_control']=="3 minutes")].to_excel('d02_white_check.xlsx')


df_black[(df_black['year']=="2022") & (df_black['eco']=="D02") & (df_black['time_control']=="3 minutes")].to_excel('d02_black_check.xlsx')


df_black[(df_black['year']=="2022") & (df_black['eco']=="D02") & (df_black['time_control']=="3 minutes")].shape

 
df_white[(df_white['year']=="2022") & (df_white['eco']=="D02") & (df_white['time_control']=="3 minutes")].shape

# No exceptions noted. 


df_white.head()

# Create weighting vars

df_white['weighted_calc']= (0.5 * (df_white['white_cumul_sum']/ df_white['white_cumul_max'] ) + (0.5 * (df_white['white_wins_mean']/ df_white['white_wins_mean_max'])))


df_white.head()

# Sort results on weighted 
df_white[df_white['year']=='2022'].groupby(['year', 'time_control', 'eco'])['weighted_calc'].describe().sort_values(by=['year', 'time_control', 'mean'], ascending=False)


# Sort results on cumluative wins over losses
df_white[df_white['year']=="2022"].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False)


# Here is a breakdown of the ECO's that are white's best openigns:
# B01 - on both sorts
# B00 - on both sorts 
# C10 - on both sorts 
# B06- on cumulative wins over losses but not on weighted
# B07 - on cumulative wins over losses but not on weighted 
# A43 - on weighted but not on cumulative wins over losses
# E70 - on weighted but not on cumulative wins over losses 


# per below white_wins_mean should be equal to white_wins mean. 
df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B01')]['white_wins_mean'].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B01')]['white_wins'].describe()


# Look at each ECO listed above for win rates 
df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B00')]['white_wins'].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='C10')]['white_wins'].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B06')]['white_wins'].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B07')]['white_wins'].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='A43')]['white_wins'].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='E70')]['white_wins'].describe()


# Get the maximum cumulative wins over losses andq win rates for each opening

df_white.head()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B01')][['white_cumul_max', 'white_wins_mean_max']].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B00')][['white_cumul_max', 'white_wins_mean_max']].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='C10')][['white_cumul_max', 'white_wins_mean_max']].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B06')][['white_cumul_max', 'white_wins_mean_max']].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='B07')][['white_cumul_max', 'white_wins_mean_max']].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='A43')][['white_cumul_max', 'white_wins_mean_max']].describe()

df_white[(df_white['year']=='2022') & (df_white['time_control']== '3 minutes') & (df_white['eco']=='E70')][['white_cumul_max', 'white_wins_mean_max']].describe()


# Note that the above all have the same values, which makes sense. These are 11 for the cumulative wins over losses maximum and white_wins_mean_max. These are at the year- time_control level so these should be the same. p/f/r. 

# No exceptions noted. 

df[(df['year']=="2022") & (df['eco']=="D02") & (df['time_control']=="3 minutes")]['white_wins'].describe()

df[(df['year']=="2022") & (df['eco']=="D02") & (df['time_control']=="3 minutes")]['color'].value_counts()

# Richard had a 0.096 win rate with the white_win dummy for the entire dataframe because the 67 games he played as black all had 0's! This is wrong. He actually had a 50% win rate for this 16 white games. So half of 16 is 8 and 8/ (16 + 67) = 0.096 but this is totally wrong and shows why the dataframes need to be split into white and black dataframes before win dummies can be assigned! 


# Get top five best and worst openings for each color. 

# Use 2022, 3 minutes as an example
df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False)

# Examine the multi-index 
df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index

# Select the top 5 of the multi-index
df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index[:5]

# Select only the ECO portion of the multi-index for the top five. 
df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index[:5].get_level_values(2)

df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[-5:]


df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index[-5:]


# Compare to the previous results. 
# For RichardShtiveland's worst white openings for 2022, 3 minutes: 
df_white[df_white['year']=="2022"].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=True)

# B50 (-6 and 14 games)
# B76 (-5 and 11 games)
# E61 (-3 and 4 games)
# C40 (-3 and 5 games)
# C45 (-3 and 5 games)


# Get the count of the selected obs for the five worst white openings. 
df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[-5:]['count']

# Get the mean for the selected obs for the five worst white openings. 
df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[-5:]['mean']


###############
# Best white openings  
#########

# Initialize three empty lists
eco = []
no_games= []
cumul_win_loss= []

# Append the eco's for the five best white openings to the eco list. 
for i in df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index[:5].get_level_values(2):
    eco.append(i)

# Append the number of games for the five best white openings to the no_games list. 
for i in df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[:5]['count']:
    no_games.append(i)

# Append the cumulative wins over losses for the five best white openings to the cumul_win_loss list. 
for i in df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[:5]['mean']:
    cumul_win_loss.append(i)

best_white_df= pd.DataFrame(data= {'eco': eco, 'no. games': no_games, 'wins over losses': cumul_win_loss})

del eco, no_games, cumul_win_loss

###############
# Worst white openings 
#########

# Initialize three empty lists
eco = []
no_games= []
cumul_win_loss= []

# Append the eco's for the five worst white openings to the eco list. 
for i in df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index[-5:].get_level_values(2):
    eco.append(i)

# Append the number of games for the five worst white openings to the no_games list. 
for i in df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[-5:]['count']:
    no_games.append(i)

# Append the cumulative wins over losses for the five worst white openings to the cumul_win_loss list. 
for i in df_white[(df_white['year']=="2022") & (df_white["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["white_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[-5:]['mean']:
    cumul_win_loss.append(i)

worst_white_df= pd.DataFrame(data= {'eco': eco, 'no. games': no_games, 'wins over losses': cumul_win_loss})

worst_white_df

del eco, no_games, cumul_win_loss

###############
# Best black openings 
#########

# Initialize three empty lists
eco = []
no_games= []
cumul_win_loss= []

# Append the eco's for the five best black openings to the eco list. 
for i in df_black[(df_black['year']=="2022") & (df_black["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index[:5].get_level_values(2):
    eco.append(i)

# Append the number of games for the five best black openings to the no_games list. 
for i in df_black[(df_black['year']=="2022") & (df_black["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[:5]['count']:
    no_games.append(i)

# Append the cumulative wins over losses for the five best black openings to the cumul_win_loss list. 
for i in df_black[(df_black['year']=="2022") & (df_black["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[:5]['mean']:
    cumul_win_loss.append(i)

best_black_df= pd.DataFrame(data= {'eco': eco, 'no. games': no_games, 'wins over losses': cumul_win_loss})


best_black_df

del eco, no_games, cumul_win_loss
###############
# Worst black openings 
#########

# Initialize three empty lists
eco = []
no_games= []
cumul_win_loss= []

# Append the eco's for the five worst black openings to the eco list. 
for i in df_black[(df_black['year']=="2022") & (df_black["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).index[-5:].get_level_values(2):
    eco.append(i)

# Append the number of games for the five worst black openings to the no_games list. 
for i in df_black[(df_black['year']=="2022") & (df_black["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[-5:]['count']:
    no_games.append(i)

# Append the cumulative wins over losses for the five worst black openings to the cumul_win_loss list. 
for i in df_black[(df_black['year']=="2022") & (df_black["time_control"]=="3 minutes")].groupby(["year", "time_control", 'eco'])["black_cumul_sum"].describe().sort_values(by=['year', 'time_control', 'mean', "count"], ascending=False).iloc[-5:]['mean']:
    cumul_win_loss.append(i)

worst_black_df= pd.DataFrame(data= {'eco': eco, 'no. games': no_games, 'wins over losses': cumul_win_loss})


worst_black_df
del eco, no_games, cumul_win_loss





#######################

df_export = df.groupby(["year", "time_control"])["rating"].describe().round()
df_export
df_export.info()
df_export = df_export.astype(int)

end = time.time()
total_time = end - start

total_time
print("execution time", str(total_time))

# Refer to a multiindex
df_export.index
df_export.index.get_level_values(0)
df_export.index.get_level_values(1)

# Per above, the index repeats if he played the same time controls in different years. Use .unique to handle this.

df_export["mean"].loc[[("2018", "1 minute"), ("2020", "1 minute")]]

df_export[df_export.index.get_level_values(1) == "3 minutes"]

for i in df_export.index.get_level_values(1).unique():
    print(i)
    print(df_export["mean"][df_export.index.get_level_values(1) == i])


df_export["mean"][df_export.index.get_level_values(1) == "3 minutes"]

df_export["mean"][df_export.index.get_level_values(1) == "3 minutes"].loc[
    "2018", "3 minutes"
]


df_export["mean"][df_export.index.get_level_values(1) == "3 minutes"].values

df_export["mean"][
    df_export.index.get_level_values(1) == "3 minutes"
].index.get_level_values(0)

plt.scatter(
    df_export["mean"][
        df_export.index.get_level_values(1) == "3 minutes"
    ].index.get_level_values(0),
    df_export["mean"][
        df_export.index.get_level_values(1) == "3 minutes"
    ].values,
)


# Loop for graphs
for i in df_export.index.get_level_values(1).unique():
    title_str = pn + " " + i
    plt.scatter(
        df_export["mean"][
            df_export.index.get_level_values(1) == i
        ].index.get_level_values(0),
        df_export["mean"][df_export.index.get_level_values(1) == i].values,
    )
    plt.xlabel("Year")
    plt.ylabel("Rating")
    plt.title(title_str)
    plt.show()



