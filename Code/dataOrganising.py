import numpy as np
import pandas as pd
import datetime as dt


games = pd.read_excel('Data/Round4_LP.xlsx', engine='openpyxl')
games = games.rename(columns={"Unnamed: 8": "Field.2"})
games["Field"] = np.nan
games["Field.1"] = np.nan
games["Field.2"] = np.nan
games["Boundary"] = np.nan
games["Boundary.1"] = np.nan

umps = pd.read_excel('Data/LP_Umps2021.xlsx', engine='openpyxl')
availability = pd.read_excel('Data/LP_Umps2021.xlsx', sheet_name="Availability",
                             usecols="A,E", nrows=118, engine="openpyxl")
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
            dt.time(13,0), dt.time(14,30), dt.time(15,0)]
playAllow = {
    dt.time(8,30): [dt.time(11,0), dt.time(11,30), 
            dt.time(13,0), dt.time(14,30), dt.time(15,0)],
    dt.time(10,0): [dt.time(13,0), dt.time(14,30), 
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

        if type(playtime) != type(np.nan):
            times = playAllow[playtime]
        else:
            times = allTimes     
        umpAvail.loc[entry][0] = times
    else: # add their available time
        playtime = playingUmps.loc[entry][0]

        if type(playtime) != type(np.nan):
            times = playAllow[playtime]
        else:
            times = allTimes
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
        newrow.loc[entry][0] = allTimes
        umpAvail = pd.concat([umpAvail, newrow])

umpAvail = umpAvail.sort_index()    
umpMaster = umpMaster.sort_index()  

for entry in umpAvail.index:
    avail = umpAvail.loc[entry][0]
    if type(avail) == type(np.nan):
        umpAvail.loc[entry][0] = allTimes

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
umpAvail.loc["Boulter, Oscar"][0] = allTimes
umpAvail.loc["Collopy, John"][0] = allTimes[:-1]
umpMaster.loc["Lee, Andrew"]["2 Games"] = False
umpAvail.loc["Stacey, Joshua"][0] = [dt.time(13,0), dt.time(15,0)]

# changes from 'Additional Notes'
umpAvail.loc["Anderson, Callum"][0] = [dt.time(13,0), dt.time(15,0)]
umpAvail.loc["Brown, Henry"][0] = [dt.time(13,0), dt.time(15,0)]
umpAvail.loc["Dodds, Matthew"][0] = dt.time(15,0)
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