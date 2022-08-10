import pandas as pd
import numpy as np

##############################
##############################
# Note that this script is for a player named Ulfheavypaws.
# To use this script, you need to change the name to the
# player you are interested in analyzing.

# Also, there were two anomalies in the Ulfheavypaws pgn
# that needed to be manually overwritten. This will likely
# not generalize to other pgn's.
#################################
#################################

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


# The pgn file appears to be separated by brackets.
games = pd.read_csv("ulfheavypaws.pgn", sep="]")

games.head(50)

games.info()

games["Unnamed: 1"].isna().sum()
games["Unnamed: 1"].notna().sum()
games[games["Unnamed: 1"].notna()]


# Drop the Unnamed: 1 column which is mostly nulls.
games = games.drop(columns="Unnamed: 1", axis=1)

games.head(50)

# Rename the column containing game data.
games.rename(columns={'[Event "Live Chess"': "data"}, inplace=True)
games.head()

games.tail(50)
games.head(50)

# Examine the pattern to get ratings for white and black games for player Ulfheavypaws.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        "Ulfheavypaws" in games["data"][i + 2]
    ):
        print(i, games["data"][i], games["data"][i + 2], games["data"][i + 6])

for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        "Ulfheavypaws" in games["data"][i + 3]
    ):
        print(i, games["data"][i], games["data"][i + 3], games["data"][i + 12])

# The two obs that don't fit the pattern for black games are
# 2773 and 4795

games["data"].iloc[2760:2790]
games["data"].iloc[4780:4810]

# Create an empty dataframe
df = pd.DataFrame(
    data=[],
    columns=["date", "player", "rating"],
    index=[i for i in range(0, len(games) - 1)],
)

df.head()


# Populate the dataframe with the games data for white games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        "Ulfheavypaws" in games["data"][i + 2]
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 2]
        df["rating"].iloc[i] = games["data"][i + 6]

# Populate the datafrme with the games data for black games.
for i in range(0, len(games) - 1):
    if ("[Date" in str(games["data"][i])) and (
        "Ulfheavypaws" in games["data"][i + 3]
    ):
        df["date"].iloc[i] = games["data"][i]
        df["player"].iloc[i] = games["data"][i + 3]
        df["rating"].iloc[i] = games["data"][i + 12]


df.info()

df

# The two obs that don't fit the pattern for black games are
# 2773 and 4795

games["data"].iloc[2760:2790]
games["data"].iloc[4780:4810]

# Manually overwrite the two black anomalies.
df["rating"].iloc[2773] = '[BlackElo "1294"'
df["rating"].iloc[4795] = '[BlackElo "1231"'

df.dropna(how="all", inplace=True)

df.head()
df.tail()

df.shape

df

df.reset_index(drop=True, inplace=True)
df.head()

# Sccaffolding to generate the right patterns to trim the data.
df["date"].iloc[0]
df["date"].iloc[0][:3]
df["date"].iloc[0][-5:-1]

df["date"].iloc[0][-5:]
df["date"].iloc[0][-1]

df["date"].iloc[0][-11:-1]

df["date"][-11:-1]

# Overwrite the data variable with just the data component
df["date"] = df["date"].apply(lambda x: x[-11:-1])

df.head()

df["player"].iloc[0][8:-1]

# Overwrite the player variabele to just contain the name.
df["player"] = df["player"].apply(lambda x: x[8:-1])

df.head()

df["rating"].iloc[0][-5:-1]

# Retain the numeric portion of the rating.
df["rating"] = df["rating"].apply(lambda x: x[-5:-1])

df.head()
df.tail()

df

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

df.tail()

df.info()

# Create a year variable.
df["year"] = df["date"].apply(lambda x: x[:4])

df.info()

df.head()

df["year"].value_counts()

# Summarize rating by year.
df[["rating", "year"]].groupby("year").describe().round()

# Rating histograms for each year.
df[["rating", "year"]].groupby("year").hist()

# Lots of visualizations could be built here - means over time, histograms overlaid, etc.

# Export to Excel.
df.to_excel("ian.xlsx", index=False)

