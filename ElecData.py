import pandas as pd
import numpy as np
import csv 
import matplotlib.pyplot as plt
import datetime

from datetime import datetime, timedelta

test = pd.read_csv(r'C:\Elec\nyt_ts.csv')
eevp_source = test['eevp_source']

#set df (dataframe) to table
df = pd.read_csv (r'C:\Elec\nyt_ts.csv')

#print (df)
#print (eevp_source)

#Save column eevp_source to file name eevp_source.csv
#eevp_source.to_csv(r'C:\Elec\eevp_source.csv')

#sort dataframe by vote_share_rep descending
#df.sort_values(by=['vote_share_rep'], inplace=True, ascending=False)

# sort by multiple columns: state and vote_share_rep

temp_table = df.sort_values(by=['state','timestamp'])

#get rightmost 10 char for Date
Date = temp_table['timestamp'].str[:10]

my_string=temp_table['timestamp']
#print (my_string.str.split("T",1))

#add columns with split date/time ---'expand=True argument expands data across 2 columns
#temp_table[['Date_Split','Time_Split']] = temp_table.timestamp.str.split("T",1,expand=True)
#_______________SPlit time stamp field by "T" convert formats of time and date and concatenate
#split Time/Date and assign to 2 arrays, format both to pd.to_datetime
DateTime = temp_table.timestamp.str.split("T",1,expand=True)
Date, Time = DateTime[0], DateTime[1]
Time = Time.str[:-1]     #remove Z off last charachter
#_______________
Date = pd.to_datetime(Date)     # Convert to pandas date/time format
Date_Format = Date.dt.strftime('%m/%d')
Time = pd.to_datetime(Time)
Time_Format = Time.dt.strftime('%H:%M')    #Capitalize H, M, S for time format
print(Time_Format)
Date_Time_Format = (Date_Format + " " + Time_Format)
print(Date_Time_Format)

#______________convert timestamp to pd_to_datetime and subtract 4 hours for EST  (previous string converts not needed)
Convert_Time = pd.to_datetime(temp_table['timestamp']) - timedelta(hours = 5)

#______________format to m/d H:M
Time_adj = Convert_Time.dt.strftime('%m/%d %H:%M')     #https://www.tutorialspoint.com/python/time_strftime.htm

#insert columns with split date/time
temp_table.insert(loc=6, column='Time_Est', value=Convert_Time)
temp_table.insert(loc=7, column='Date_Split', value=Date_Format)
temp_table.insert(loc=8, column='Time_Split', value=Time_Format)
temp_table.insert(loc=9, column='Date_Time_Format', value=Date_Time_Format)
temp_table.insert(loc=10, column='Time_adj', value=Time_adj)

#perform scalar calculations
Rep_Dem_VoteSplit = temp_table['vote_share_rep'] / (temp_table['vote_share_rep'] \
                    + temp_table['vote_share_dem'])
temp_table['Rep/Dem Vote Split'] = Rep_Dem_VoteSplit

#user np.where for if...then,  shift() defaults to previous row,  diff(1) needs period specified to only return difference of prev row
#if state = state from line above
temp_table['Vote_Batch'] = np.where(temp_table['state'].eq(temp_table['state'].shift()), temp_table['votes'].diff(1), 0)
#.eq can be used on columns or entire dataframe

#replace negative values with zero
temp_table['Vote_Batch'] = np.where(temp_table['Vote_Batch'] < 0, 0, temp_table['Vote_Batch'])

temp_table['Cum_Rep_Votes'] = temp_table['vote_share_rep'] * temp_table['Vote_Batch']

print (temp_table)

#SAVE DATAFRAME
#temp_table.to_csv(r'C:\Elec\temp_table.csv')

#get portion of dataframe based on value of column
#df.loc[df['column_name'].isin(some_values)]

#**********************************************************
Name_State = "texas"

#***********************************************************
state = temp_table.loc[temp_table['state'] == Name_State]
print(state['Time_Est'].index)
ShenaniganStart = pd.to_datetime('2020-11-04 01:00').tz_localize('UTC') #attach a timezone to match with search range timezone
ShenaniganEnd = pd.to_datetime('2020-11-04 07:00').tz_localize('UTC')
#find closest value in range
idx =state['Time_Est'].sub(ShenaniganStart).abs().idxmin()
idx2 =state['Time_Est'].sub(ShenaniganEnd).abs().idxmin()
print(idx)

testvar =state['vote_share_rep'].sub(.6).abs().idxmin()

state_sum = state['Vote_Batch'].sum()

#Build even time series around first and last date/time of sample
First_Date = pd.to_datetime(state['Time_Est'].head(1))
Last_Date = pd.to_datetime(state['Time_Est'].tail(1))

First_Date = First_Date.dt.strftime('%Y-%m-%d %H:%M')  #format to YYYY-M-D H:M
Last_Date =Last_Date.dt.strftime('%Y-%m-%d %H:%M')

First_Date = First_Date.values[0]   #knock off index number, just get value
Last_Date = Last_Date.values[0]

print(First_Date)

#range = pd.date_range('2009-06-01 05:00', '2009-06-30 05:00', freq='1H')
range = pd.date_range(First_Date, Last_Date, periods=len(state['Time_Est']))
#t_index = pd.DatetimeIndex(pd.date_range(start='2009-06-01', end='2009-06-30'), freq="1h")

print(range)
#Dual Y axis plot attempt #1
#plt.tight_layout()


ax = state.plot(kind='line', x='Time_adj', y='Rep/Dem Vote Split', color='blue', style='.', \
    legend=False, rot=45, figsize=(10,7))
ax2 = state.plot(kind='bar', x='Time_adj', y='votes', color='red', secondary_y=True, \
    ax = ax.twinx(), rot =45, alpha = .2, width = 1, legend=False, figsize=(10,7))   #alpha = transparency
ax3 = state.plot(kind='line', x='Time_adj', y='votes2016', color='green', secondary_y=True, \
    ax = ax2, linewidth=2, alpha = 1,  linestyle = ":") 
ax4 = state.plot(kind='line', x='Time_adj', y='votes2012', color='purple', secondary_y=True, \
    ax = ax2, linewidth=2, alpha = 1, linestyle = ":")  
ax.axvline(idx-state.head(1).index, color='black', linestyle='-', lw=.5, alpha = .5)    # take index number minus first index number of 'state'
ax.axvline(idx2-state.head(1).index, color='black', linestyle='-', lw=.5, alpha = .5)    # take index number minus first index number of 'state'

ax3.legend(frameon=False)
ax2.legend(["Total Votes 2016", "Total Votes 2012", "Cumulative Votes 2020"], loc="upper left")
print(state)

plt.title(Name_State)
#ax.set_xticklabels(ax, fontsize=8)

#ax.grid(axis='y',b=True, which='both', color='0.65')
# Major ticks every 20, minor ticks every 5
major_ticks = np.arange(.25, .75, .25)
minor_ticks = np.arange(.25, .75, .1)
ax.set_yticks(major_ticks)
ax.set_yticks(minor_ticks, minor=True)
ax.grid(axis='y', which='major', alpha =.75 , linestyle='-', color='0.25')
ax.grid(axis='y', which='minor', alpha = .25, linestyle='--', color='0.65')

ax.set_ylabel('% Trump/Biden', color='b')
ax2.set_ylabel('Total # Votes (MM)', color='r')
ax.set_xlabel('Time EST')

#ax.yaxis.set_major_locator(.1)
#ax.yaxis.set_major_locator(plt.MaxNLocator(6)) #manually set number of ticks across y axis
ax2.xaxis.set_major_locator(plt.MaxNLocator(20)) 

ax.tick_params(axis="x", labelsize=8)

bob = ax.legend()
# ax.legend(loc=0)
print(state_sum)
plt.show()


