#!/usr/bin/env python

"""
Trilby Time 2019 copyright
Module: matrixClock
"""

from samplebase import SampleBase
from rgbmatrix import graphics
#import max7219
#from machine import RTC, Pin, SPI
import time
import urequests
import ujson
from timeClass import TimeTank
#from NeoPixelClass import NeoPixel

# Graph
__min = 100
__max = 0
__gOff = 8 * 8
__jData = None
__currentTemp = 0
__graphSample = 32
__gData = [0. for x in range(0, __graphSample)]

class GraphicsTest(SampleBase):
    def __init__(self, *args, **kwargs):
        super(GraphicsTest, self).__init__(*args, **kwargs)

    def getgraphdata():
        print('def getgraphdata():')

        resthost = "http://192.168.86.240:5000/getWeatherGraph/"
        returnstring = ''

        # print(resthost)

        response = urequests.get(resthost)
        returnstring = response.text
        response.close()

        returnstring = returnstring.replace('\"', '')

        # print(returnstring)
        return returnstring

    """def displaytext(display, text, show):
        display.fill(0)
        display.text(text, 0, 0, 1)

        if show:
            display.show()"""

    def run(self):
        canvas = self.matrix
        font = graphics.Font()
        font.LoadFont("./fonts/7x13.bdf")

        __red = graphics.Color(255, 0, 0)
        __green = graphics.Color(0, 255, 0)
        __blue = graphics.Color(0, 0, 255)

        # Init the display time variables
        initLoop = True
        currHour = 0
        lastHour = 0
        hourChanged = False

        currMinute = 0
        lastMinute = 0
        minuteChanged = False

        timeNow = (0 for x in range(0, 8))

        displayTimeNow = ''
        displayTimeLast = ''

        # Set the RTC
        mytime = TimeTank()

        while not mytime.settime():
            pass

        #rtc = RTC()

        while True:
            #timeNow = rtc.datetime()
            currHour = timeNow[4]
            currMinute = timeNow[5]

            if currHour != lastHour:
                #__np.colour(2, 'Green')
                #__np.write()

                while not mytime.settime():
                    pass

                #rtc = RTC()

                #timeNow = rtc.datetime()
                lastHour = currHour
                #local = time.localtime()

                #__np.colour(2, 'Black')
                #__np.write()
                hourChanged = True

            if currMinute != lastMinute:
                lastMinute = currMinute
                minuteChanged = True

            # ************
            # Display time

            if timeNow[4] < 10:
                displayTimeNow = '0{0}{2}{1}'
            else:
                displayTimeNow = '{0}{2}{1}'

            if timeNow[5] < 10:
                displayTimeNow = displayTimeNow.replace('{2}', '0')
            else:
                displayTimeNow = displayTimeNow.replace('{2}', '')

            displayTimeNow = displayTimeNow.replace('{0}', str(timeNow[4]))
            displayTimeNow = displayTimeNow.replace('{1}', str(timeNow[5]))

            if displayTimeNow != displayTimeLast:
                displayTimeLast = displayTimeNow

            #displaytext(__display, str(displayTimeNow), 0)

            # *********************
            # Display seconds pixel

            seconds = timeNow[6]
            if (seconds/2) == round(seconds/2):
                #__display.rect(15, 5, 2, 2, 1)
            else:
                #__display.rect(15, 5, 2, 2, 0)

            # *****************
            # Display the graph

            if initLoop or (currMinute in [1, 16, 31, 46] and minuteChanged):
                __gData = getgraphdata()

            __jData = ujson.loads(__gData)
            __min = 100
            __max = 0

            __gOff = 8 * 8

            #__display.line(__gOff, 0, __gOff, 7, 1)
            #__display.line(__gOff, 7, __gOff + 32, 7, 1)

            # Get min and __max
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
            sample = __graphSample - 1
            for column in __jData:

                bar = round(7 - (7 / (__max - __min)) * (column - __min))

                __display.line(__gOff + sample, 7, __gOff + sample, bar, 1)

                sample -= 1

            __currentTemp = __jData[0]

            # Print current temp
            graphics.DrawText(canvas, font, 2, 10, blue, "__currentTemp")
            __display.text(str(__currentTemp), 32, 0, 1)

            __display.show()

            hourChanged = False
            minuteChanged = False
            initLoop = False

            time.sleep(0.25)


# Main function
if __name__ == "__main__":
    graphics_test = GraphicsTest()
    if (not graphics_test.process()):
        graphics_test.print_help()
