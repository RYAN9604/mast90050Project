import numpy as np
import pandas as pd
import datetime as dt
import copy
import random


games = pd.read_excel('~/mast90050Project/Code/Data/Round4_LP.xlsx', engine='openpyxl')
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

umps = pd.read_excel('~/mast90050Project/Code/Data/LP_Umps2021.xlsx', engine='openpyxl')
availability = pd.read_excel('~/mast90050Project/Code/Data/LP_Umps2021.xlsx', sheet_name="Availability",
                             usecols="A,E", nrows=118, engine="openpyxl")
playingUmps = pd.read_excel('~/mast90050Project/Code/Data/LP_playing_Rd4.xlsx', usecols="A,D",
                             engine="openpyxl")

umpMaster = umps
umpAvail = availability

umpMaster = umpMaster.set_index("Name")
umpAvail = umpAvail.set_index("Names")
playingUmps = playingUmps.set_index("Name")

#%% Only consider umpires who we have full data for
        
# Assign availability to playing umps        
# Dictionary    playing time : [allowable umpiring times]
allTimes = ['08:30:00', '10:00:00', '11:00:00', '11:30:00',
            '13:00:00', '14:30:00', '15:00:00']
playAllow = {
    '08:30:00': ['11:00:00', '11:30:00',
            '13:00:00', '14:30:00', '15:00:00'],
    '10:00:00': ['13:00:00', '14:30:00',
                          '15:00:00'],
    '11:00:00': ['08:30:00', '14:30:00',
                          '15:00:00'],
    '11:30:00': ['08:30:00', '14:30:00',
                          '15:00:00'],
    '13:00:00': ['08:30:00', '10:00:00'],
    '14:30:00': ['08:30:00', '10:00:00',
                          '11:30:00'],
    '15:00:00': ['08:30:00', '10:00:00',
                          '11:30:00']
    }

for entry in playingUmps.index:
    if entry in umpAvail.index:
        playtime = playingUmps.loc[entry][0]

        if type(playtime) != type(np.nan) and playtime != None:
            playtime = playtime.strftime("%H:%M:%S")
            times = copy.deepcopy(playAllow[playtime])
        else:
            times = copy.deepcopy(allTimes)
        umpAvail.loc[entry][0] = times
    else: # add their available time
        playtime = playingUmps.loc[entry][0]

        if type(playtime) != type(np.nan):
            playtime = playtime.strftime("%H:%M:%S")
            times = copy.deepcopy(playAllow[playtime])
        else:
            times = copy.deepcopy(allTimes)
        newrow = pd.DataFrame(0, index=[entry], columns=[umpAvail.columns[0]],
                              dtype=object)
        newrow.loc[entry][0] = times
        umpAvail = pd.concat([umpAvail, newrow])
        
for entry in umpAvail.index:
    if entry not in umpMaster.index:
        #print(entry)
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
umpMaster = umpMaster[0:120]
umpAvail = umpAvail[0:120]


#print("\n******\n")
#print(np.all(umpMaster.index == umpAvail.index))
#%% Assign umpires to clubs they play for
    
team = [' ' for i in range(umpMaster.shape[0])]
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
umpAvail.loc["Collopy, John"][0] = allTimes[:-1]
umpMaster.loc["Lee, Andrew"]["2 Games"] = False
umpAvail.loc["Stacey, Joshua"][0] = ['13:00:00', '15:00:00']

# changes from 'Additional Notes'
umpAvail.loc["Anderson, Callum"][0] = ['13:00:00', '15:00:00']
umpAvail.loc["Brown, Henry"][0] = ['13:00:00', '15:00:00']
umpAvail.loc["Dodds, Matthew"][0] = ['15:00:00']
umpAvail.loc["Lee, Andrew"][0] = ['10:00:00', '11:30:00']
umpAvail.loc["Scott, Angus"][0] = ['13:00:00', '15:00:00']
umpAvail.loc["Walsh, Austin"][0] = ['13:00:00', '15:00:00']
#%% Remove unavailable umpires
for ump in umpAvail.index:
    if umpAvail.loc[ump][0] == "Unavailable":
        #print(ump)
        umpMaster = umpMaster.drop(ump)
        umpAvail = umpAvail.drop(ump)
#print("\n******\n")
#for ump in playingUmps.index:
#    if ump not in umpMaster.index:
#        print(ump)
#
#print(np.all(umpMaster.index == umpAvail.index))

#%%
umpMaster = pd.concat([umpMaster, umpAvail], axis = 1)
umpMaster = umpMaster.rename(columns = {umpAvail.columns[0]: "Available"})
cols = ["Age Group", "Category", "2 Games", "Available", "Playing", "Club",
        "Additonal Notes", "Last Name", "First Name"]
umpMaster = umpMaster[cols]

for entry in umpMaster.index:
    if umpMaster.loc[entry]['Available'] is None:
        umpMaster.loc[entry]['Available'] = allTimes
#for index in umpMaster.index:
#    print(umpMaster.loc[index]['Available'])
umpMaster.loc['Parker, Cameron']['Available']= ['08:30:00']
#for j in umpMaster.index:
#    print(umpMaster.loc[j]['Club'])
#for i in games.index:
#    print(games.loc[i]['Teams'])

#greedy algorithm:


u = [[] for i in range(games.shape[0])]
v = [[] for i in range(umpMaster.shape[0])]
w = [[] for i in range(umpMaster.shape[0])]
p = [[] for i in range(umpMaster.shape[0])]
games['ump'] = u
umpMaster['game'] = v
umpMaster['working time'] = w
umpMaster['working team'] = p
games.set_index('Venue Name')


#minimize category difference
'''
for i in games.index:
    #team = []
    time = games.loc[i]['Match Time']
    time = str(time)
    Category = games.loc[i]['Category']
    team = games.loc[i]['Teams']
    #team.append(games.loc[i]['Team 1'])
    #team.append(games.loc[i]['Team 2'])
    for j in umpMaster.index:
        if umpMaster.loc[j]['Available'] is not None:
            if time in umpMaster.loc[j]['Available'] and umpMaster.loc[j]['Category'] == Category \
                    and umpMaster.loc[j]['Club'] not in team and len(games.loc[i]['ump']) < 1:
                #print(umpMaster.loc[j]['Available'])
                #print(time)
                umpMaster.loc[j]['Available'].remove(time)
                #print(umpMaster.loc[j]['Available'])
                games.loc[i]['ump'].append(j)
                umpMaster.loc[j]['game'].append(i)

for i in games.index:
    #team = []
    time = games.loc[i]['Match Time']
    time = str(time)
    Category = games.loc[i]['Category']
    team = games.loc[i]['Teams']
    #team.append(games.loc[i]['Team 1'])
    #team.append(games.loc[i]['Team 2'])
    for j in umpMaster.index:
            if time in umpMaster.loc[j]['Available'] and umpMaster.loc[j]['Category'] == Category \
                    and umpMaster.loc[j]['Club'] not in team and len(games.loc[i]['ump']) < 2 \
                    and ((len(umpMaster.loc[j]['game']) < 2  and umpMaster.loc[j]['2 Games']) or (len(umpMaster.loc[j]['game'])<1 and not umpMaster.loc[j]['2 Games'])):
                #print(umpMaster.loc[j]['Available'])
                #print(time)
                umpMaster.loc[j]['Available'].remove(time)
                #print(umpMaster.loc[j]['Available'])
                games.loc[i]['ump'].append(j)
                umpMaster.loc[j]['game'].append(i)
'''
#for index in games.index:
#    print(games.loc[index]['ump'])
#
#    if games.loc[index]['ump'] == []:
#        print(index)
#        print(games.loc[index]['Match Time'])

#for index in umpMaster.index:
#    print(umpMaster.loc[index]['Available'])


#same location
venueSet = games['Venue Name']
venueSet = sorted(set(venueSet))
teamMap = { i : {} for i in venueSet}
cateGoryMap = { j : {} for j in venueSet}
umpNumberMap = {k:{} for k in venueSet}
indexMap = {l:{} for l in venueSet}
timeAvailabel = {m:[]for m in venueSet}
for x in venueSet:
    for i in games.index:
        if games.loc[i]['Venue Name'] == x:
            timeAvailabel[x].append(str(games.loc[i]['Match Time']))
            teamMap[x][str(games.loc[i]['Match Time'])] = games.loc[i]['Teams']
            cateGoryMap[x][str(games.loc[i]['Match Time'])] = games.loc[i]['Category']
            umpNumberMap[x][str(games.loc[i]['Match Time'])] = 0
            indexMap[x][str(games.loc[i]['Match Time'])] = i
for x in venueSet:
    for j in umpMaster.index:
        if len(umpMaster.loc[j]['game']) == 2 or not umpMaster.loc[j]['2 Games']:
            continue
        timeSet = sorted(set(timeAvailabel[x]) & set(umpMaster.loc[j]['Available']))
        if len(timeSet)>=2:
            filterTeamTime = []
            for y in timeSet:
                if x not in teamMap[x][y]:
                    filterTeamTime.append(y)
            if len(filterTeamTime) >= 2 :
                for z in filterTeamTime:
                    if cateGoryMap[x][z] == umpMaster.loc[j]['Category']:
                        games.loc[indexMap[x][z]]['ump'].append(j)
                        umpNumberMap[x][z]+=1
                        if umpNumberMap[x][z] >=2:
                            timeAvailabel[x].remove(z)
                        umpMaster.loc[j]['game'].append(x+z)
                        umpMaster.loc[j]['working time'].append(z)
                        umpMaster.loc[j]['working team']+= teamMap[x][z]
                        filterTeamTime.remove(z)
                        anotherTime = filterTeamTime[0]
                        games.loc[indexMap[x][anotherTime]]['ump'].append(j)
                        umpNumberMap[x][anotherTime]+=1
                        if umpNumberMap[x][anotherTime] >= 2:
                            timeAvailabel[x].remove(anotherTime)
                        umpMaster.loc[j]['game'].append(x + anotherTime)
                        umpMaster.loc[j]['working time'].append(anotherTime)
                        umpMaster.loc[j]['working team'] += teamMap[x][anotherTime]
                        break



for i in games.index:
    #team = []
    time = games.loc[i]['Match Time']
    time = str(time)
    Category = games.loc[i]['Category']
    team = games.loc[i]['Teams']
    #team.append(games.loc[i]['Team 1'])
    #team.append(games.loc[i]['Team 2'])
    for j in umpMaster.index:
            if time in umpMaster.loc[j]['Available'] and abs(ord(umpMaster.loc[j]['Category']) - ord(Category)) <=1 \
                    and umpMaster.loc[j]['Club'] not in team and len(games.loc[i]['ump']) < 2 \
                    and ((len(umpMaster.loc[j]['game']) < 2 and umpMaster.loc[j]['2 Games']) or (len(umpMaster.loc[j]['game'])<1 and not umpMaster.loc[j]['2 Games'])):
                #print(umpMaster.loc[j]['Available'])
                #print(time)
                umpMaster.loc[j]['Available'].remove(time)
                umpMaster.loc[j]['working time'].append(time)
                #print(umpMaster.loc[j]['Available'])
                games.loc[i]['ump'].append(j)
                umpMaster.loc[i]['working team'] += team
                umpMaster.loc[j]['game'].append(i)









#for j in umpMaster.index:
#    for i in games.index:
#        time = games.loc[i]['Match Time']
#        time = str(time)
#        Category = games.loc[i]['Category']
#        team = games.loc[i]['Teams']
#        if time in umpMaster.loc[j]['Available']  \
#            and umpMaster.loc[j]['Club'] not in team \
#            and umpMaster.loc[j]['Category'] == games.loc[i]['Category'] \
#            and umpMaster.loc[j]['2 Games'] \
#            and len(games.loc[i]['ump']) < 1\
#            and len(umpMaster.loc[j]['game']) < 1:
#            umpMaster.loc[j]['Available'].remove(time)
#            games.loc[i]['ump'].append(j)
#            umpMaster.loc[j]['game'].append(i)


#and (umpMaster.loc[j]['game'] == [] or (games.loc[i]['Venue Name'] in umpMaster.loc[j]['game'] and umpMaster.loc[j]['2 Games'] and len(umpMaster.loc[j]['game'])<2))\
#for j in umpMaster.index:
#    for i in games.index:
#        time = games.loc[i]['Match Time']
#        time = str(time)
#        Category = games.loc[i]['Category']
#        team = games.loc[i]['Teams']
#        if time in umpMaster.loc[j]['Available']  \
#            and umpMaster.loc[j]['Club'] not in team \
#            and (games.loc[i]['Venue Name'] in umpMaster.loc[j]['game'] and umpMaster.loc[j]['2 Games'] and len(umpMaster.loc[j]['game'])<2)\
#            and len(games.loc[i]['ump']) < 2:
#            umpMaster.loc[j]['Available'].remove(time)
#            games.loc[i]['ump'].append(j)
#            umpMaster.loc[j]['game'].append(i)

#for index in games.index:
#    print(games.loc[index]['ump'])
#
#
#f = open('/home/mi/mast90050Project/Code/outputForSameLocation.txt', 'a')
#for index in games.index:
#    f.write(str(games.loc[index]['ump']))
#    f.write('\n')


# local step
umpSet = list(umpMaster.index)
a = random.choice(umpSet)
b = a
while b == a:
    b = random.choice(umpSet)
if umpMaster.loc[a]['2 Games'] == umpMaster.loc[b]['2 Games']  \
        and umpMaster.loc[b]['working time'] in umpMaster.loc[a]['Available']\
        and umpMaster.loc[a]['working time'] in umpMaster.loc[b]['Available']\
        and umpMaster.loc[b]['Club'] not in umpMaster.loc[a]['working team']\
        and umpMaster.loc[a]['Club'] not in umpMaster.loc[b]['working team']\
        and :





