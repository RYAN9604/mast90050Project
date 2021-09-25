import numpy as np
import pandas as pd
import datetime as dt
import copy
from collections import defaultdict

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
playingUmps = pd.read_excel('Data/Lp_playing_Rd4.xlsx', usecols="A,D",
                             engine="openpyxl")

umpMaster = umps
umpAvail = availability

umpMaster = umpMaster.set_index("Name")
umpAvail = umpAvail.set_index("Names")
playingUmps = playingUmps.set_index("Name")

#%% Only consider umpires who we have full data for
        
# Assign availability to playing umps        
# Dictionary    playing time : [allowable umpiring times]
allTimes = [dt.time(8,30), dt.time(10,0), dt.time(11,0), dt.time(11,30),
            dt.time(13,0), dt.time(13,30), dt.time(14,30), dt.time(15,0)]
playAllow = {
    dt.time(8,30): [dt.time(11,0), dt.time(11,30), 
            dt.time(13,0), dt.time(13,30), dt.time(14,30), dt.time(15,0)],
    dt.time(10,0): [dt.time(13,0), dt.time(13,30), dt.time(14,30), 
                          dt.time(15,0)],
    dt.time(11,0): [dt.time(8,30), dt.time(14,30), 
                          dt.time(15,0)],
    dt.time(11,30): [dt.time(8,30), dt.time(14,30), 
                          dt.time(15,0)],
    dt.time(13,0): [dt.time(8,30), dt.time(10,0)],
    dt.time(14,30): [dt.time(8,30), dt.time(10,0),
                          dt.time(11,30)],
    dt.time(15,0): [dt.time(8,30), dt.time(10,0),
                          dt.time(11,30)]
    }

for entry in playingUmps.index:
    if entry in umpAvail.index:
        playtime = playingUmps.loc[entry][0]

        if playtime != 'None':
            times = copy.deepcopy(playAllow[playtime])
        else:
            times = copy.deepcopy(allTimes)     
        umpAvail.loc[entry][0] = times
    else: # add their available time
        playtime = playingUmps.loc[entry][0]

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
        print(entry)
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

print("\n******\n")
print(np.all(umpMaster.index == umpAvail.index))
#%% Assign umpires to clubs they play for
    
team = [np.nan for i in range(umpMaster.shape[0])]
umpMaster["Club"] = team

for ump in umpMaster.index:
    t = umpMaster.loc[ump, "Playing"]
    if type(t) == str:
        umpMaster.loc[ump, "Club"] = t.split()[0]
        
#%% Indicate two or one game and manually review special cases
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
umpAvail.loc["Stacey, Joshua"][0] = [dt.time(13,0), dt.time(15,0)]

# changes from 'Additional Notes'
umpAvail.loc["Anderson, Callum"][0] = [dt.time(13,0), dt.time(15,0)]
umpAvail.loc["Brown, Henry"][0] = [dt.time(13,0), dt.time(15,0)]
umpAvail.loc["Dodds, Matthew"][0] = [dt.time(15,0)]
umpAvail.loc["Lee, Andrew"][0] = [dt.time(10,0), dt.time(11,30)]
umpAvail.loc["Scott, Angus"][0] = [dt.time(13,0), dt.time(15,0)]
umpAvail.loc["Walsh, Austin"][0] = [dt.time(13,0), dt.time(15,0)]
#%% Remove unavailable umpires
for ump in umpAvail.index:
    if umpAvail.loc[ump][0] == "Unavailable":
        print(ump)
        umpMaster = umpMaster.drop(ump)
        umpAvail = umpAvail.drop(ump)
print("\n******\n")     
for ump in playingUmps.index:
    if ump not in umpMaster.index:
        print(ump)

print(np.all(umpMaster.index == umpAvail.index))

#%%
umpMaster = pd.concat([umpMaster, umpAvail], axis = 1)
umpMaster = umpMaster.rename(columns = {umpAvail.columns[0]: "Available"})
cols = ["Age Group", "Category", "2 Games", "Available", "Playing", "Club",
        "Additonal Notes", "Last Name", "First Name"]
umpMaster = umpMaster[cols]

#%% 
u = [[] for i in range(games.shape[0])]
v = [[] for i in range(umpMaster.shape[0])]
games['ump'] = u
umpMaster['game'] = v
games.set_index('Venue Name')


#same location

# for j in umpMaster.index:
#     for i in games.index:
#         time = games.loc[i]['Match Time']
#         Category = games.loc[i]['Category']
#         team = games.loc[i]['Teams']
#         if time in umpMaster.loc[j]['Available']  \
#             and umpMaster.loc[j]['Club'] not in team \
#             and (umpMaster.loc[j]['game'] == [] or (i in umpMaster.loc[j]['game'] and umpMaster.loc[j]['2 Games'] and len(umpMaster.loc[j]['game'])<2))\
#             and len(games.loc[i]['ump']) < 1:
#             umpMaster.loc[j]['Available'].remove(time)
#             games.loc[i]['ump'].append(j)
#             umpMaster.loc[j]['game'].append(i)

# for j in umpMaster.index:
#     for i in games.index:
#         time = games.loc[i]['Match Time']
#         Category = games.loc[i]['Category']
#         team = games.loc[i]['Teams']
#         if time in umpMaster.loc[j]['Available']  \
#             and umpMaster.loc[j]['Club'] not in team \
#             and (umpMaster.loc[j]['game'] == [] or (i in umpMaster.loc[j]['game'] and umpMaster.loc[j]['2 Games'] and len(umpMaster.loc[j]['game'])<2))\
#             and len(games.loc[i]['ump']) < 2:
#             umpMaster.loc[j]['Available'].remove(time)
#             games.loc[i]['ump'].append(j)
#             umpMaster.loc[j]['game'].append(i)

#%% OBJECTIVE FUNCTION
example_sched = pd.read_excel('Data/Round4_LP_Example.xlsx', engine='openpyxl')
example_sched = example_sched.rename(columns={"Unnamed: 9": "Field.2"})

def objective(schedule, umpMaster):
    obj = 0
    upCatPenalty = 10
    downCatPenalty = 5
    not2gamesPenalty = 50
    noGamePenalty = 10**5
    TooManyGamesPen = 10**6
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
    
    print('objective =', obj)
    print(ump_numgames)
    for ump in umpMaster.index:
        if ump_numgames[ump] == 0:
            obj += noGamePenalty
        elif umpMaster.loc[ump]["2 Games"] == True and ump_numgames[ump] == 1:
            obj += not2gamesPenalty
        elif umpMaster.loc[ump]["2 Games"] == False and ump_numgames[ump] == 2:
            print(ump)
            obj += TooManyGamesPen

    print('objective =', obj)
    return obj, schedule

a,b = objective(example_sched, umpMaster)