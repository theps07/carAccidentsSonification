#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 09:12:54 2021

Using pandas to read and manipulate data. 
Data to sound translations:
    1. Duration of sample playback is mapped to duration of the crash and duration of LPF filter sweep. (longer crash time=longer duration)
    2. Filter cutoff is mapped to the weather condition, (Clear=lowest, Thunder=highest).
    3. Duration of LPF sweep is mapped to distance of the crash. (greater distance=longer attack time)
    4. Reverb gain of inst i99 is mapped to sun position. (Daylight=no reverb, night=reverb).
    5. Pan position of sample is mapped to side of the crash. (Left pan=left side crash)
    6. Pitch of the sample is mapped to severity (higher severity=higher pitch)
    
Soundfont:
    The current soundfont being used is a wood hit. 
    The sharp transient and short duration help illustrate the duration, attack time and reverb gain pfield
    Sounds can be swapped easily by changing filename in line 193
    
@author: puruboii
"""

"""Score Generation"""
#libraries
import pandas as pd
from datetime import datetime, date
from math import sin, cos, sqrt, atan2, radians
import numpy as np

#file
cA = pd.read_csv('carAccidents_SD_reduced.csv') 

#Functions

#function to generate pfield's of constant values
def constPField(data, pField, value): #function to generate pfield's of constant values
    emptyList = []
    for i in data.index:
        emptyList.append(value)
    data[pField] = emptyList
    return data[pField]

#function to convert date to datetime and substract them to find elapsed time
def timePField(data, column1, column2, pField, scale=1): #function to convert date to datetime and substract them to find elapsed time
    emptyList = []
    for i in data.index:
        startTime = datetime.strptime(data[column1][i], '%m/%d/%Y %H:%M' )
        endTime = datetime.strptime(data[column2][i], '%m/%d/%Y %H:%M' )
        et = endTime - startTime
        emptyList.append(et.total_seconds())
    data['Elapsed_Time'] = emptyList
    data[pField] = np.log(data['Elapsed_Time']) / scale #logarithmic scaling
    #data[pField] = ((data['Elapsed_Time'] - data['Elapsed_Time'].min()) / (data['Elapsed_Time'].max() - data['Elapsed_Time'].min())) * scale #normalize
    return data[pField]

#function to assign values to weather data
def weatherPField(data, column, pField, scale=1): 
    emptyList = []
    for value in data[column]:
        if value == 'Clear' or value == 'Clear / Windy' or  value == 'Fair' or value == 'Fair / Windy':
            emptyList.append(float('10000') * scale)
        elif value == 'Fog' or value == 'Fog / Windy':
            emptyList.append(float('12000') * scale)
        elif value == 'Light Rain' or value == 'Light Rain / Windy':
            emptyList.append(float('14000') * scale)
        elif value == 'Light Snow' or value == 'Light Snow / Windy' or  value == 'Snow' or value == 'Snow / Windy':
            emptyList.append(float('18000') * scale)
        elif value == 'Thunder' or value == 'Thunder / Windy':
            emptyList.append(float('20000') * scale)
        else:
            emptyList.append(float('16000') * scale)
        
    data[pField] = emptyList
    return data[pField]

#function that utilizes the haversite formula to calculate the distance between two coordinates
def distPField(data, sLat, sLng, eLat, eLng, pField, scale=1): 
    emptyList = []
    for i in data.index:
        R = 6373.0 # approximate radius of earth in km
        lat1 = radians(data[sLat][i])
        lon1 = radians(data[sLng][i])
        lat2 = radians(data[eLat][i])
        lon2 = radians(data[eLng][i])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        dist = R * c
        emptyList.append(dist)
    data['Dist'] = emptyList
    data['Dist2'] = (data['Dist'] +0.002) * 1000 #correct for zero data values and scale to avoid negatives
    data[pField] = np.log(data['Dist2']) / scale
   #data[pField] = ((data['Dist'] - data['Dist'].min()) / (data['Dist'].max() - data['Dist'].min())) * scale #normalize #normalize
    return data[pField]

#function to assign values to Sunrise/Sunset data
def sunPosPField(data, column, pField):
    emptyList = []
    for value in data[column]:
        if value == 'D':
            emptyList.append(float('0'))
        else:
            emptyList.append(float('0.2'))
    data[pField] = emptyList
    return data[pField]

#function to assign values to side data
def sidePField(data, column, pField):
    emptyList = []
    for value in data[column]:
        if value == 'R':
            emptyList.append(int('0'))
        else:
            emptyList.append(int('1'))
    data[pField] = emptyList
    return data[pField]

#function that assigns samples to severity
def severityPField(data, column, pField):
    emptyList = []
    for value in data[column]:
        if value == 2:
            emptyList.append(float('3'))
        elif value == 3:
            emptyList.append(float('4'))
        elif value == 4:
            emptyList.append(float('5'))
    data[pField] = emptyList
    return data[pField]

#function for start time
def counterPField(data, pField, scale):
    emptyList = []
    for i in data.index:
        value = i * scale
        emptyList.append(value)
    data[pField] = emptyList
    return data[pField]





#Creating pfields:

#i9
constPField(cA, 'p1', 'i9') #p1(Inst No.)
counterPField(cA, 'p2', 0.25) #p2(start time)
timePField(cA, 'Start_Time', 'End_Time', 'p3', 40) #p3(idur) = Duration of crash
constPField(cA, 'p4', 0.3) #p4(iamp) = Constant
constPField(cA, 'p5', 0) #p5(skip time)
constPField(cA, 'p6', 0.01) #p6(iattack) = Constant
constPField(cA, 'p7', 0.1) #p7(irelease) 
sunPosPField(cA, 'Sunrise_Sunset', 'p8') #p8(irvbgain) = Sunrise/Sunset
sidePField(cA, 'Side', 'p9') #p9(ibalance) = Side of the accident
severityPField(cA, 'Severity', 'p10') #p10(ipitch) = Severity of the accident
weatherPField(cA, 'Weather_Condition', 'p11', 1) #p11(ifreq1) (filter cutoff) = Weather condition 
distPField(cA, 'Start_Lat', 'Start_Lng', 'End_Lat', 'End_Lng', 'p12', 10) #p12(isweep) = Distance of crash


#i99
scorei99 = "i99 0 50 0.2 \n"

#generates string from list of lists
scorei9 = cA.to_string(columns=['p1','p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12'], header=False, index=False)

#final score, combines instrument i9 and i99
score = scorei99 + scorei9
print(score)  #for testing purposes

#Orchestra for the project 
instrument="""
nchnls    =         2                        ; stereo output

garvbsig  init      0                        ; global "a" variable initialized to 0

          instr 9

idur      =         p3
iamp      =         p4
iskiptime =         p5
iattack   =         p6
irelease  =         p7
ibalance  =         p8                       ; 1 = left, .5 = center, 0 = right
irvbgain  =         p9
ipitch    =         p10
ifreq1    =         p11
isweep    =         p12


kamp      linen     iamp, iattack, idur, irelease
asig      diskin    "sample9.wav", ipitch, iskiptime, 1, 0, 32
asig      =         K35_lpf(asig, expseg:a(ifreq1, isweep/10, 3000), 9, 0, 2)
arampsig  =         kamp * asig
          outs      arampsig * ibalance, arampsig * (1 - ibalance)
garvbsig  =         garvbsig + arampsig * irvbgain
          endin

          instr 99
irvbtime  =         p4
asig      reverb    garvbsig,  irvbtime      ; put global sig into reverb
          outs      asig, asig
garvbsig  =         0                        ; then clear it
          endin
"""


import ctcsound
cs = ctcsound.Csound()       # create an instance of Csound
cs.setOption("-odac")        # Set dac as output option for Csound
cs.compileOrc(instrument)    # Compile the Orchestra from the accidentOrchestra
cs.readScore(score)          # Read in Score from pre-written String

cs.start()   # When compiling to score from strings, this call is necessary before performing

while (cs.performKsmps() == 0):  # The main performance loop perform one block of sound at a time
#  pass         # or continue    # and keep processing while the 'performer' returns 0 
    continue
cs.reset()


...