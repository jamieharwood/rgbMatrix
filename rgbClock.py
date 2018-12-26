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


class GraphicsTest(SampleBase):
    #__red = graphics.Color(255, 0, 0)
    #__green = graphics.Color(0, 255, 0)
    #__blue = graphics.Color(0, 0, 255)
    
    __restHost = "http://192.168.86.240:5000"

    __lastSeconds = "0"
    __lastMinutes = "0"
    __seconds = time.strftime("%S", time.localtime())
    __minutes = time.strftime("%M", time.localtime())

    __sampleMinutes = [0, 15, 30, 45]

    __samples = 32
    __gData = [0. for x in range(0, __samples)]

    def __init__(self, *args, **kwargs):
        super(GraphicsTest, self).__init__(*args, **kwargs)

    def getgraphdata():
        global __restHost
        #print('def getgraphdata():')

        resthost = __restHost + "/getWeatherGraph/"
        returnstring = ''

        # print(resthost)

        response = requests.get(resthost)
        returnstring = response.text
        response.close()

        returnstring = returnstring.replace('\"', '')

        print(returnstring)
        return returnstring


    def displayTime(dispTime):

        print(time.strftime("%H:%M:%S", dispTime))


    def run(self):
        global __lastSeconds,  __lastMinutes,  __sampleMinutes,  __firstRun
        #canvas = self.matrix
        #font = graphics.Font()
        #font.LoadFont("../../../fonts/7x13.bdf")
        
        while True:
            __seconds = time.strftime("%S", time.localtime())
            __minutes = time.strftime("%M", time.localtime())

            if (__seconds != __lastSeconds) or __firstRun: # Every second
                self.displayTime(time.localtime())

                __lastSeconds = __seconds

            if (int(__minutes) in __sampleMinutes and __minutes != __lastMinutes) or __firstRun: # Every sample minute
                __gData = self.getgraphdata()

                __jData = json.loads(__gData)
                
                pointer = 0
                for sample in __jData:
                    if pointer == 0:
                        print("Current temp: ", sample)
                    else:
                        print("Previous: ",  sample)
                    
                    pointer += 1
                
                __lastMinutes = __minutes
            
            __firstRun = False


# Main function
if __name__ == "__main__":
    graphics_test = GraphicsTest()
    if (not graphics_test.process()):
        graphics_test.print_help()
