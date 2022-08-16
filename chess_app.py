%reset -f
import matplotlib.pyplot as plt
import os
import pandas as pd
import requests
import time

start = time.time()

pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", None)

# Define the player's name.
pn = "RaeKwan"
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
    columns=["date", "player", "rating", "time_control", "eco", "eco_desc", "result"],
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

df['white_wins']= df.apply(white_wins, axis=1)
df['black_wins']= df.apply(black_wins, axis=1)
df['white_losses']= df.apply(white_losses, axis=1)
df['black_losses']= df.apply(black_losses, axis=1)
df['white_draws']= df.apply(white_draws, axis=1)
df['black_draws']= df.apply(black_draws, axis=1)


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
df["time_control"] = df["time_control"].apply(
    lambda x: x.replace("TimeControl", "")
)
df["time_control"] = df["time_control"].apply(lambda x: x.replace('"', ""))
df["time_control"] = df["time_control"].apply(lambda x: x.replace("[", ""))
df["time_control"] = df["time_control"].apply(lambda x: x.replace("]", ""))


# Remove the unnecessary components of the string.
df["eco"] = df["eco"].apply(
    lambda x: x.replace("[ECO", "")
)

df["eco"] = df["eco"].apply(lambda x: x.replace('"', ""))
df["eco"] = df["eco"].apply(lambda x: x.replace(']', ""))
df.head()


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

# Create a year variable.
df["year"] = df["date"].apply(lambda x: x[:4])
df["year"].value_counts()

# Create an annual count variable for each year-time_control.
df["ann_count"] = df.groupby(["year", "time_control"])["rating"].transform(
    len
)

# sort the dataframe
df.sort_values(by=["year", "time_control"], inplace=True)

df.reset_index(drop=True, inplace=True)


df["ann_count"].value_counts()

# Judgement call to remove any time control with less than 12 games per year.
df.drop(df[df["ann_count"] < 12].index, inplace=True)
df.shape

df["time_control"].value_counts()


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

df.head()

# rg: box and whiskser plot off the df dataframe?????

df.groupby(["year", "time_control"])["rating"].describe()


df.groupby(["year", "time_control", 'eco'])["white_wins"].describe()

df.groupby(["year", "time_control", 'eco'])["white_wins"].describe().columns

# This is a working example of the sorting. 

''' Sorting '''
df.groupby(["year", "time_control", 'eco'])["white_wins"].describe().sort_values(by=[ 'year', 'time_control', 'mean', 'count'], ascending=False)

df.groupby(["year", "time_control", 'eco'])["white_wins"].describe().sort_values(by=[ 'year', 'time_control', 'count', 'mean'], ascending=False)

# Per above, look at 2022, 15 minutes + 10. C45 21 games wtih a 0.47
# win rate vs. B54 with 7 games and a 0.71 win rate.... which is more useful to know? How would this compare to the weighted score? 


# Think I need to weight the mean of each win or loss by a weighting factor 
# equal to (# games played in the particular opening / total games played in 
# the time control ). Note that total games played in each time control 
# was previously calculated in a variable named ann_count. 

df.head()

df['year_time_eco_count']= df.groupby(['year', 'time_control', 'eco'])['eco'].transform(len)

df['weights']= df['year_time_eco_count'] / df['ann_count']

df.head()

# Calculate weighted white wins and white losses for each game. This is a temporary
# step to then sum up within each year and time control. 
df['white_wins_weighted'] = df['white_wins'] * df['weights']
df['white_losses_weighted'] = df['white_losses'] * df['weights']

''' Weighted ''' 
# Compare to the sorting 

df[(df['year']== '2022') & (df['eco']== 'C45')] 
df[df['year']== '2022'].head()
df[df['eco']== 'C45'].head()

df['eco'].iloc[0]== 'B20'
df['eco'].str.strip().iloc[0] == 'B20'

df['eco'].str.strip().head()


df[((df['year']== '2022') & (df['eco']== 'C45') ) | ( (df['year']== '2022') & (df['eco']== 'B54') )]



df.info()
df['white_wins_weighted_sum']= df.groupby(['year', 'time_control', 'eco'], group_keys=False)['white_wins_weighted'].apply(lambda x: x.sum())


df['white_wins_weighted_sum']= df.groupby(['year', 'time_control', 'eco'], group_keys=False)['white_wins_weighted'].apply(lambda x: x.sum()).values


df.shape
df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].apply(lambda x: x.sum())

df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].transform('sum')


df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].transform('sum').shape

df['white_wins_weighted_sum']= df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].transform('sum')


df.head()

df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].apply(lambda x: x.sum()).shape

df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].apply(lambda x: x.sum())

df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].apply(lambda x: x.transform('sum'))



df.groupby(['year', 'time_control', 'eco'], group_keys=False)['white_wins_weighted'].apply(lambda x: x.sum()).shape

df.groupby(['year', 'time_control', 'eco'])['white_wins_weighted'].apply(lambda x: x.sum()).values

df.shape

import numpy as np
np.unique(df[['year', 'time_control', 'eco']]).shape

df.head()

df[(df['year']=='2022') & (df['time_control']== '10 minutes')][['year', 'time_control', 'eco', 'year_time_eco_count', 'ann_count', 'weights']].to_excel('df_test.xlsx')

df.head()

df_export = df.groupby(["year", "time_control"])["rating"].describe().round()
df_export
df_export.info()
df_export = df_export.astype(int)

export_string = pn + ".xlsx"
df_export.to_excel(export_string)

end = time.time()
total_time = end - start

total_time
print("execution time", str(total_time))


df_export

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


# Using pivot
df_export.reset_index().pivot("year", "time_control", "mean")

df_export.reset_index().pivot("year", "time_control", "mean").plot()

df_export.reset_index().pivot("year", "time_control", "mean").index
df_export.reset_index().pivot("year", "time_control", "mean").columns

df_export.reset_index().pivot("year", "time_control", "mean").plot()

for i in df_export.reset_index().pivot("year", "time_control", "mean").columns:
    print(i)

