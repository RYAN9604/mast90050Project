import random

import numpy as np
import pandas as pd
import datetime as dt
import copy
from collections import defaultdict
import openpyxl
import time as ts

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



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
        u3 = schedule.loc[i]["Field.2"]
        b1 = schedule.loc[i]["Boundary"]
        b2 = schedule.loc[i]["Boundary.1"]
        if len(schedule.loc[i]["Field"])==1:
            u1 = schedule.loc[i]["Field"][0]
        else:
            u1 = schedule.loc[i]["Field"]
        if len(schedule.loc[i]["Field.1"])==1:
            u2 = schedule.loc[i]["Field.1"][0]
        else:
            u2 = schedule.loc[i]["Field.1"]
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
        if len(ump) == 0:
            continue
        ump = ump[0]
        ump_numgames[ump] += 1
    for ump in schedule["Field.1"]:
        if len(ump) == 0:
            continue
        ump = ump[0]
        ump_numgames[ump] += 1
    #for ump in schedule["Field.2"]:
    #
    #    ump_numgames[ump] += 1
    for ump in schedule["Boundary"]:

        ump_numgames[ump] += 1
    for ump in schedule["Boundary.1"]:

        ump_numgames[ump] += 1



    for ump in umpMaster.index:
        if ump_numgames[ump] == 0:
            obj += noGamePenalty
        elif umpMaster.loc[ump]["2 Games"] == True and ump_numgames[ump] == 1:
            obj += not2gamesPenalty
        elif umpMaster.loc[ump]["2 Games"] == False and ump_numgames[ump] == 2:
            obj += TooManyGamesPen

    return obj, schedule

#objctive difference when switching two ump
def objectdifferece(umpA, umpB):
    objBefore = 0
    objAfter = 0
    upCatPenalty = 10
    downCatPenalty = 5
    not2gamesPenalty = 50
    noGamePenalty = 10 ** 5
    TooManyGamesPen = 10 ** 6
    for i in umpMaster.loc[umpA]["working category"]:
        diffBefore = ord(umpMaster.loc[umpA]["Category"]) - ord(i)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpB]["Category"]) - ord(i)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    for j in umpMaster.loc[umpB]["working category"]:
        diffBefore = ord(umpMaster.loc[umpB]["Category"]) - ord(j)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpA]["Category"]) - ord(j)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    if len(umpMaster.loc[umpA]["game"]) != len(umpMaster.loc[umpB]["game"]) \
        and umpMaster.loc[umpA]["2 Games"] != umpMaster.loc[umpB]["2 Games"]:
        if umpMaster.loc[umpA]["2 Games"]:
            ump2 = umpA
            ump1 = umpB
        else:
            ump2 = umpB
            ump1 = umpA
        if len(umpMaster.loc[ump2]["game"]) == 2 and len(umpMaster.loc[ump1]["game"]) == 1:
            objAfter += not2gamesPenalty + TooManyGamesPen
        if len(umpMaster.loc[ump1]["game"]) == 2 and len(umpMaster.loc[ump2]["game"]) == 1:
            objBefore += not2gamesPenalty + TooManyGamesPen
        if len(umpMaster.loc[ump2]["game"]) == 2 and len(umpMaster.loc[ump1]["game"]) == 0:
            objBefore += noGamePenalty
            objAfter += noGamePenalty + TooManyGamesPen
        if len(umpMaster.loc[ump1]["game"]) == 2 and len(umpMaster.loc[ump2]["game"]) == 0:
            objBefore += TooManyGamesPen + noGamePenalty
            objAfter += noGamePenalty
        if len(umpMaster.loc[ump2]["game"]) == 1 and len(umpMaster.loc[ump1]["game"]) == 0:
            objBefore += not2gamesPenalty + noGamePenalty
            objAfter += noGamePenalty
        if len(umpMaster.loc[ump1]["game"]) == 1 and len(umpMaster.loc[ump2]["game"]) == 0:
            objBefore += noGamePenalty
            objAfter += not2gamesPenalty + noGamePenalty
    res = objAfter - objBefore
    return res


#objctive difference when switching one ump with 2 Games and 2 umpires with one game respectively
def objectdiffereceThree(umpA, umpB, umpC):
    objBefore = 0
    objAfter = 0
    upCatPenalty = 10
    downCatPenalty = 5
    not2gamesPenalty = 50
    noGamePenalty = 10 ** 5
    TooManyGamesPen = 10 ** 6
    for i in umpMaster.loc[umpA]["working category"]:
        diffBefore = ord(umpMaster.loc[umpA]["Category"]) - ord(i)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpC]["Category"]) - ord(i)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    for i in umpMaster.loc[umpB]["working category"]:
        diffBefore = ord(umpMaster.loc[umpB]["Category"]) - ord(i)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpC]["Category"]) - ord(i)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    j = umpMaster.loc[umpC]["working category"][0]
    diffBefore = ord(umpMaster.loc[umpC]["Category"]) - ord(j)
    if diffBefore < 0:
        objBefore += downCatPenalty * (-1) * diffBefore
    elif diffBefore > 0:
        objBefore += upCatPenalty * diffBefore
    diffAfter = ord(umpMaster.loc[umpA]["Category"]) - ord(j)
    if diffAfter < 0:
        objAfter += downCatPenalty * (-1) * diffAfter
    elif diffAfter > 0:
        objAfter += upCatPenalty * diffAfter
    j = umpMaster.loc[umpC]["working category"][1]
    diffBefore = ord(umpMaster.loc[umpC]["Category"]) - ord(j)
    if diffBefore < 0:
        objBefore += downCatPenalty * (-1) * diffBefore
    elif diffBefore > 0:
        objBefore += upCatPenalty * diffBefore
    diffAfter = ord(umpMaster.loc[umpB]["Category"]) - ord(j)
    if diffAfter < 0:
        objAfter += downCatPenalty * (-1) * diffAfter
    elif diffAfter > 0:
        objAfter += upCatPenalty * diffAfter
    res = objAfter - objBefore
    return res
for seedNum in range(100):
    random.seed(seedNum)

    games = pd.read_excel('Data/Round4_LP.xlsx', engine='openpyxl')
    games = games.rename(columns={"Unnamed: 9": "Field.2"})
    games["Field"] = np.nan
    games["Field.1"] = np.nan
    games["Field.2"] = np.nan
    games["Boundary"] = np.nan
    games["Boundary.1"] = np.nan

    club_names = []
    for index in games.index:
        t1 = games.loc[index]["Team 1"].split()[0]
        t2 = games.loc[index]["Team 2"].split()[0]
        club_names.append([t1, t2])

    games["Teams"] = club_names

    umps = pd.read_excel('Data/LP_Umps2021.xlsx', engine='openpyxl')
    availability = pd.read_excel('Data/LP_Umps2021.xlsx', sheet_name="Availability",
                                 usecols="A,E", engine="openpyxl")
    playingUmps = pd.read_excel('Data/LP_playing_Rd4.xlsx', usecols="A,D",
                                engine="openpyxl")

    umpMaster = umps
    umpAvail = availability

    umpMaster = umpMaster.set_index("Name")
    umpAvail = umpAvail.set_index("Names")
    playingUmps = playingUmps.set_index("Name")

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

    #print("\n******\n")
    #print(np.all(umpMaster.index == umpAvail.index))
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

    # %%
    umpMaster = pd.concat([umpMaster, umpAvail], axis=1)
    umpMaster = umpMaster.rename(columns={umpAvail.columns[0]: "Available"})
    cols = ["Age Group", "Category", "2 Games", "Available", "Playing", "Club",
            "Additonal Notes", "Last Name", "First Name"]
    umpMaster = umpMaster[cols]
    resultObject = []
    resultTime = []
    localSteps = []

# %%
# greedy algorithm

    u = [[] for i in range(games.shape[0])]
    v = [[] for i in range(umpMaster.shape[0])]
    w = [[] for i in range(umpMaster.shape[0])]
    p = [[] for i in range(umpMaster.shape[0])]
    k = [[] for i in range(umpMaster.shape[0])]
    games['ump'] = u
    umpMaster['game'] = v
    umpMaster['working time'] = w
    umpMaster['working team'] = p
    umpMaster['working category'] = k
    l = [[] for i in range(games.shape[0])]
    games['Field'] = l
    l1 = [[] for i in range(games.shape[0])]
    games['Field.1'] = l1
    l2 = [[] for i in range(games.shape[0])]
    games['Field.2'] = l2
    games.set_index('Venue Name')


    # same location initial solution
    venueSet = games['Venue Name']
    venueSet = sorted(set(venueSet))
    teamMap = {i : {} for i in venueSet}
    cateGoryMap = {j : {} for j in venueSet}
    umpNumberMap = {k : {} for k in venueSet}
    indexMap = {l : {} for l in venueSet}
    timeAvailable = {m : [] for m in venueSet}
    typeMap = {n : {} for n in venueSet}
    for x in venueSet:
        for i in games.index:
            if games.loc[i]['Venue Name'] == x:
                timeAvailable[x].append(str(games.loc[i]['Match Time']))
                teamMap[x][str(games.loc[i]['Match Time'])] = games.loc[i]['Teams']
                cateGoryMap[x][str(games.loc[i]['Match Time'])] = games.loc[i]['Category']
                umpNumberMap[x][str(games.loc[i]['Match Time'])] = 0
                indexMap[x][str(games.loc[i]['Match Time'])] = i
                typeMap[x][str(games.loc[i]['Match Time'])] = []
    for x in venueSet:
        for j in umpMaster.index:
            if len(umpMaster.loc[j]['game']) == 2 or not umpMaster.loc[j]['2 Games'] or umpMaster.loc[j]['Category'] == "E":
                continue
            timeSet = sorted(set(timeAvailable[x]) & set(umpMaster.loc[j]['Available']))
            if len(timeSet) >= 2:
                filterTeamTime = []
                for y in timeSet:
                    if x not in teamMap[x][y]:
                        filterTeamTime.append(y)
                if len(filterTeamTime) >= 2:
                    for z in filterTeamTime:
       #                 if cateGoryMap[x][z] == umpMaster.loc[j]['Category']:
                            games.loc[indexMap[x][z]]['ump'].append(j)
                            if games.loc[indexMap[x][z]]['Field'] == []:
                                games.loc[indexMap[x][z]]['Field'].append(j)
                            else:
                                games.loc[indexMap[x][z]]['Field.1'].append(j)
                            umpNumberMap[x][z] += 1
                            if umpNumberMap[x][z] >= 2:
                                timeAvailable[x].remove(z)
                            umpMaster.loc[j]['game'].append(x)
                            umpMaster.loc[j]['working time'].append(z)
                            umpMaster.loc[j]['working team'] += teamMap[x][z]
                            umpMaster.loc[j]['working category'] += cateGoryMap[x][z]
                            typeMap[x][z].append(2)
                            indexNumber = filterTeamTime.index(z)
                            if indexNumber + 1 <= len(filterTeamTime) - 1:
                                anotherTime = filterTeamTime[indexNumber + 1]
                            else:
                                anotherTime = filterTeamTime[indexNumber - 1]
                            games.loc[indexMap[x][anotherTime]]['ump'].append(j)
                            if games.loc[indexMap[x][anotherTime]]['Field'] == []:
                                games.loc[indexMap[x][anotherTime]]['Field'].append(j)
                            else:
                                games.loc[indexMap[x][anotherTime]]['Field.1'].append(j)
                            umpNumberMap[x][anotherTime] += 1
                            if umpNumberMap[x][anotherTime] >= 2:
                                timeAvailable[x].remove(anotherTime)
                            umpMaster.loc[j]['game'].append(x)
                            umpMaster.loc[j]['working time'].append(anotherTime)
                            umpMaster.loc[j]['working team'] += teamMap[x][anotherTime]
                            umpMaster.loc[j]['working category'] += cateGoryMap[x][anotherTime]
                            typeMap[x][anotherTime].append(2)
                            break
    for i in games.index:
        time = games.loc[i]['Match Time']
        time = str(time)
        Category = games.loc[i]['Category']
        team = games.loc[i]['Teams']
        for j in umpMaster.index:
            if time in umpMaster.loc[j]['Available'] and abs(ord(umpMaster.loc[j]['Category']) - ord(Category)) <= 2 \
                    and umpMaster.loc[j]['Club'] not in team and len(games.loc[i]['ump']) < 2 \
                    and ((len(umpMaster.loc[j]['game']) < 2 and umpMaster.loc[j]['2 Games']) or (
                    len(umpMaster.loc[j]['game']) < 1 and not umpMaster.loc[j]['2 Games'])):
                if len(umpMaster.loc[j]['game']) == 1 and i not in umpMaster.loc[j]['game']:
                    continue
                umpMaster.loc[j]['Available'].remove(time)
                umpMaster.loc[j]['working time'].append(time)
                games.loc[i]['ump'].append(j)
                if games.loc[i]['Field'] == []:
                    games.loc[i]['Field'].append(j)
                else:
                    games.loc[i]['Field.1'].append(j)
                umpMaster.loc[j]['working team'] += team
                umpMaster.loc[j]['game'].append(games.loc[i]['Venue Name'])
                umpMaster.loc[j]['working category'] += games.loc[i]['Category']
                if umpMaster.loc[j]['2 Games']:
                    typeMap[games.loc[i]['Venue Name']][time].append(2)
                else:
                    typeMap[games.loc[i]['Venue Name']][time].append(1)

    originalObject, b = objective(games, umpMaster)



    # local step 1:
    umpSet = list(umpMaster.index)
    local = 0
    start = ts.time()
    switchTimes = 0
    localOptima = 0
    while local <= 499:
        a = random.choice(umpSet, )
        while len(umpMaster.loc[a]['game']) == []:
            a = random.choice(umpSet, )
        b = copy.deepcopy(a)
        while b == a or len(umpMaster.loc[b]['game']) != len(umpMaster.loc[a]['game']):
            b = random.choice(umpSet)


        if (all(item in umpMaster.loc[a]['Available'] for item in umpMaster.loc[b]['working time'])) \
                and (all(item in umpMaster.loc[b]['Available'] for item in umpMaster.loc[a]['working time']))\
                and umpMaster.loc[b]['Club'] not in umpMaster.loc[a]['working team']\
                and umpMaster.loc[a]['Club'] not in umpMaster.loc[b]['working team']\
                and objectdifferece(a, b) < 0:
            for i in range(len(umpMaster.loc[a]['game'])):
                if games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]]['Field'] == [a]:
                    games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                        'Field'].clear()
                    games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                        'Field'].append(b)
                else:
                    games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                        'Field.1'].clear()
                    games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                        'Field.1'].append(b)
            for i in range(len(umpMaster.loc[a]['game'])):
                if games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]]['Field'] == [b]:
                    games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                        'Field'].clear()
                    games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                        'Field'].append(a)
                else:
                    games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                        'Field.1'].clear()
                    games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                        'Field.1'].append(a)
            tempWorkingTime = copy.deepcopy(umpMaster.loc[a]['working time'])
            umpMaster.loc[a]['working time'] = copy.deepcopy(umpMaster.loc[b]['working time'])
            umpMaster.loc[b]['working time'] = copy.deepcopy(tempWorkingTime)
            tempWorkingTeam = copy.deepcopy(umpMaster.loc[a]['working team'])
            umpMaster.loc[a]['working team'] = copy.deepcopy(umpMaster.loc[b]['working team'])
            umpMaster.loc[b]['working team'] = copy.deepcopy(tempWorkingTeam)
            tempWorkingCategory = copy.deepcopy(umpMaster.loc[a]['working category'])
            umpMaster.loc[a]['working category'] = copy.deepcopy(umpMaster.loc[b]['working category'])
            umpMaster.loc[b]['working category'] = copy.deepcopy(tempWorkingCategory)
            tempWorkingGame = copy.deepcopy(umpMaster.loc[a]['game'])
            umpMaster.loc[a]['game'] = copy.deepcopy(umpMaster.loc[b]['game'])
            umpMaster.loc[b]['game'] = copy.deepcopy(tempWorkingGame)
            localOptima = copy.deepcopy(local)
            switchTimes += 1


    #facility search

        c = random.choice(umpSet)
        while not umpMaster.loc[c]['2 Games'] or not len(umpMaster.loc[c]['game']) == 2:
            c = random.choice(umpSet)
        venue = random.choice(venueSet)
        timeSS = timeAvailable[venue]
        lenghth = len(timeSS)
        while lenghth == 0 or lenghth == 1:
            venue = random.choice(venueSet)
            timeSS = timeAvailable[venue]
            lenghth = len(timeSS)
        num = random.randint(0, lenghth-1)
        if num >= lenghth/2.0:
            a = num
            b = num - 1
        else:
            a = num
            b = num + 1
        #print(lenghth)
        #print(num)
        #print(b)



        if 1 in typeMap[venue][timeSS[a]] and 1 in typeMap[venue][timeSS[b]]:
            umpA = games.loc[indexMap[venue][timeSS[a]]]['Field'][0]
            if umpMaster.loc[umpA]['2 Games'] == True:
                if len(games.loc[indexMap[venue][timeSS[a]]]['Field.1']) == 0 :
                    continue
                umpA = games.loc[indexMap[venue][timeSS[a]]]['Field.1'][0]
            umpB = games.loc[indexMap[venue][timeSS[b]]]['Field'][0]
            if umpMaster.loc[umpB]['2 Games'] == True:
                if len(games.loc[indexMap[venue][timeSS[b]]]['Field.1']) == 0 :
                    continue
                umpB = games.loc[indexMap[venue][timeSS[b]]]['Field.1'][0]
            if (all(item in umpMaster.loc[c]['Available'] for item in umpMaster.loc[umpA]['working time']))\
            and (all(item in umpMaster.loc[c]['Available'] for item in umpMaster.loc[umpB]['working time']))\
            and umpMaster.loc[c]['working time'][0] in umpMaster.loc[umpA]['Available']\
            and umpMaster.loc[c]['working time'][1] in umpMaster.loc[umpB]['Available']\
            and umpMaster.loc[c]['Club'] not in umpMaster.loc[umpA]['working team']\
            and umpMaster.loc[c]['Club'] not in umpMaster.loc[umpB]['working team']\
            and umpMaster.loc[umpB]['Club'] not in umpMaster.loc[c]['working team']\
            and umpMaster.loc[umpA]['Club'] not in umpMaster.loc[c]['working team']\
            and objectdiffereceThree(umpA,umpB,c) < 0:

                a = umpA
                b = umpB
                if len(umpMaster.loc[a]['working time']) == 2 or len(umpMaster.loc[b]['working time']) == 2:
                    continue
                if games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]]['Field'] == [a]:

                    games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                        'Field'].clear()
                    games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                        'Field'].append(c)

                else:
                    games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                        'Field.1'].clear()
                    games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                        'Field.1'].append(c)


                if games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]]['Field'] == [b]:
                    games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                        'Field'].clear()
                    games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                        'Field'].append(c)
                else:
                    games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                        'Field.1'].clear()
                    games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                        'Field.1'].append(c)
                if games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]]['Field'] == [c]:
                    games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                        'Field'].clear()
                    games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                        'Field'].append(a)
                else:
                    games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                        'Field.1'].clear()
                    games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                        'Field.1'].append(a)
                if games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]]['Field'] == [c]:
                    games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                        'Field'].clear()
                    games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                        'Field'].append(b)
                else:
                    games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                        'Field.1'].clear()
                    games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                        'Field.1'].append(b)


import random

import numpy as np
import pandas as pd
import datetime as dt
import copy
from collections import defaultdict
import openpyxl
import time as ts

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



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
        u3 = schedule.loc[i]["Field.2"]
        b1 = schedule.loc[i]["Boundary"]
        b2 = schedule.loc[i]["Boundary.1"]
        if len(schedule.loc[i]["Field"])==1:
            u1 = schedule.loc[i]["Field"][0]
        else:
            u1 = schedule.loc[i]["Field"]
        if len(schedule.loc[i]["Field.1"])==1:
            u2 = schedule.loc[i]["Field.1"][0]
        else:
            u2 = schedule.loc[i]["Field.1"]
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
        if len(ump) == 0:
            continue
        ump = ump[0]
        ump_numgames[ump] += 1
    for ump in schedule["Field.1"]:
        if len(ump) == 0:
            continue
        ump = ump[0]
        ump_numgames[ump] += 1
    #for ump in schedule["Field.2"]:
    #
    #    ump_numgames[ump] += 1
    for ump in schedule["Boundary"]:

        ump_numgames[ump] += 1
    for ump in schedule["Boundary.1"]:

        ump_numgames[ump] += 1



    for ump in umpMaster.index:
        if ump_numgames[ump] == 0:
            obj += noGamePenalty
        elif umpMaster.loc[ump]["2 Games"] == True and ump_numgames[ump] == 1:
            obj += not2gamesPenalty
        elif umpMaster.loc[ump]["2 Games"] == False and ump_numgames[ump] == 2:
            obj += TooManyGamesPen

    return obj, schedule

#objctive difference when switching two ump
def objectdifferece(umpA, umpB):
    objBefore = 0
    objAfter = 0
    upCatPenalty = 10
    downCatPenalty = 5
    not2gamesPenalty = 50
    noGamePenalty = 10 ** 5
    TooManyGamesPen = 10 ** 6
    for i in umpMaster.loc[umpA]["working category"]:
        diffBefore = ord(umpMaster.loc[umpA]["Category"]) - ord(i)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpB]["Category"]) - ord(i)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    for j in umpMaster.loc[umpB]["working category"]:
        diffBefore = ord(umpMaster.loc[umpB]["Category"]) - ord(j)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpA]["Category"]) - ord(j)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    if len(umpMaster.loc[umpA]["game"]) != len(umpMaster.loc[umpB]["game"]) \
        and umpMaster.loc[umpA]["2 Games"] != umpMaster.loc[umpB]["2 Games"]:
        if umpMaster.loc[umpA]["2 Games"]:
            ump2 = umpA
            ump1 = umpB
        else:
            ump2 = umpB
            ump1 = umpA
        if len(umpMaster.loc[ump2]["game"]) == 2 and len(umpMaster.loc[ump1]["game"]) == 1:
            objAfter += not2gamesPenalty + TooManyGamesPen
        if len(umpMaster.loc[ump1]["game"]) == 2 and len(umpMaster.loc[ump2]["game"]) == 1:
            objBefore += not2gamesPenalty + TooManyGamesPen
        if len(umpMaster.loc[ump2]["game"]) == 2 and len(umpMaster.loc[ump1]["game"]) == 0:
            objBefore += noGamePenalty
            objAfter += noGamePenalty + TooManyGamesPen
        if len(umpMaster.loc[ump1]["game"]) == 2 and len(umpMaster.loc[ump2]["game"]) == 0:
            objBefore += TooManyGamesPen + noGamePenalty
            objAfter += noGamePenalty
        if len(umpMaster.loc[ump2]["game"]) == 1 and len(umpMaster.loc[ump1]["game"]) == 0:
            objBefore += not2gamesPenalty + noGamePenalty
            objAfter += noGamePenalty
        if len(umpMaster.loc[ump1]["game"]) == 1 and len(umpMaster.loc[ump2]["game"]) == 0:
            objBefore += noGamePenalty
            objAfter += not2gamesPenalty + noGamePenalty
    res = objAfter - objBefore
    return res


#objctive difference when switching one ump with 2 Games and 2 umpires with one game respectively
def objectdiffereceThree(umpA, umpB, umpC):
    objBefore = 0
    objAfter = 0
    upCatPenalty = 10
    downCatPenalty = 5
    not2gamesPenalty = 50
    noGamePenalty = 10 ** 5
    TooManyGamesPen = 10 ** 6
    for i in umpMaster.loc[umpA]["working category"]:
        diffBefore = ord(umpMaster.loc[umpA]["Category"]) - ord(i)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpC]["Category"]) - ord(i)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    for i in umpMaster.loc[umpB]["working category"]:
        diffBefore = ord(umpMaster.loc[umpB]["Category"]) - ord(i)
        if diffBefore < 0:
            objBefore += downCatPenalty * (-1) * diffBefore
        elif diffBefore > 0:
            objBefore += upCatPenalty * diffBefore
        diffAfter = ord(umpMaster.loc[umpC]["Category"]) - ord(i)
        if diffAfter < 0:
            objAfter += downCatPenalty * (-1) * diffAfter
        elif diffAfter > 0:
            objAfter += upCatPenalty * diffAfter
    j = umpMaster.loc[umpC]["working category"][0]
    diffBefore = ord(umpMaster.loc[umpC]["Category"]) - ord(j)
    if diffBefore < 0:
        objBefore += downCatPenalty * (-1) * diffBefore
    elif diffBefore > 0:
        objBefore += upCatPenalty * diffBefore
    diffAfter = ord(umpMaster.loc[umpA]["Category"]) - ord(j)
    if diffAfter < 0:
        objAfter += downCatPenalty * (-1) * diffAfter
    elif diffAfter > 0:
        objAfter += upCatPenalty * diffAfter
    j = umpMaster.loc[umpC]["working category"][1]
    diffBefore = ord(umpMaster.loc[umpC]["Category"]) - ord(j)
    if diffBefore < 0:
        objBefore += downCatPenalty * (-1) * diffBefore
    elif diffBefore > 0:
        objBefore += upCatPenalty * diffBefore
    diffAfter = ord(umpMaster.loc[umpB]["Category"]) - ord(j)
    if diffAfter < 0:
        objAfter += downCatPenalty * (-1) * diffAfter
    elif diffAfter > 0:
        objAfter += upCatPenalty * diffAfter
    res = objAfter - objBefore
    return res

random.seed(10086)

games = pd.read_excel('Data/Round4_LP.xlsx', engine='openpyxl')
games = games.rename(columns={"Unnamed: 9": "Field.2"})
games["Field"] = np.nan
games["Field.1"] = np.nan
games["Field.2"] = np.nan
games["Boundary"] = np.nan
games["Boundary.1"] = np.nan

club_names = []
for index in games.index:
    t1 = games.loc[index]["Team 1"].split()[0]
    t2 = games.loc[index]["Team 2"].split()[0]
    club_names.append([t1, t2])

games["Teams"] = club_names

umps = pd.read_excel('Data/LP_Umps2021.xlsx', engine='openpyxl')
availability = pd.read_excel('Data/LP_Umps2021.xlsx', sheet_name="Availability",
                             usecols="A,E", engine="openpyxl")
playingUmps = pd.read_excel('Data/LP_playing_Rd4.xlsx', usecols="A,D",
                            engine="openpyxl")

umpMaster = umps
umpAvail = availability

umpMaster = umpMaster.set_index("Name")
umpAvail = umpAvail.set_index("Names")
playingUmps = playingUmps.set_index("Name")

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

#print("\n******\n")
#print(np.all(umpMaster.index == umpAvail.index))
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

# %%
umpMaster = pd.concat([umpMaster, umpAvail], axis=1)
umpMaster = umpMaster.rename(columns={umpAvail.columns[0]: "Available"})
cols = ["Age Group", "Category", "2 Games", "Available", "Playing", "Club",
        "Additonal Notes", "Last Name", "First Name"]
umpMaster = umpMaster[cols]
resultObject = []
resultTime = []
localSteps = []


#greedy algorithm

u = [[] for i in range(games.shape[0])]
v = [[] for i in range(umpMaster.shape[0])]
w = [[] for i in range(umpMaster.shape[0])]
p = [[] for i in range(umpMaster.shape[0])]
k = [[] for i in range(umpMaster.shape[0])]
games['ump'] = u
umpMaster['game'] = v
umpMaster['working time'] = w
umpMaster['working team'] = p
umpMaster['working category'] = k
l = [[] for i in range(games.shape[0])]
games['Field'] = l
l1 = [[] for i in range(games.shape[0])]
games['Field.1'] = l1
l2 = [[] for i in range(games.shape[0])]
games['Field.2'] = l2
games.set_index('Venue Name')


# same location initial solution
venueSet = games['Venue Name']
venueSet = sorted(set(venueSet))
teamMap = {i : {} for i in venueSet}
cateGoryMap = {j : {} for j in venueSet}
umpNumberMap = {k : {} for k in venueSet}
indexMap = {l : {} for l in venueSet}
timeAvailable = {m : [] for m in venueSet}
typeMap = {n : {} for n in venueSet}
for x in venueSet:
    for i in games.index:
        if games.loc[i]['Venue Name'] == x:
            timeAvailable[x].append(str(games.loc[i]['Match Time']))
            teamMap[x][str(games.loc[i]['Match Time'])] = games.loc[i]['Teams']
            cateGoryMap[x][str(games.loc[i]['Match Time'])] = games.loc[i]['Category']
            umpNumberMap[x][str(games.loc[i]['Match Time'])] = 0
            indexMap[x][str(games.loc[i]['Match Time'])] = i
            typeMap[x][str(games.loc[i]['Match Time'])] = []
for x in venueSet:
    for j in umpMaster.index:
        if len(umpMaster.loc[j]['game']) == 2 or not umpMaster.loc[j]['2 Games'] or umpMaster.loc[j]['Category'] == "E":
            continue
        timeSet = sorted(set(timeAvailable[x]) & set(umpMaster.loc[j]['Available']))
        if len(timeSet) >= 2:
            filterTeamTime = []
            for y in timeSet:
                if x not in teamMap[x][y]:
                    filterTeamTime.append(y)
            if len(filterTeamTime) >= 2:
                for z in filterTeamTime:
   #                 if cateGoryMap[x][z] == umpMaster.loc[j]['Category']:
                        games.loc[indexMap[x][z]]['ump'].append(j)
                        if games.loc[indexMap[x][z]]['Field'] == []:
                            games.loc[indexMap[x][z]]['Field'].append(j)
                        else:
                            games.loc[indexMap[x][z]]['Field.1'].append(j)
                        umpNumberMap[x][z] += 1
                        if umpNumberMap[x][z] >= 2:
                            timeAvailable[x].remove(z)
                        umpMaster.loc[j]['game'].append(x)
                        umpMaster.loc[j]['working time'].append(z)
                        umpMaster.loc[j]['working team'] += teamMap[x][z]
                        umpMaster.loc[j]['working category'] += cateGoryMap[x][z]
                        typeMap[x][z].append(2)
                        indexNumber = filterTeamTime.index(z)
                        if indexNumber + 1 <= len(filterTeamTime) - 1:
                            anotherTime = filterTeamTime[indexNumber + 1]
                        else:
                            anotherTime = filterTeamTime[indexNumber - 1]
                        games.loc[indexMap[x][anotherTime]]['ump'].append(j)
                        if games.loc[indexMap[x][anotherTime]]['Field'] == []:
                            games.loc[indexMap[x][anotherTime]]['Field'].append(j)
                        else:
                            games.loc[indexMap[x][anotherTime]]['Field.1'].append(j)
                        umpNumberMap[x][anotherTime] += 1
                        if umpNumberMap[x][anotherTime] >= 2:
                            timeAvailable[x].remove(anotherTime)
                        umpMaster.loc[j]['game'].append(x)
                        umpMaster.loc[j]['working time'].append(anotherTime)
                        umpMaster.loc[j]['working team'] += teamMap[x][anotherTime]
                        umpMaster.loc[j]['working category'] += cateGoryMap[x][anotherTime]
                        typeMap[x][anotherTime].append(2)
                        break
for i in games.index:
    time = games.loc[i]['Match Time']
    time = str(time)
    Category = games.loc[i]['Category']
    team = games.loc[i]['Teams']
    for j in umpMaster.index:
        if time in umpMaster.loc[j]['Available'] and abs(ord(umpMaster.loc[j]['Category']) - ord(Category)) <= 2 \
                and umpMaster.loc[j]['Club'] not in team and len(games.loc[i]['ump']) < 2 \
                and ((len(umpMaster.loc[j]['game']) < 2 and umpMaster.loc[j]['2 Games']) or (
                len(umpMaster.loc[j]['game']) < 1 and not umpMaster.loc[j]['2 Games'])):
            if len(umpMaster.loc[j]['game']) == 1 and i not in umpMaster.loc[j]['game']:
                continue
            umpMaster.loc[j]['Available'].remove(time)
            umpMaster.loc[j]['working time'].append(time)
            games.loc[i]['ump'].append(j)
            if games.loc[i]['Field'] == []:
                games.loc[i]['Field'].append(j)
            else:
                games.loc[i]['Field.1'].append(j)
            umpMaster.loc[j]['working team'] += team
            umpMaster.loc[j]['game'].append(games.loc[i]['Venue Name'])
            umpMaster.loc[j]['working category'] += games.loc[i]['Category']
            if umpMaster.loc[j]['2 Games']:
                typeMap[games.loc[i]['Venue Name']][time].append(2)
            else:
                typeMap[games.loc[i]['Venue Name']][time].append(1)


originalObject, b = objective(games, umpMaster)



# local step 1:
umpSet = list(umpMaster.index)
local = 0
start = ts.time()
switchTimes = 0
localOptima = 0
while local <= 499:
    a = random.choice(umpSet, )
    while len(umpMaster.loc[a]['game']) == []:
        a = random.choice(umpSet, )
    b = copy.deepcopy(a)
    while b == a or len(umpMaster.loc[b]['game']) != len(umpMaster.loc[a]['game']):
        b = random.choice(umpSet)


    if (all(item in umpMaster.loc[a]['Available'] for item in umpMaster.loc[b]['working time'])) \
            and (all(item in umpMaster.loc[b]['Available'] for item in umpMaster.loc[a]['working time']))\
            and umpMaster.loc[b]['Club'] not in umpMaster.loc[a]['working team']\
            and umpMaster.loc[a]['Club'] not in umpMaster.loc[b]['working team']\
            and objectdifferece(a, b) < 0:
        for i in range(len(umpMaster.loc[a]['game'])):
            if games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]]['Field'] == [a]:
                games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                    'Field'].clear()
                games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                    'Field'].append(b)
            else:
                games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                    'Field.1'].clear()
                games.loc[indexMap[umpMaster.loc[a]['game'][i]][umpMaster.loc[a]['working time'][i]]][
                    'Field.1'].append(b)
        for i in range(len(umpMaster.loc[a]['game'])):
            if games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]]['Field'] == [b]:
                games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                    'Field'].clear()
                games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                    'Field'].append(a)
            else:
                games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                    'Field.1'].clear()
                games.loc[indexMap[umpMaster.loc[b]['game'][i]][umpMaster.loc[b]['working time'][i]]][
                    'Field.1'].append(a)
        tempWorkingTime = copy.deepcopy(umpMaster.loc[a]['working time'])
        umpMaster.loc[a]['working time'] = copy.deepcopy(umpMaster.loc[b]['working time'])
        umpMaster.loc[b]['working time'] = copy.deepcopy(tempWorkingTime)
        tempWorkingTeam = copy.deepcopy(umpMaster.loc[a]['working team'])
        umpMaster.loc[a]['working team'] = copy.deepcopy(umpMaster.loc[b]['working team'])
        umpMaster.loc[b]['working team'] = copy.deepcopy(tempWorkingTeam)
        tempWorkingCategory = copy.deepcopy(umpMaster.loc[a]['working category'])
        umpMaster.loc[a]['working category'] = copy.deepcopy(umpMaster.loc[b]['working category'])
        umpMaster.loc[b]['working category'] = copy.deepcopy(tempWorkingCategory)
        tempWorkingGame = copy.deepcopy(umpMaster.loc[a]['game'])
        umpMaster.loc[a]['game'] = copy.deepcopy(umpMaster.loc[b]['game'])
        umpMaster.loc[b]['game'] = copy.deepcopy(tempWorkingGame)
        localOptima = copy.deepcopy(local)
        switchTimes += 1


#facility search

    c = random.choice(umpSet)
    while not umpMaster.loc[c]['2 Games'] or not len(umpMaster.loc[c]['game']) == 2:
        c = random.choice(umpSet)
    venue = random.choice(venueSet)
    timeSS = timeAvailable[venue]
    lenghth = len(timeSS)
    while lenghth == 0 or lenghth == 1:
        venue = random.choice(venueSet)
        timeSS = timeAvailable[venue]
        lenghth = len(timeSS)
    num = random.randint(0, lenghth-1)
    if num >= lenghth/2.0:
        a = num
        b = num - 1
    else:
        a = num
        b = num + 1
    #print(lenghth)
    #print(num)
    #print(b)



    if 1 in typeMap[venue][timeSS[a]] and 1 in typeMap[venue][timeSS[b]]:
        umpA = games.loc[indexMap[venue][timeSS[a]]]['Field'][0]
        if umpMaster.loc[umpA]['2 Games'] == True:
            if len(games.loc[indexMap[venue][timeSS[a]]]['Field.1']) == 0 :
                continue
            umpA = games.loc[indexMap[venue][timeSS[a]]]['Field.1'][0]
        umpB = games.loc[indexMap[venue][timeSS[b]]]['Field'][0]
        if umpMaster.loc[umpB]['2 Games'] == True:
            if len(games.loc[indexMap[venue][timeSS[b]]]['Field.1']) == 0 :
                continue
            umpB = games.loc[indexMap[venue][timeSS[b]]]['Field.1'][0]
        if (all(item in umpMaster.loc[c]['Available'] for item in umpMaster.loc[umpA]['working time']))\
        and (all(item in umpMaster.loc[c]['Available'] for item in umpMaster.loc[umpB]['working time']))\
        and umpMaster.loc[c]['working time'][0] in umpMaster.loc[umpA]['Available']\
        and umpMaster.loc[c]['working time'][1] in umpMaster.loc[umpB]['Available']\
        and umpMaster.loc[c]['Club'] not in umpMaster.loc[umpA]['working team']\
        and umpMaster.loc[c]['Club'] not in umpMaster.loc[umpB]['working team']\
        and umpMaster.loc[umpB]['Club'] not in umpMaster.loc[c]['working team']\
        and umpMaster.loc[umpA]['Club'] not in umpMaster.loc[c]['working team']\
        and objectdiffereceThree(umpA,umpB,c) < 0:

            a = umpA
            b = umpB
            if len(umpMaster.loc[a]['working time']) == 2 or len(umpMaster.loc[b]['working time']) == 2:
                continue
            if games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]]['Field'] == [a]:

                games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                    'Field'].clear()
                games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                    'Field'].append(c)

            else:
                games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                    'Field.1'].clear()
                games.loc[indexMap[umpMaster.loc[a]['game'][0]][umpMaster.loc[a]['working time'][0]]][
                    'Field.1'].append(c)


            if games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]]['Field'] == [b]:
                games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                    'Field'].clear()
                games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                    'Field'].append(c)
            else:
                games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                    'Field.1'].clear()
                games.loc[indexMap[umpMaster.loc[b]['game'][0]][umpMaster.loc[b]['working time'][0]]][
                    'Field.1'].append(c)
            if games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]]['Field'] == [c]:
                games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                    'Field'].clear()
                games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                    'Field'].append(a)
            else:
                games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                    'Field.1'].clear()
                games.loc[indexMap[umpMaster.loc[c]['game'][0]][umpMaster.loc[c]['working time'][0]]][
                    'Field.1'].append(a)
            if games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]]['Field'] == [c]:
                games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                    'Field'].clear()
                games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                    'Field'].append(b)
            else:
                games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                    'Field.1'].clear()
                games.loc[indexMap[umpMaster.loc[c]['game'][1]][umpMaster.loc[c]['working time'][1]]][
                    'Field.1'].append(b)


            tempWorkingTime = copy.deepcopy(umpMaster.loc[c]['working time'])
            umpMaster.loc[c]['working time'].clear()
            umpMaster.loc[c]['working time'].append(copy.deepcopy(umpMaster.loc[a]['working time'][0]))
            umpMaster.loc[c]['working time'].append(copy.deepcopy(umpMaster.loc[b]['working time'][0]))
            umpMaster.loc[a]['working time'] = copy.deepcopy([tempWorkingTime[0]])
            umpMaster.loc[b]['working time'] = copy.deepcopy([tempWorkingTime[1]])




            tempWorkingTeam = umpMaster.loc[c]['working team']
            umpMaster.loc[c]['working team'] = []
            umpMaster.loc[c]['working team'].append(umpMaster.loc[a]['working team'][0])
            umpMaster.loc[c]['working team'].append(umpMaster.loc[b]['working team'][0])
            umpMaster.loc[a]['working team'] = [tempWorkingTeam[0]]
            umpMaster.loc[b]['working team'] = [tempWorkingTeam[1]]
            tempWorkingCategory = umpMaster.loc[c]['working category']
            umpMaster.loc[c]['working category'] = []
            umpMaster.loc[c]['working category'].append(umpMaster.loc[a]['working category'][0])
            umpMaster.loc[c]['working category'].append(umpMaster.loc[b]['working category'][0])
            umpMaster.loc[a]['working category'] = [tempWorkingCategory[0]]
            umpMaster.loc[b]['working category'] = [tempWorkingCategory[1]]
            tempWorkingGame = umpMaster.loc[c]['game']
            umpMaster.loc[c]['game'] = []
            umpMaster.loc[c]['game'].append(umpMaster.loc[a]['game'][0])
            umpMaster.loc[c]['game'].append(umpMaster.loc[b]['game'][0])
            umpMaster.loc[a]['game'] = [tempWorkingGame[0]]
            umpMaster.loc[b]['game'] = [tempWorkingGame[1]]
            localOptima = copy.deepcopy(local)
            switchTimes += 1
    local +=1


            #switch ump a and  ump b with one 2 games ump







end = ts.time()
processingTime = end - start
improvedObject, d = objective(games, umpMaster)
#print(improvedObject-originalObject)
resultObject.append(improvedObject-originalObject)
#if switchTimes != 0:
    #print(processingTime/switchTimes)
resultTime.append(processingTime)
#print(localOptima)
localSteps.append(localOptima)
print('--------umpires---------')
print(umpMaster)
print('--------games---------')
print(games)

