## Importing appropriate libraries
from selenium import webdriver
from bs4 import BeautifulSoup
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas
from pandas import DataFrame

## Establishing a connection to Chrome, accessing all NBA Players' 2018-2019
## Advanced Statistics
driver = webdriver.Chrome()
driver.get("https://stats.nba.com/players/advanced/?sort=PLAYER_NAME&dir=-1&Season=2018-19&SeasonType=Regular%20Season")
dropdown = driver.find_element_by_class_name("stats-table-pagination__select")
for option in dropdown.find_elements_by_tag_name("option"):
    if option.text == "All":
        option.click()

## Retrieving and preparing appropriate data
content = driver.page_source
soup = BeautifulSoup(content, features="html.parser")
Stats = soup.find("div", class_="nba-stat-table__overflow")

## Creating a list, Category, of players' names and corresponding statistics
## titles
Category = []
for i in soup.find_all("th", hidden=False)[1:]:
    title = i.text
    Category.append(title)
length = len(Category)
del Category[length-2:]

## Denoting a dictionary to give indexing a degree of readability when accessing
## the players' data
get = {}
for i in range(len(Category)):
    if i >= 1:
        get[Category[i]] = i-1
    else: get[Category[i]] = "Access player inventory via PlayerData.keys()"

## Creating a list, PlayerStats, which contains each row corresponding
## to an individual athlete and their information as a list
PlayerStats = []
for a in Stats.find_all("tr")[1:]:
    name = a.text
    infolist = name.split("\n")[2:]
    length2 = len(infolist)
    del infolist[length2-1:]
    PlayerStats.append(infolist)

## Transforming PlayerStats into a cleaner and more streamlined dictionary object
## for data access and calculations
PlayerData = {}
for i in range(len(PlayerStats)):
    PlayerData[PlayerStats[i][0]] = [PlayerStats[i][1]] + list(map(float, PlayerStats[i][2:]))

## AP measures a player's off-ball offensive contribution
## A negative value indicates lost potential due to turnovers exceeding assists
def AP(Player):
    avg = 0
    total_mins = cm(PlayerData[Player][get["TEAM"]])
    for i in PlayerData.keys():
        if PlayerData[i][get["TEAM"]] == PlayerData[Player][get["TEAM"]] and not i == Player:
            avg += PlayerData[i][get["TS%"]] * (PlayerData[i][get["MIN"]]/total_mins)
    TeamAvgTS = avg*.01
    OffensiveContribution = (PlayerData[Player][get["AST\xa0Ratio"]] - PlayerData[Player][get["TO\xa0Ratio"]])*2*TeamAvgTS
    return OffensiveContribution

## A helper function designed to give weights to each players' TS% for the AP
## metric calculation
def cm(Team):
    count = 0
    for i in PlayerData.keys():
        if PlayerData[i][get["TEAM"]] == Team:
            count += PlayerData[i][get["MIN"]]
    return count

## Adding the AP metric to the previously defined objects for analysis
for i in PlayerData.keys():
    PlayerData[i].append(AP(i))
Category.append("AP")
get["AP"] = 21
print(get)

## Active is a list containing the names of players who will be plotted and whose
## AP metric will be analyzed;a minimum average minutes per game requirement is
## currently set at 32
active = []
for i in PlayerData.keys():
    if PlayerData[i][get["MIN"]] >= 32:
        active.append(i)

## Preparing the player statistics into a list of lists, numbers, of those who
## satisfy the active requirement for plotting
numbers = []
for i in active:
    numbers.append(PlayerData[i])

## Defining a DataFrame, df, for plotting and analysis; the AP metric is added
df = DataFrame(data=numbers, index=active, columns=Category[1:])
metric = df["AP"]

## Plotting the statistics for analysis using matplotlib
plt.scatter(active,metric)
plt.xlabel("Players")
plt.ylabel("AP Metric")
plt.title("NBA 2018-2019 Season Player Metrics")
plt.ion()
plt.show()