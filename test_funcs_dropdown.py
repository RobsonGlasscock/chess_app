import matplotlib.pyplot as plt
import os
import pandas as pd
import requests
import streamlit as st
import time

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

year = ""
time_control = ""
time_control_df = None
year_list_df = None

# Define the player's name.
pn = st.text_input("Enter your username below:", value="")
if pn != "":

    @st.cache(suppress_st_warning=True)
    def data_pull():

        # The chess.com player name in the url path is lowercase. Convert to lower here.
        player_name = pn.lower()

        # Use the player name within the url string.
        archives_url_pull = (
            "https://api.chess.com/pub/player/"
            + player_name
            + "/games/archives"
        )

        # Pull the archives data which will show which YYYY/MM the player had games
        archives = requests.get(archives_url_pull)

        # strip off the dictionary structure-like components of the string and other components that aren't necessary.
        stripper_list = ['{"archives":', "}", "]", "["]
        for i, j in enumerate(stripper_list):
            if (i == 0) and type(archives == "requests.models.Response"):
                archives = archives.text.replace(j, "")
            else:
                archives = archives.replace(j, "")

        # Make a directory for the player name and change into it.
        os.makedirs(pn, exist_ok=True)
        os.chdir(pn)

        # write out to a file.
        with open("archives.txt", "w") as f:
            f.write(archives)

        # import the data and transpose the columns into rows.
        df_archives = pd.read_csv("archives.txt", sep=",").transpose()

        # Modify the original url string to be in accordance with the dataframe elements. This is the first step to stripping off the url and retaining only the YYYY/MM for the player.
        archives_url_mod = archives_url_pull.replace("archives", "")

        # Below resets the index and retains the original indices.
        df_archives.reset_index(drop=False, inplace=True)

        # Remove the url part of the strings and retain only YYYY/MM.
        df_archives["index"] = df_archives["index"].apply(
            lambda x: x.replace(archives_url_mod, "")
        )

        # Create a list of the archive links.
        year_month_list = df_archives["index"].values.tolist()

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
            # create the full path to use below.
            save_to = os.path.join(pather, games_string)
            # write out the files to the game_lib path.
            with open(save_to, "w") as f:
                f.write(game_year_month.text)

        os.chdir("./game_lib")

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

        # Create an empty dataframe
        df = pd.DataFrame(
            data=[],
            columns=[
                "date",
                "player",
                "rating",
                "time_control",
                "eco",
                "eco_desc",
                "result",
                "color",
            ],
            index=[i for i in range(0, len(games) - 1)],
        )

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
                df["color"].iloc[i] = "white"

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
                df["color"].iloc[i] = "black"

        df.dropna(how="all", inplace=True)

        # drop the non-elo obs.

        # df["dropper"] = "Elo" in df["rating"]
        # "Elo" in df["rating"].iloc[0]

        df["dropper"] = df["rating"].apply(lambda x: "Elo" not in x)

        df.drop(df[df["dropper"] == 1].index, inplace=True)

        df.drop(columns=["dropper"], inplace=True)

        # Create functions for the following variables: white wins, white losses, black wins,
        # black losses, white draws, black draws.
        def white_wins(df):
            if ("White" in df["player"]) and ("1-0" in df["result"]):
                return 1
            else:
                return 0

        def black_wins(df):
            if ("Black" in df["player"]) and ("0-1" in df["result"]):
                return 1
            else:
                return 0

        def white_losses(df):
            if ("White" in df["player"]) and ("0-1" in df["result"]):
                return 1
            else:
                return 0

        def black_losses(df):
            if ("Black" in df["player"]) and ("1-0" in df["result"]):
                return 1
            else:
                return 0

        def white_draws(df):
            if ("White" in df["player"]) and ("1/2-1/2" in df["result"]):
                return 1
            else:
                return 0

        def black_draws(df):
            if ("Black" in df["player"]) and ("1/2-1/2" in df["result"]):
                return 1
            else:
                return 0

        # Create cumulative counts where wins =+1 and losses =-1

        def white_cumul(df):
            if ("White" in df["player"]) and ("1-0" in df["result"]):
                return 1
            if ("White" in df["player"]) and ("0-1" in df["result"]):
                return -1
            else:
                return 0

        def black_cumul(df):
            if ("Black" in df["player"]) and ("0-1" in df["result"]):
                return 1
            if ("Black" in df["player"]) and ("1-0" in df["result"]):
                return -1
            else:
                return 0

        # Create vars for combined df.
        df["white_wins"] = df.apply(white_wins, axis=1)
        df["black_wins"] = df.apply(black_wins, axis=1)
        df["white_losses"] = df.apply(white_losses, axis=1)
        df["black_losses"] = df.apply(black_losses, axis=1)
        df["white_draws"] = df.apply(white_draws, axis=1)
        df["black_draws"] = df.apply(black_draws, axis=1)

        df["white_cumul"] = df.apply(white_cumul, axis=1)
        df["black_cumul"] = df.apply(black_cumul, axis=1)

        # Overwrite the data variable with just the data component
        df["date"] = df["date"].apply(lambda x: x[-12:-2])

        # Overwrite the player variabele to just contain the name.
        df["player"] = df["player"].apply(lambda x: x[8:-2])

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

        # Remove the unnecessary components of the string.

        df["time_control"] = df["time_control"].apply(
            lambda x: x.replace("TimeControl", "")
        )
        df["time_control"] = df["time_control"].apply(
            lambda x: x.replace('"', "")
        )
        df["time_control"] = df["time_control"].apply(
            lambda x: x.replace("[", "")
        )
        df["time_control"] = df["time_control"].apply(
            lambda x: x.replace("]", "")
        )

        # Remove the unnecessary components of the string.
        df["eco"] = df["eco"].apply(lambda x: x.replace("[ECO", ""))

        df["eco"] = df["eco"].apply(lambda x: x.replace('"', ""))
        df["eco"] = df["eco"].apply(lambda x: x.replace("]", ""))
        df["eco"] = df["eco"].apply(lambda x: x.strip())

        df["eco_desc"] = df["eco_desc"].apply(lambda x: x.strip())

        df["eco_desc"] = df["eco_desc"].apply(
            lambda x: x.replace('[ECOUrl "https://www.chess.com/openings/', "")
        )

        df["eco_desc"] = df["eco_desc"].apply(lambda x: x.replace('"', ""))

        df["eco_desc"] = df["eco_desc"].apply(lambda x: x.replace("]", ""))

        # Create a year variable.
        df["year"] = df["date"].apply(lambda x: x[:4])

        # Create an annual count variable for each year-time_control.
        df["ann_count"] = df.groupby(["year", "time_control"])[
            "rating"
        ].transform(len)

        # sort the dataframe
        df.sort_values(by=["year", "time_control"], inplace=True)

        df.reset_index(drop=True, inplace=True)

        def time_convert(col):
            if col.strip() == "180":
                return "3 minutes"
            if col.strip() == "60":
                return "1 minute"
            if col.strip() == "600":
                return "10 minutes"
            if col.strip() == "900+10":
                return "15 minutes + 10"
            if col.strip() == "900+5":
                return "15 minutes + 5"
            if col.strip() == "1200+10":
                return "20 minutes + 10"
            if col.strip() == "1200":
                return "20 minutes"
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

        # Create cumulative sums for white and black by eco. This uses the +1 for wins and -1 for losses.
        df["white_cumul_sum"] = df.groupby(["year", "time_control", "eco"])[
            "white_cumul"
        ].transform("sum")

        df["black_cumul_sum"] = df.groupby(["year", "time_control", "eco"])[
            "black_cumul"
        ].transform("sum")

        # Create separate df's from white games and black games where draws are excluded.
        # Use these to create the dummy variables. As shown below, Richard's white_win
        # dummy for 2022, D02 shows 0.09 for 84 games, but this
        # is misleading because he was white in 16 of these games and black in 68 of them.
        # My win and loss dummies don't actually work for the combined dataframe. One way
        # # I wanted to get around this was to create a cumulative count variable that
        # increments white wins +1 and decrements for white losses. This would show the
        # "spread" of wins over losses or losses over wins.

        # Judgement call to remove any time control with less than 12 games per year. Do this for df, white_df, and black_df.
        df.drop(df[df["ann_count"] < 12].index, inplace=True)
        df_white = df[df["color"] == "white"].copy(deep=True)
        df_black = df[df["color"] == "black"].copy(deep=True)

        df.to_csv(pn + "/df.csv")
        df_white.to_csv(pn + "/df_white.csv")
        df_black.to_csv(pn + "/df_black.csv")

    data_pull()

    #####################
    # Show players their games for each year and time control - this is needed here rather than inside data_pull() because data_pull() is set to only run once. So, if a player changes an input then the table goes away if it is inside data_pull().
    ###################
    df = pd.read_csv(pn + "/df.csv")
    df_val_cts = (
        df.groupby("year")["time_control"].value_counts().reset_index(level=0)
    )
    df_val_cts.info()
    df_val_cts.rename(
        columns={"time_control": "Number of Games"}, inplace=True
    )
    df_val_cts.reset_index(level=0, inplace=True)
    df_val_cts.rename(
        columns={"time_control": "Time Control", "year": "Year"}, inplace=True
    )
    val_ct_cols = ["Year", "Time Control", "Number of Games"]

    # CSS to ineject contained in a string
    # https://docs.streamlit.io/knowledge-base/using-streamlit/hide-row-indices-displaying-dataframe
    hide_table_row_index = """ 
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        </style>
        """
    st.write("__Your time control counts for each year are:__")
    st.table(df_val_cts[val_ct_cols])
    st.markdown(hide_table_row_index, unsafe_allow_html=True)

    # st.write(df_val_cts['Year'].unique())
    # st.write(df_val_cts['Time Control'].unique())

    time_control_list = []
    for i in df_val_cts["Time Control"].unique():
        time_control_list.append(i)

    year_list = []
    for i in df_val_cts["Year"].unique():
        year_list.append(int(i))
    # st.write(time_control_list)
    # st.write(year_list)

    time_control_df = pd.DataFrame(data={"Time Control": time_control_list})
    time_control_df.to_csv("time_control_list.csv")
    year_list_df = pd.DataFrame(data={"Year": year_list})
    year_list_df.to_csv("year_list.csv")

    ########################
    time_control_df = pd.read_csv("time_control_list.csv")

    year_list_df = pd.read_csv("year_list.csv")
    year_list_df["Year"] = year_list_df["Year"].astype(str)
    # st.write(year_list_df.info())

    if time_control_df is not None:
        # tc_list= []
        tc_list = time_control_df["Time Control"].values.tolist()
        tc_list.insert(0, "")
        # for i in time_control_df['Time Control'].values():
        # tc_list.append(i)

    if year_list_df is not None:
        # y_list= []
        y_list = year_list_df["Year"].values.tolist()
        y_list.insert(0, "")
        # for i in year_list_df['Year']:
        # y_list.append(i)

    if (time_control_df is not None) & (year_list_df is not None):
        time_control = st.selectbox(
            "Which time control do you want to see analytics for?",
            tc_list,
            index=0,
        )
        year = st.selectbox(
            "Which year do you want to see analytics for", y_list, index=0
        )

    if (time_control != "") & (year != ""):

        def analytics():
            hide_table_row_index = """ 
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """
            print("year is", year)
            print("year type is", type(year))
            print("time_control is", time_control)
            df_white = pd.read_csv(pn + "/df_white.csv")
            print(df_white.head())
            df_white["year"] = df_white["year"].astype(str)
            print(df_white.info())
            df_black = pd.read_csv(pn + "/df_black.csv")
            df_black["year"] = df_black["year"].astype(str)
            df = pd.read_csv(pn + "/df.csv")
            df["year"] = df["year"].astype(str)
            #####################
            # Create accuracy for each year, time, and eco combination.
            ##########################
            df_white["win_rate"] = df_white.groupby(
                ["year", "time_control", "eco"]
            )["white_wins"].transform("mean")

            df_black["win_rate"] = df_black.groupby(
                ["year", "time_control", "eco"]
            )["black_wins"].transform("mean")
            print("end of analytics loop", df_black["win_rate"].head())

            ###############
            # Best white openings
            #########

            # Initialize three empty lists
            eco = []
            no_games = []
            cumul_win_loss = []
            win_rate = []

            # Append the eco's for the five best white openings to the eco list.
            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["white_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .index[:5]
                .get_level_values(2)
            ):
                eco.append(i)

            # Append the number of games for the five best white openings to the no_games list.
            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["white_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[:5]["count"]
            ):
                no_games.append(int(i))

            # Append the cumulative wins over losses for the five best white openings to the cumul_win_loss list.
            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["white_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[:5]["mean"]
            ):
                cumul_win_loss.append(int(i))

            # Append the win_rate for the five best white openings to the win_rate list.

            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])[
                    "white_cumul_sum", "win_rate"
                ]
                .describe()
                .sort_values(
                    by=[
                        "year",
                        "time_control",
                        ("white_cumul_sum", "mean"),
                        ("white_cumul_sum", "count"),
                    ],
                    ascending=False,
                )[("win_rate", "mean")]
                .iloc[:5]
                .values
            ):
                win_rate.append(i)

            best_white_df = pd.DataFrame(
                data={
                    "ECO": eco,
                    "Color": "White",
                    "Number of Games": no_games,
                    "Wins Over Losses": cumul_win_loss,
                    "Win Percentage": win_rate,
                }
            )

            del eco, no_games, cumul_win_loss

            ###############
            # Worst white openings
            #########

            # Initialize three empty lists
            eco = []
            no_games = []
            cumul_win_loss = []
            win_rate = []

            # Append the eco's for the five worst white openings to the eco list.
            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["white_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .index[-5:]
                .get_level_values(2)
            ):
                eco.append(i)

            # Append the number of games for the five worst white openings to the no_games list.
            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["white_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[-5:]["count"]
            ):
                no_games.append(int(i))

            # Append the cumulative wins over losses for the five worst white openings to the cumul_win_loss list.
            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["white_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[-5:]["mean"]
            ):
                cumul_win_loss.append(int(i))

            # Append the win_rate for the five worst white openings to the win_rate list.

            for i in (
                df_white[
                    (df_white["year"] == year)
                    & (df_white["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])[
                    "white_cumul_sum", "win_rate"
                ]
                .describe()
                .sort_values(
                    by=[
                        "year",
                        "time_control",
                        ("white_cumul_sum", "mean"),
                        ("white_cumul_sum", "count"),
                    ],
                    ascending=False,
                )[("win_rate", "mean")]
                .iloc[-5:]
                .values
            ):
                win_rate.append(i)

            worst_white_df = pd.DataFrame(
                data={
                    "ECO": eco,
                    "Color": "White",
                    "Number of Games": no_games,
                    "Losses Over Wins": cumul_win_loss,
                    "Win Percentage": win_rate,
                }
            )

            worst_white_df.sort_values(
                by="Losses Over Wins", ascending=True, inplace=True
            )

            del eco, no_games, cumul_win_loss

            ###############
            # Best black openings
            #########

            # Initialize three empty lists
            eco = []
            no_games = []
            cumul_win_loss = []
            win_rate = []

            # Append the eco's for the five best black openings to the eco list.
            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["black_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .index[:5]
                .get_level_values(2)
            ):
                eco.append(i)

            # Append the number of games for the five best black openings to the no_games list.
            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["black_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[:5]["count"]
            ):
                no_games.append(int(i))

            # Append the cumulative wins over losses for the five best black openings to the cumul_win_loss list.
            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["black_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[:5]["mean"]
            ):
                cumul_win_loss.append(int(i))

            # Append the win_rate for the five best black openings to the win_rate list.

            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])[
                    "black_cumul_sum", "win_rate"
                ]
                .describe()
                .sort_values(
                    by=[
                        "year",
                        "time_control",
                        ("black_cumul_sum", "mean"),
                        ("black_cumul_sum", "count"),
                    ],
                    ascending=False,
                )[("win_rate", "mean")]
                .iloc[:5]
                .values
            ):
                win_rate.append(i)

            best_black_df = pd.DataFrame(
                data={
                    "ECO": eco,
                    "Color": "Black",
                    "Number of Games": no_games,
                    "Wins Over Losses": cumul_win_loss,
                    "Win Percentage": win_rate,
                }
            )

            del eco, no_games, cumul_win_loss
            ###############
            # Worst black openings
            #########

            # Initialize three empty lists
            eco = []
            no_games = []
            cumul_win_loss = []
            win_rate = []

            # Append the eco's for the five worst black openings to the eco list.
            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["black_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .index[-5:]
                .get_level_values(2)
            ):
                eco.append(i)

            # Append the number of games for the five worst black openings to the no_games list.
            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["black_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[-5:]["count"]
            ):
                no_games.append(int(i))

            # Append the cumulative wins over losses for the five worst black openings to the cumul_win_loss list.
            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])["black_cumul_sum"]
                .describe()
                .sort_values(
                    by=["year", "time_control", "mean", "count"],
                    ascending=False,
                )
                .iloc[-5:]["mean"]
            ):
                cumul_win_loss.append(int(i))

            # Append the win_rate for the five worst black openings to the win_rate list.

            for i in (
                df_black[
                    (df_black["year"] == year)
                    & (df_black["time_control"] == time_control)
                ]
                .groupby(["year", "time_control", "eco"])[
                    "black_cumul_sum", "win_rate"
                ]
                .describe()
                .sort_values(
                    by=[
                        "year",
                        "time_control",
                        ("black_cumul_sum", "mean"),
                        ("black_cumul_sum", "count"),
                    ],
                    ascending=False,
                )[("win_rate", "mean")]
                .iloc[-5:]
                .values
            ):
                win_rate.append(i)

            worst_black_df = pd.DataFrame(
                data={
                    "ECO": eco,
                    "Color": "Black",
                    "Number of Games": no_games,
                    "Losses Over Wins": cumul_win_loss,
                    "Win Percentage": win_rate,
                }
            )

            worst_black_df.sort_values(
                by="Losses Over Wins", ascending=True, inplace=True
            )

            del eco, no_games, cumul_win_loss

            df_export = (
                df.groupby(["year", "time_control"])["rating"]
                .describe()
                .round()
            )
            df_export = df_export.astype(int)

            #################################
            # Link openings to opening descriptions
            ###################################
            df_openings = (
                df.groupby(["eco"])["eco_desc"]
                .describe()
                .reset_index(drop=False)
            )

            df_openings = df_openings[["eco", "top"]].copy(deep=True)

            df_openings.rename(
                columns={"eco": "ECO", "top": "ECO Description"}, inplace=True
            )

            #######################
            # Merge in the eco_descriptions to the best and worst dataframes
            ###################

            best_white_df = best_white_df.merge(
                df_openings, on="ECO", how="left"
            )

            worst_white_df = worst_white_df.merge(
                df_openings, on="ECO", how="left"
            )

            best_black_df = best_black_df.merge(
                df_openings, on="ECO", how="left"
            )

            worst_black_df = worst_black_df.merge(
                df_openings, on="ECO", how="left"
            )

            ##############################
            # Best and Worst Openings
            #############################

            best = pd.concat([best_white_df, best_black_df])
            worst = pd.concat([worst_white_df, worst_black_df])

            # Convert to text percentages for display.
            best["Win Percentage"] = best["Win Percentage"] * 100
            best["Win Percentage"] = best["Win Percentage"].astype(int)
            best["Win Percentage"] = best["Win Percentage"].astype(str) + "%"

            worst["Win Percentage"] = worst["Win Percentage"] * 100
            worst["Win Percentage"] = worst["Win Percentage"].astype(int)
            worst["Win Percentage"] = worst["Win Percentage"].astype(str) + "%"

            st.write("__Your best openings are:__")
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.table(best)
            st.write("__Your worst openings are:__")
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.table(worst)

            #############################
            # Box and whisker plots
            #################################

            # Create a variable for the graph titles.
            title_str = pn + " " + time_control

            # Initialize an empty list and put the year indices for the time control into the list.
            year_idx = []
            for i in (
                df[df["time_control"] == time_control]["rating"]
                .groupby(df["year"])
                .describe()
                .index
            ):
                year_idx.append(i)

            # Create an empty dictionary and then put values of the rating series for the year and time control into a dictionary with the key equal to the string of col_year and the values equal to the series. This step also includes creating a list of the x_labels and the default box plot integers for creating an x axis on the box plots with the years rather than 1, 2, 3, etc.
            dicter = {}
            x_labels = []
            x_ints = []
            for i, j in enumerate(
                df[df["time_control"] == time_control]["rating"]
                .groupby(df["year"])
                .describe()
                .index
            ):
                name = "col" + "_" + str(j)
                x_labels.append(str(j))
                x_ints.append(i + 1)
                key = name
                values = df[
                    (df["time_control"] == time_control) & (df["year"] == j)
                ]["rating"]
                dicter[key] = values

            # Create auto-labels for the datapoints on the scatterplot graph. Earlier, I automated finding out the number of years for the x axis. Since that is known, the mean of the rating within each time control will have the same length and order. Below grabs these values.

            y_labels = (
                df[df["time_control"] == time_control]["rating"]
                .groupby(df["year"])
                .describe()["mean"]
                .values.astype(int)
            )

            # Create a list of np arrays for the values of the series of the ratings for each year.
            cols = []
            for i in dicter.keys():
                cols.append(dicter[i].values)

            # Per above, the list contains numpy arrays for each year.

            # Create the graph which plots each of the arrays as a separate box plot.
            fig_2, ax = plt.subplots()
            ax.boxplot(cols)
            plt.xticks(x_ints, x_labels)
            plt.title(title_str)
            for i in range(len(x_labels)):
                # Note that below has to use the x_ints associated with the x_labels but not the x_labels list.
                plt.text(
                    x_ints[i] + 0.33,
                    y_labels[i],
                    str(y_labels[i]),
                    horizontalalignment="center",
                )
            plt.show()

            ############################
            # Scatter Plots
            ###########################

            # Graph of average rating for the time control over all the years the player has played that time control.

            fig_1, ax = plt.subplots()
            ax.scatter(
                df_export["mean"][
                    df_export.index.get_level_values(1) == time_control
                ].index.get_level_values(0),
                df_export["mean"][
                    df_export.index.get_level_values(1) == time_control
                ].values,
            )
            plt.xlabel("Year")
            plt.ylabel("Rating")
            plt.title(title_str)
            # I would like the y axis to be larger than the ratings by a specified amount so that the labels will fit nicely. Below sets the limits equal to the min and max of the y_labels ndarray.
            plt.ylim(y_labels.min() - 50, y_labels.max() + 50)
            # Below uses a loop since the number of years the player has played is not known before hand. Again, the x_labels have the same legnth as the y_labels and will be in the same order from year_1 to year_1+whatever. Below is equivalent to multiple plt.text() statements and the loop is constructed to essentially "write" as many of these statements as necessary.
            for i in range(len(x_labels)):
                plt.text(
                    x_labels[i],
                    y_labels[i] + 12.0,
                    str(y_labels[i]),
                    horizontalalignment="center",
                )
            plt.show()

            st.write(
                "__Below are plots of your average rating for each year__:"
            )

            st.pyplot(fig_1)
            st.pyplot(fig_2)

            #############################

            st.write(
                "__Time control definitions are available here__: http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm#c9.6"
            )

            st.write(
                "__Here are some useful conversion examples from the documentation:__"
            )
            st.write(
                """The third Time control field kind is formed as two positive integers separated by a solidus ("/") character. The first integer is the number of moves in the period and the second is the number of seconds in the period. Thus, a time control period of 40 moves in 2 1/2 hours would be represented as "40/9000"."""
            )
            st.write(
                """The fifth TimeControl field kind is used for an "incremental" control period. It should only be used for the last descriptor in a TimeControl tag value and is usually the only descriptor in the value. The format consists of two positive integers separated by a plus sign ("+") character. The first integer gives the minimum number of seconds allocated for the period and the second integer gives the number of extra seconds added after each move is made. So, an incremental time control of 90 minutes plus one extra minute per move would be given by "4500+60" in the TimeControl tag value."""
            )

        analytics()

