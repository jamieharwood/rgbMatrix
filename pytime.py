#!/usr/bin/env python

"""
Trilby Time 2019 copyright
Module: matrixClock
"""
#from samplebase import SampleBase
#from rgbmatrix import graphics
import time
import requests
import json

__firstRun = True

__restHost = "http://192.168.86.240:5000"

__lastSeconds = "0"
__lastMinutes = "0"
__lastHours = "0"
__seconds = time.strftime("%S", time.localtime())
__minutes = time.strftime("%M", time.localtime())
__hours = time.strftime("%H", time.localtime())

__sampleMinutes = [0, 15, 30, 45]

__samples = 32
__gData = [0. for x in range(0, __samples)]

__max = 0
__min = 0
__currentTemp = 0

def getgraphdata():
    #print('def getgraphdata():')

    resthost = __restHost + "/getWeatherGraph/"
    returnstring = ''

    # print(resthost)

    response = requests.get(resthost)
    returnstring = response.text
    response.close()

    returnstring = returnstring.replace('\"', '')

    #print(returnstring)
    return returnstring


def displayTime(dispTime):

    print(time.strftime("%H:%M:%S", dispTime))


def main():
    global __seconds, __lastSeconds, __minutes, __lastMinutes, __hours, __lastHours, __currentTemp,  __firstRun

    while True:
        __seconds = time.strftime("%S", time.localtime())
        __minutes = time.strftime("%M", time.localtime())
        __hours = time.strftime("%H", time.localtime())
        
        # Every second
        if (__seconds != __lastSeconds) or __firstRun: 
            displayTime(time.localtime())

            __lastSeconds = __seconds
        
        # Every sample minute
        if (int(__minutes) in __sampleMinutes and __minutes != __lastMinutes) or __firstRun: 
            __gData = getgraphdata()
            __jData = json.loads(__gData)
            
            __min = 100
            __max = 0
            
            # ******************
            # Get __min and __max
            sample = 0
            for column in __jData:
                # print(__jData[sample])

                if column < __min:
                    __min = column

                if column > __max:
                    __max = column

                sample += 1
            
            # ******************
            # Draw the bar graph
            sample = __samples - 1
            for column in __jData:
                bar = round(7 - (7 / (__max - __min)) * (column - __min))
                print(sample, 7, sample, bar, 1) # This should draw the line.
                sample -= 1

            # Get the current temp
            __currentTemp = __jData[0]
            
            __lastMinutes = __minutes
            
        # Every hour
        if (__hours != __lastHours) or __firstRun: 
            __lastHours = __hours
        
        __firstRun = False
        
        time.sleep(0.5)

if __name__ == "__main__":
    # execute only if run as a script
    main()
