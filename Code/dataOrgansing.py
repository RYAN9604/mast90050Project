import random

import numpy as np
import pandas as pd
import random
import datetime as dt
import copy
from collections import defaultdict
import openpyxl

# np.random.seed(10); random.seed(10)

games = pd.read_excel('Data/Round4_LP.xlsx', engine='openpyxl')
games = games.rename(columns={"Unnamed: 9": "Field.2"})
games["Field"] = "nan"
games["Field.1"] = "nan"
games["Field.2"] = "nan"
games["Boundary"] = "nan"
games["Boundary.1"] = "nan"

club_names = []
for index in games.index:
    t1 = games.loc[index]["Team 1"].split()[0]
    t2 = games.loc[index]["Team 2"].split()[0]
    club_names.append([t1, t2])

games["Teams"] = club_names

umps = pd.read_excel('Data/LP_Umps2021.xlsx', engine='openpyxl')
availability = pd.read_excel('Data/LP_Umps2021.xlsx', sheet_name="Availability",
                             usecols="A,E", engine="openpyxl")
playingUmps = pd.read_excel('Data/Lp_playing_Rd4.xlsx', usecols="A,D",
                            engine="openpyxl")

umpMaster = umps
umpAvail = availability

umpMaster = umpMaster.set_index("Name")
umpAvail = umpAvail.set_index("Names")
playingUmps = playingUmps.set_index("Name")

games = games.sort_values(by=["Venue Name", "Match Time"])
games = games.reset_index(drop = True)

# %% Only consider umpires who we have full data for

# Assign availability to playing umps
# Dictionary    playing time : [allowable umpiring times]
allTimes = [str(dt.time(8, 30)), str(dt.time(10, 0)), str(dt.time(11, 0)), str(dt.time(11, 30)),
            str(dt.time(13, 0)), str(dt.time(13, 30)), str(dt.time(14, 30)), str(dt.time(15, 0))]
playAllow = {
    str(dt.time(8, 30)): [str(dt.time(11, 0)), str(dt.time(11, 30)),
                          str(dt.time(13, 0)), str(dt.time(13, 30)), str(dt.time(14, 30)), str(dt.time(15, 0))],
    str(dt.time(10, 0)): [str(dt.time(13, 0)), str(dt.time(13, 30)), str(dt.time(14, 30)),
                          str(dt.time(15, 0))],
    str(dt.time(11, 0)): [str(dt.time(8, 30)), str(dt.time(14, 30)),
                          str(dt.time(15, 0))],
    str(dt.time(11, 30)): [str(dt.time(8, 30)), str(dt.time(14, 30)),
                           str(dt.time(15, 0))],
    str(dt.time(13, 0)): [str(dt.time(8, 30)), str(dt.time(10, 0))],
    str(dt.time(14, 30)): [str(dt.time(8, 30)), str(dt.time(10, 0)),
                           str(dt.time(11, 30))],
    str(dt.time(15, 0)): [str(dt.time(8, 30)), str(dt.time(10, 0)),
                          str(dt.time(11, 30))]
}

for entry in playingUmps.index:
    if entry in umpAvail.index:
        playtime = str(playingUmps.loc[entry][0])

        if playtime != 'None':
            times = copy.deepcopy(playAllow[playtime])
        else:
            times = copy.deepcopy(allTimes)
        umpAvail.loc[entry][0] = times
    else:  # add their available time
        playtime = str(playingUmps.loc[entry][0])

        if type(playtime) != type(np.nan):
            times = copy.deepcopy(playAllow[playtime])
        else:
            times = copy.deepcopy(allTimes)
        newrow = pd.DataFrame(0, index=[entry], columns=[umpAvail.columns[0]],
                              dtype=object)
        newrow.loc[entry][0] = times
        umpAvail = pd.concat([umpAvail, newrow])

for entry in umpAvail.index:
    if entry not in umpMaster.index:
        umpAvail = umpAvail.drop(entry)
        # print(entry)
        

for entry in umpMaster.index:
    if entry not in umpAvail.index:
        newrow = pd.DataFrame(0, index=[entry], columns=[umpAvail.columns[0]],
                              dtype=object)
        newrow.loc[entry][0] = copy.deepcopy(allTimes)
        umpAvail = pd.concat([umpAvail, newrow])

umpAvail = umpAvail.sort_index()
umpMaster = umpMaster.sort_index()

for entry in umpAvail.index:
    avail = umpAvail.loc[entry][0]
    if type(avail) == type(np.nan):
        umpAvail.loc[entry][0] = copy.deepcopy(allTimes)

# print("\n******\n")
# print(np.all(umpMaster.index == umpAvail.index))
# %% Assign umpires to clubs they play for

team = [np.nan for i in range(umpMaster.shape[0])]
umpMaster["Club"] = team

for ump in umpMaster.index:
    t = umpMaster.loc[ump, "Playing"]
    if type(t) == str:
        umpMaster.loc[ump, "Club"] = t.split()[0]

# %% Indicate two or one game and manually review special cases
for ump in umpMaster.index:
    if umpMaster.loc[ump]["2 Games"] == "Yes":
        umpMaster.loc[ump]["2 Games"] = True
    elif umpMaster.loc[ump]["2 Games"] != True:
        umpMaster.loc[ump]["2 Games"] = False

# Round specific availability changes
umpMaster.loc["Boulter, Oscar"]["2 Games"] = False
umpAvail.loc["Boulter, Oscar"][0] = copy.deepcopy(allTimes)
umpAvail.loc["Collopy, John"][0] = copy.deepcopy(allTimes[:-1])
umpAvail.loc["Parker, Cameron"][0] = copy.deepcopy(allTimes[1:])
umpMaster.loc["Lee, Andrew"]["2 Games"] = False
umpAvail.loc["Stacey, Joshua"][0] = [str(dt.time(13, 0)), str(dt.time(15, 0))]

# changes from 'Additional Notes'
umpAvail.loc["Anderson, Callum"][0] = [str(dt.time(13, 0)), str(dt.time(15, 0))]
umpAvail.loc["Brown, Henry"][0] = [str(dt.time(13, 0)), str(dt.time(15, 0))]
umpAvail.loc["Dodds, Matthew"][0] = [str(dt.time(15, 0))]
umpAvail.loc["Lee, Andrew"][0] = [str(dt.time(10, 0)), str(dt.time(11, 30))]
umpAvail.loc["Scott, Angus"][0] = [str(dt.time(13, 0)), str(dt.time(15, 0))]
umpAvail.loc["Walsh, Austin"][0] = [str(dt.time(13, 0)), str(dt.time(15, 0))]
# %% Remove unavailable umpires
for ump in umpAvail.index:
    if umpAvail.loc[ump][0] == "Unavailable":
        umpMaster = umpMaster.drop(ump)
        umpAvail = umpAvail.drop(ump)
        # print(ump)
        
# print("\n******\n")

# for ump in playingUmps.index:
#     if ump not in umpMaster.index:
#         print(ump)

# print(np.all(umpMaster.index == umpAvail.index))

# %%
umpMaster = pd.concat([umpMaster, umpAvail], axis=1)
umpMaster = umpMaster.rename(columns={umpAvail.columns[0]: "Available"})
cols = ["Age Group", "Category", "2 Games", "Available", "Playing", "Club",
        "Additonal Notes", "Last Name", "First Name"]
umpMaster = umpMaster[cols]

# %%
# greedy algorithm:

    
def bestUmp(Umps, Match, notAllowed, gamesLeft):
        """ 
        Umps - dataframe with full umpire details
        Match - a single match 
        notAllowed - a list of not allowed umpires      
        """
        cat = Match["Category"]
        time = str(Match["Match Time"])
        teams = Match["Teams"]
        Umps = Umps.sample(frac=1) #randomise so schedule not always same
        
        if gamesLeft == 1:
            potUmps = list(Umps.loc[Umps["Category"] == cat].index)
            potUmps = sorted(potUmps, key=lambda ump: len(Umps.at[ump, "Available"]))
            
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed and 
                    Umps.at[cand, "2 Games"] == False):
                    return cand
                
            # Try again but relax category condition
            potUmps = list(Umps.index)
            potUmps = sorted(potUmps, key=lambda ump: len(Umps.at[ump, "Available"]))
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed and
                    Umps.at[cand, "2 Games"] == False):
                    return cand
                
            # Drop the game requirement
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed):
                    return cand
        elif gamesLeft == 2:
            potUmps = list(Umps.loc[Umps["Category"] == cat].index)
            potUmps = sorted(potUmps, key=lambda ump: len(Umps.at[ump, "Available"]))
            
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed and 
                    Umps.at[cand, "2 Games"] == True):
                    return cand
                
            # Try again but relax category condition
            potUmps = list(Umps.index)
            potUmps = sorted(potUmps, key=lambda ump: len(Umps.at[ump, "Available"]))
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed and
                    Umps.at[cand, "2 Games"] == True):
                    return cand
                
            # Drop the game requirement
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed):
                    return cand
        else:
            potUmps = list(Umps.loc[Umps["Category"] == cat].index)
            potUmps = sorted(potUmps, key=lambda ump: len(Umps.at[ump, "Available"]))
            
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed):
                    return cand
                
            # Try again but relax category condition
            potUmps = list(Umps.index)
            potUmps = sorted(potUmps, key=lambda ump: len(Umps.at[ump, "Available"]))
            for cand in potUmps:
                if (time in Umps.at[cand, "Available"] and
                    Umps.at[cand, "Club"] not in teams and 
                    cand not in notAllowed):
                    return cand
        
        # Try returning some person
        potUmps = list(Umps.index)
        potUmps = sorted(potUmps, key=lambda ump: len(Umps.at[ump, "Available"]))
        for cand in potUmps:
            if cand not in notAllowed:
                return cand
        
        return "ERROR"

v = [0 for i in range(umpMaster.shape[0])]
w = [[] for i in range(umpMaster.shape[0])]
q = [[] for i in range(umpMaster.shape[0])]
u = [[] for i in range(games.shape[0])]
n = [2 for i in range(games.shape[0])]
t = [0 for i in range(games.shape[0])]

umpMaster['ngames'] = v
umpMaster['UmpCats'] = w
umpMaster['GameIds'] = q
games["ump"] = u
games["Boundaries"] = u
games["umpsNeeded"] = n
games["boundUmps"] = t
    
fieldUmps = list(umpMaster.loc[umpMaster['Category'] != "E"].index)
Fumps = copy.deepcopy(umpMaster.loc[fieldUmps])

# same location
venueSet = games['Venue Name']
venueSet = sorted(set(venueSet))

for ven in venueSet:
    GroundMatches = games.loc[games['Venue Name'] == ven]
    matchesLeft = GroundMatches.shape[0]
    contUmps = []
    
    for match in GroundMatches.index:

        newumps = []
        FullMatch = games.loc[match]
        # for a specific match
        
        # assign continuing umpires
        notAllowed = copy.deepcopy(contUmps)
        toRemove = []
        for ump in notAllowed:
            games.at[match, "ump"].append(ump)
            umpMaster.at[ump, "ngames"] += 1
            umpMaster.at[ump, "GameIds"].append(match)
            umpMaster.at[ump, "UmpCats"].append(FullMatch["Category"])
            games.at[match, "umpsNeeded"] -= 1    
            contUmps.remove(ump)
        
        
        # assign one new umpire to the match
        if games.at[match, "umpsNeeded"] == 1:
            newumps = [bestUmp(Fumps, FullMatch, notAllowed, matchesLeft)] 
            if newumps[0] == "ERROR": break
                
            games.at[match, "ump"].append(newumps[0])
            umpMaster.at[newumps[0], "ngames"] += 1
            umpMaster.at[newumps[0], "GameIds"].append(match)
            umpMaster.at[newumps[0], "UmpCats"].append(FullMatch["Category"])
            games.at[match, "umpsNeeded"] -= 1
        elif games.at[match, "umpsNeeded"] == 2:
            newumps = [bestUmp(Fumps, FullMatch, [], matchesLeft)]
            if newumps[0] == "ERROR": break
        
            notAllowed = [newumps[0]]
            nextump = bestUmp(Fumps, FullMatch, notAllowed, matchesLeft)
            newumps.append(nextump)
            if newumps[1] == "ERROR": break
        
            for ump in newumps:
                games.at[match, "ump"].append(ump)
                umpMaster.at[ump, "ngames"] += 1
                umpMaster.at[ump, "GameIds"].append(match)
                umpMaster.at[ump, "UmpCats"].append(FullMatch["Category"])
                games.at[match, "umpsNeeded"] -= 1        
        
        for ump in games.at[match, "ump"]:
            if umpMaster.at[ump, "ngames"] == 1 and not umpMaster.at[ump, "2 Games"]:
                Fumps = Fumps.drop(ump)
            elif umpMaster.at[ump, "ngames"] == 2:
                Fumps = Fumps.drop(ump)
            else:
                contUmps.append(ump)
                
        matchesLeft -= 1
        
        if matchesLeft == 0:
            for ump in contUmps:
                Fumps = Fumps.drop(ump)
                    

        
        


# %% OBJECTIVE FUNCTION
example_sched = pd.read_excel('Data/Round4_LP_Example.xlsx', engine='openpyxl')
example_sched = example_sched.rename(columns={"Unnamed: 9": "Field.2"})


def objective(schedule, umpMaster):
    obj = 0
    upCatPenalty = 10
    downCatPenalty = 5
    not2gamesPenalty = 50
    noGamePenalty = 10 ** 5
    TooManyGamesPen = 10 ** 6
    # Penalties for categories of matches that umpires do
    for i in range(schedule.shape[0]):
        matchCat = schedule.loc[i]["Category"]
        u1 = schedule.loc[i]["Field"]
        u2 = schedule.loc[i]["Field.1"]
        u3 = schedule.loc[i]["Field.2"]
        b1 = schedule.loc[i]["Boundary"]
        b2 = schedule.loc[i]["Boundary.1"]
        fieldumps = [u1, u2, u3]
        for ump in fieldumps:
            # make sure the entry is valid
            if type(ump) == type('string') and ump != 'nan':
                umpCat = umpMaster.loc[ump]["Category"]
                diff = ord(umpCat) - ord(matchCat)
                if diff < 0:
                    # ump is higher skill than match
                    obj += downCatPenalty * (-1) * diff
                elif diff > 0:
                    # ump is lower skill than match
                    obj += upCatPenalty * diff

    # Penalty for not doing preferrred number of games
    ump_numgames = defaultdict(lambda: 0)
    for ump in schedule["Field"]:
        ump_numgames[ump] += 1
    for ump in schedule["Field.1"]:
        ump_numgames[ump] += 1
    for ump in schedule["Field.2"]:
        ump_numgames[ump] += 1
    for ump in schedule["Boundary"]:
        ump_numgames[ump] += 1
    for ump in schedule["Boundary.1"]:
        ump_numgames[ump] += 1

    # print(ump_numgames)
    for ump in umpMaster.index:
        if ump_numgames[ump] == 0:
            obj += noGamePenalty
        elif umpMaster.loc[ump]["2 Games"] == True and ump_numgames[ump] == 1:
            obj += not2gamesPenalty
        elif umpMaster.loc[ump]["2 Games"] == False and ump_numgames[ump] == 2:
            # print(ump)
            obj += TooManyGamesPen

    print('objective =', obj)
    return obj, schedule

a, b = objective(example_sched, umpMaster)

#%% Assign umps to position in df
for i in games.index:
    umps = games.loc[i]["ump"]

    if len(umps) == 1:
        games.at[i,"Field"] = umps[0]
    elif len(umps) == 2:
        games.at[i,"Field"] = umps[0]
        games.at[i,"Field.1"] = umps[1]
    elif len(umps) == 3:
        games.at[i,"Field"] = umps[0]
        games.at[i,"Field.1"] = umps[1]
        games.at[i,"Field.1"] = umps[2]

boundUmps = list(umpMaster.loc[umpMaster['Category'] == "E"].index)

for game in games.loc[games['Category'] == "A"].index:
    venue = games.at[game, "Venue Name"]
    if games.at[game, "Match Time"] == dt.time(13,0):
        for ump in boundUmps:
            if(len(umpMaster.at[ump, "GameIds"]) == 0 and 
               games.at[game, "boundUmps"] <= 1 and 
               str(dt.time(13,0)) in umpMaster.at[ump, "Available"]):
                # assign to first game 
                umpMaster.at[ump, "GameIds"].append(game)
                games.at[game, "Boundaries"].append(ump)
                games.at[game, "boundUmps"] += 1
                umpMaster.at[ump, "ngames"] += 1
                
                # assign to second game if wanted 
                if (umpMaster.at[ump, "2 Games"] == True and 
                    games.at[game+1, "Venue Name"] == venue):
                    
                    umpMaster.at[ump, "GameIds"].append(game+1)
                    games.at[game+1, "Boundaries"].append(ump)
                    games.at[game+1, "boundUmps"] += 1
                    umpMaster.at[ump, "ngames"] += 1
                    
# In practice remaining umpires can easily be assigned manually.
                
