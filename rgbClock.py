#!/usr/bin/env python3

"""
Trilby Time 2019 copyright
Module: matrixClock
"""

from samplebase import SampleBase
from rgbmatrix import graphics

import time
import requests
import json
import math

import Colours


class GraphicsTest(SampleBase):
    __panelHeight = 32
    __panelWidth = 64
    
    __restHost = "http://192.168.86.240:5000"
    #__restHost = "http://tankControl:5000"
    __restGraphData = "getWeatherGraph64"
    __restSunrise = "sunriseTime"
    __restSunset = "sunsetTime"
    __restIsSunrise = "IsSunrise"
    __restIsSunset = "IsSunset"
    __restIsDay = "isDay"
    __restGetWeatherDirection = "getWeatherDirection"
    __restGetWindSpeed = "getWindSpeed"
    __restGetWeatherName = "getWeatherName"
    
    __restGetClouds = "getClouds"
    __restGetRain = "getRain"
    __restGetHumidity = "getHumidity"
    __restGetPressure = "getPressure"
    __restGetSunrise_time = "getSunrise_time"
    __restGetSunset_time = "getSunset_time"
    
    __isDay = False
    
    __lastSeconds = "0"
    __lastMinutes = "0"
    __lastMinutesSample = "0"
    __lastHours = "0"
    __seconds = time.strftime("%S", time.localtime())
    __minutes = time.strftime("%M", time.localtime())
    __hours = time.strftime("%H", time.localtime())

    __sampleMinutes = [1, 16, 31, 46]

    __samples = __panelWidth #32
    __gData = [0. for x in range(0, __samples)]
    __gTop = 31

    __max = 0
    __min = 0
    __currentTemp = 0
    __windDirection = 0
    __windSpeed = 0
    
    __clouds = 0
    __rain = 0
    __humidity = 0
    __pressure = 0
    __sunrise_time = 0
    __sunset_time = 0
    
    # Draw pressure
    # https://sciencing.com/range-barometric-pressure-5505227.html
    #
    # Standard air pressure at sea level is 1013.25 mb. 
    # The highest air pressure recorded was 1084 mb in Siberia.
    # The lowest air pressure, 870 mb, was recorded in a typhoon in the Pacific Ocean.
    __siberia = 1082
    __typhoon = 870

    __firstRun = True

    __canvas = 0
    __brightnessNight = 25 
    __brightnessDay = 50
    __brightness = __brightnessNight
    
    __font = graphics.Font()
    __font.LoadFont("./fonts/tom-thumb.bdf")
    __fontHeight = 5
    __fontWidth = 4
    __clearDisplay = True
    
    # Anim pointers
    __animSunStep = 0
    __animTotal = 20

    # Images
    __imagePath = "./images/"
    __currWeather = ""
    __lastWeather = ""
    __weatherName = ""
    __weatherSymbol = []

    def __init__(self, *args, **kwargs):

        super(GraphicsTest, self).__init__(*args, **kwargs)


    def getRestData(self, urlPath):
        resthost = self.__restHost + "/" + urlPath# + "/"
        returnstring = ''

        response = requests.get(resthost)
        returnstring = response.text
        response.close()

        returnstring = returnstring.replace('\"', '')
        
        return returnstring


    def displayTime(self, x, y, dispTime,  dispColour):
        graphics.DrawText(self.offscreen_canvas, self.__font, x, y, dispColour, time.strftime("%H:%M:%S", dispTime))


    def drawDataBoarder(self,  centerX,  centerY,  squareSize, dispColour, drawTop=True, drawBottom=True, drawLeft=True, drawRight=False):
        # Draw border lines
        if drawTop:
            graphics.DrawLine(self.offscreen_canvas, centerX - squareSize, centerY - squareSize, centerX + squareSize, centerY - squareSize, dispColour) # top
        
        if drawBottom:
            graphics.DrawLine(self.offscreen_canvas, centerX - squareSize, centerY + squareSize, centerX + squareSize, centerY + squareSize, dispColour) # bottom
        
        if drawLeft:
            graphics.DrawLine(self.offscreen_canvas, centerX - squareSize, centerY - squareSize, centerX - squareSize, centerY + squareSize, dispColour) # left
        
        if drawRight:
            graphics.DrawLine(self.offscreen_canvas, centerX + squareSize, centerY - squareSize, centerX + squareSize, centerY + squareSize, dispColour) # right
        
        # Draw black corners
        graphics.DrawLine(self.offscreen_canvas, centerX - squareSize, centerY - squareSize, centerX - squareSize, centerY - squareSize, Colours.Black)
        graphics.DrawLine(self.offscreen_canvas, centerX + squareSize, centerY - squareSize, centerX + squareSize, centerY - squareSize, Colours.Black)
        graphics.DrawLine(self.offscreen_canvas, centerX - squareSize, centerY + squareSize, centerX - squareSize, centerY + squareSize, Colours.Black)
        graphics.DrawLine(self.offscreen_canvas, centerX + squareSize, centerY + squareSize, centerX + squareSize, centerY + squareSize, Colours.Black)


    def displayTemp(self, centerX, centerY, currTemp, minTemp,  maxTemp,  dispColour):
        dispColour =self.getColourTemp(float(currTemp))
        
        #Draw border
        squareSize = 6
        
        self.drawDataBoarder(centerX,  centerY,  squareSize,  dispColour)
        
        #Draw text
        centerX -= 3
        centerY += 3
        
        dispString = "%2.0f" % (float(currTemp))
        dispString = dispString.strip()
        
        
        if len(dispString) == 1:
            charWidth = -2
        elif len(dispString) == 2:
            charWidth = 0
        else:
            if int(dispString) == 11:
                charWidth  = 0
            else:
                charWidth  = 1
        
        graphics.DrawText(self.offscreen_canvas, self.__font, centerX - charWidth, centerY, dispColour, dispString)


    def getColourTemp(self, temp):
        # Graph colour
        
        if temp < 0.0:
            return Colours.White
        elif temp >= 0.0 and temp < 5.0:
            return Colours.Blue
        elif temp >= 5.0 and temp < 10.0:
            return Colours.MidBlue
        elif temp >= 10.0 and temp < 15.0:
            return Colours.Cyan
        elif temp >= 15.0 and temp < 20.0:
            return Colours.Green
        elif temp >= 20.0 and temp < 25.0:
            return Colours.Yellow
        elif temp >= 25.0 and temp < 30.0:
            return Colours.Coral
        elif temp >= 30.0:
            return Colours.Red

    def animCorner(self):
        animColour = Colours.Red
        x = (self.__panelWidth - self.__animTotal) + self.__animStep
        
        graphics.DrawLine(self.offscreen_canvas, x, 0, x,  10, animColour)
        
        self.__animStep += 1
        if self.__animStep > self.__animTotal:
            self.__animStep = 0

    def windDirection(self, centerX, centerY, windPointer,  windSpeed,  handLength,  handColour):
        circleRadius = 5
        arrowHeadSize = 10
        
        windPointer = float(windPointer)
        windPointerR = math.radians(windPointer)
        
        sinMult = math.sin(windPointerR)
        cosMult = math.cos(windPointerR)
        
        graphics.DrawCircle(self.offscreen_canvas, centerX, centerY, circleRadius,  handColour)
        graphics.DrawLine(self.offscreen_canvas, centerX + ((sinMult * circleRadius) * 1.1), centerY - ((cosMult * circleRadius) * 1.1), centerX + (sinMult * handLength),  centerY - (cosMult * handLength), handColour)
        
        # Left
        headAngle = windPointer - arrowHeadSize
        if headAngle > 360:
            headAngle += 360
        
        sinMultL = math.sin(math.radians(headAngle))
        cosMultL = math.cos(math.radians(headAngle))
        
        graphics.DrawLine(self.offscreen_canvas, centerX + (sinMultL * (handLength - 1)),  centerY - (cosMultL * (handLength - 1)), centerX + (sinMult * handLength),  centerY - (cosMult * handLength), handColour)
        
        # Right
        headAngle = windPointer + arrowHeadSize
        if headAngle > 360:
            headAngle -= 360
        
        sinMultR = math.sin(math.radians(headAngle))
        cosMultR = math.cos(math.radians(headAngle))
        
        graphics.DrawLine(self.offscreen_canvas, centerX + (sinMultR * (handLength - 1)),  centerY - (cosMultR * (handLength - 1)), centerX + (sinMult * handLength),  centerY - (cosMult * handLength), handColour)
        
        dispString = "%2.0f" % (float(windSpeed))
        
        if float(windSpeed) < 10:
            charWidth = 2
        else:
            charWidth  = 0
        
        graphics.DrawText(self.offscreen_canvas, self.__font, (centerX - 3) - charWidth, centerY + 3, handColour, dispString)
    
    def drawWindDirection(self, centerX, centerY, windPointer,  windSpeed,  handLength,  dispColour):
        arrowHeadSize = 1
        squareSize = 6
        
        windPointer = float(windPointer)
        windPointerR = math.radians(windPointer)
        
        sinMult = math.sin(windPointerR)
        cosMult = math.cos(windPointerR)
        
        self.drawDataBoarder(centerX,  centerY,  squareSize,  dispColour)
        
        graphics.DrawLine(self.offscreen_canvas, centerX, centerY, centerX + (sinMult * handLength),  centerY - (cosMult * handLength), dispColour)
        
        # Left
        headAngle = windPointer - arrowHeadSize
        if headAngle > 360:
            headAngle += 360
        
        sinMultL = math.sin(math.radians(headAngle))
        cosMultL = math.cos(math.radians(headAngle))
        
        graphics.DrawLine(self.offscreen_canvas, centerX + (sinMultL * (handLength)),  centerY - (cosMultL * (handLength)), centerX + (sinMult * handLength),  centerY - (cosMult * handLength), dispColour)
        
        # Right
        headAngle = windPointer + arrowHeadSize
        if headAngle > 360:
            headAngle -= 360
        
        sinMultR = math.sin(math.radians(headAngle))
        cosMultR = math.cos(math.radians(headAngle))
        
        graphics.DrawLine(self.offscreen_canvas, centerX + (sinMultR * (handLength)),  centerY - (cosMultR * (handLength)), centerX + (sinMult * handLength),  centerY - (cosMult * handLength), dispColour)
    
    def drawWindDirBig(self, centerX, centerY, windPointer,  windSpeed,  handLength,  dispColour):
        squareSize = 6
        
        windPointer = float(windPointer)
        windPointerR = math.radians(windPointer)
        
        sinMult = math.sin(windPointerR)
        cosMult = math.cos(windPointerR)
        
        self.drawDataBoarder(centerX,  centerY,  squareSize,  dispColour)
        
        # Left
        headAngle = windPointer + 135
        if headAngle > 360:
            headAngle -= 360
        
        sinMultL = math.sin(math.radians(headAngle))
        cosMultL = math.cos(math.radians(headAngle))
        
        graphics.DrawLine(self.offscreen_canvas, centerX + (sinMultL * (handLength - 1)),  centerY - (cosMultL * (handLength - 1)), centerX + (sinMult * handLength),  centerY - (cosMult * handLength), dispColour)
        
        # Right
        headAngle = windPointer + 225
        if headAngle > 360:
            headAngle -= 360
        
        sinMultR = math.sin(math.radians(headAngle))
        cosMultR = math.cos(math.radians(headAngle))
        
        graphics.DrawLine(self.offscreen_canvas, centerX + (sinMultR * (handLength - 1)),  centerY - (cosMultR * (handLength - 1)), centerX + (sinMult * handLength),  centerY - (cosMult * handLength), dispColour)
        
        #Back bar
        graphics.DrawLine(self.offscreen_canvas, centerX + (sinMultL * (handLength - 1)),  centerY - (cosMultL * (handLength - 1)), centerX + (sinMultR * (handLength - 1)),  centerY - (cosMultR * (handLength - 1)), dispColour)
    
    def drawWindSpeed(self, centerX, centerY, windPointer,  windSpeed,  handLength,  dispColour):
        squareSize = 6
        windSpeed = float(windSpeed) * 2.237
        
        self.drawDataBoarder(centerX,  centerY,  squareSize,  dispColour)
        
        dispString = "%2.0f" % (float(windSpeed))
        
        if round(windSpeed) == 11:
            charWidth = 1
        elif float(windSpeed) < 10:
            charWidth = 2
        else:
            charWidth  = 0
        
        graphics.DrawText(self.offscreen_canvas, self.__font, (centerX - 3) - charWidth, centerY + 3, dispColour, dispString)
    
    
    
    def getWeatherData(self):
        self.__gData = self.getRestData(self.__restGraphData)
        self.__jData = json.loads(self.__gData)

        # Get __min and __max
        self.__min = 100
        self.__max = 0

        sample = 0
        for column in self.__jData:
            
            if column < self.__min:
                self.__min = column

            if column > self.__max:
                self.__max = column

            sample += 1
        
        self.__clouds = float(self.getRestData(self.__restGetClouds))
        self.__rain = float(self.getRestData(self.__restGetRain))
        self.__humidity = float(self.getRestData(self.__restGetHumidity))
        self.__pressure = float(self.getRestData(self.__restGetPressure))
        self.__sunrise_time = float(self.getRestData(self.__restGetSunrise_time))
        self.__sunset_time = float(self.getRestData(self.__restGetSunset_time))
    
    def drawWeatherData(self, gHeight):
        # Graph body
        sample = self.__samples - 1
        for column in self.__jData:
            bar = round((self.__gTop) - (gHeight / (self.__max - self.__min)) * (column - self.__min))
            graphics.DrawLine(self.offscreen_canvas, sample, self.__gTop - 1, sample, bar, self.getColourTemp(column))
            sample -= 1

        self.__currentTemp = self.__jData[0]

        # Graph border
        graphBorderColour = Colours.Red
        
        graphics.DrawLine(self.offscreen_canvas, 0, self.__panelHeight - 1, self.__panelWidth - 1, self.__panelHeight - 1, graphBorderColour)
        graphics.DrawLine(self.offscreen_canvas, 0, self.__gTop - gHeight, self.__panelWidth - 1, self.__gTop - gHeight, graphBorderColour)
        
        # Hour markers
        graphBorderHourMarkColour = Colours.White

        for markX in range(self.__panelWidth,  0,  -4):
            markX -= 1

            graphics.DrawLine(self.offscreen_canvas, markX, self.__gTop, markX,  self.__gTop, graphBorderHourMarkColour)
            graphics.DrawLine(self.offscreen_canvas, markX, self.__gTop - gHeight, markX,  self.__gTop - gHeight, graphBorderHourMarkColour)
        # ******************
        
    def drawDayNight(self, centerX, centerY, isDay):
        dayNightColour = Colours.Black
        squareSize=6
        
        if isDay == 1:
            dayNightColour = Colours.Yellow
        else:
            dayNightColour = Colours.Gray
        
        self.drawDataBoarder(centerX,  centerY,  squareSize,  dispColour=dayNightColour, drawRight=True)
        
        graphics.DrawLine(self.offscreen_canvas, centerX - 1,  centerY - 1,  centerX + 1, centerY + 1, dayNightColour)
        graphics.DrawLine(self.offscreen_canvas, centerX - 1,  centerY + 1,  centerX + 1, centerY - 1, dayNightColour)
        
        for r in range(0, 3):
            graphics.DrawCircle(self.offscreen_canvas, centerX, centerY, r,  dayNightColour)
        
        if isDay == 1:
            # Sun twinkles
            twinkleSize=4
            
            self.__animSunStep += 5
            start = 0 - self.__animSunStep
            end = 359 - self.__animSunStep
            
            if start < -359:
                self.__animSunStep = 0
                start = 0
                end  = 359
            
            for twinkle in range(start,  end, int(360/8)):
                sinMultR = math.sin(math.radians(twinkle))
                cosMultR = math.cos(math.radians(twinkle))
                
                graphics.DrawLine(self.offscreen_canvas, centerX + (twinkleSize * sinMultR),  centerY + (twinkleSize * cosMultR), centerX + (twinkleSize * sinMultR),  centerY + (twinkleSize * cosMultR), Colours.Yellow)


    def weatherLookup(self,  weather):
        weather = weather.lower()
        weather = weather.strip()
        
        if weather in ["", "clear",  "mist",  "clear sky"]: # Clear
            return "clear"
        elif weather in ["scattered Clouds",  "overcast clouds",  "mostly cloudy",  "overcast",  "partly cloudy",  "scattered clouds",  "few clouds",  "broken clouds"]: # Clouds
            return "cloud"
        elif weather in ["fog",  "light fog",  "patches of fog",  "shallow fog"]: # Fog
            return "fog"
        elif weather in ["haze"]: # Haze
            return "haze"

        elif weather in ["light freezing rain"]: # Freezing rain
            return "rainfreezing"
        elif weather in ["heavy intensity rain",  "very heavy rain",  "heavy rain"]: # Heavy rain
            return "rainheavy"
        elif weather in ["rain showers", "light drizzle", "light rain", "light rain showers",  "shower rain",  "light intensity shower rain",  "light intensity drizzle rain",  "drizzle",  "light intensity drizzle", "drizzle rain"]: # Rain
            return "rainlight"
        elif weather in ["rain"]: # Moderate rain
            return "rain"
        elif weather in ["moderate rain"]: # Moderate rain
            return "rainmoderate"
        elif weather in ["heavy snow showers",  "heavy snow grains"]: # Heavy snow
            return "snowheavy"
        elif weather in ["light snow showers",  "light snow", "light snow grains"]: # Light snow
            return "snowlight"
        elif weather in ["snow"]: # Snow
            return "snow"
        elif weather in ["moderate snow"]: # Moderate snow
            return "snowmoderate"
        elif weather in ["thunderstorm"]: # Thunderstorm'
            return "thunderstorm"
        else:
            return "wtf"
    
    def drawWeatherSymbol(self, centerX, centerY, weather, dispColour):
        squareSize = 6
        imageWidth = 11
        imageHeight = 11
        imageXoffset = (centerX - squareSize) + 1
        imageYoffset = (centerY - squareSize) + 1
        imagePointer = 0
        pixelColour = dispColour
        
        self.__currWeather = weather
        
        if self.__lastWeather != self.__currWeather:
            
            lookupWeather = self.weatherLookup(weather)
            filename = self.__imagePath + lookupWeather + ".csv"
            self.__weatherSymbol = []
            
            weatherfile = open(filename, "r")
        
            for imageRow in weatherfile:
                #__weatherSymbol
                imageRow = imageRow.replace("\n", "")
                
                self.__weatherSymbol += imageRow.split(",")
            
            self.__lastWeather = self.__currWeather
        
        self.drawDataBoarder(centerX, centerY, squareSize, dispColour)
        
        for y in range(0, imageWidth):
            for x in range(0, imageHeight):
                pixelColour = Colours.Colour[int(self.__weatherSymbol[imagePointer])]
                
                graphics.DrawLine(self.offscreen_canvas, imageXoffset + x,  imageYoffset + y, imageXoffset + x, imageYoffset + y, pixelColour)
                
                imagePointer += 1
    
    def drawPercentH(self, centerX, centerY, percent, scale, dispColour):
        percent = int(percent / 10)
        scale = int(scale/2)
        
        graphics.DrawLine(self.offscreen_canvas, centerX - (scale + 1), centerY, centerX - (scale + 1),  centerY + 1, Colours.White)
        graphics.DrawLine(self.offscreen_canvas, centerX + scale, centerY, centerX + scale,  centerY + 1, Colours.White)
        graphics.DrawLine(self.offscreen_canvas, centerX - (scale + 1), centerY + 1, centerX + scale,  centerY + 1, dispColour)
        
        graphics.DrawLine(self.offscreen_canvas, centerX + (-(scale + 1) + percent), centerY, centerX + (-(scale + 1) + percent),  centerY + 1, dispColour)

    def drawPercentV(self, centerX, centerY, percent, scale,  low,  high, dispColour):
        
        high -= low
        percent -= low
        low = 0
        
        percent = int((scale / high) * percent)
        
        scale = int(scale / 2)
        
        graphics.DrawLine(self.offscreen_canvas, centerX - 1, centerY - scale, centerX + 1,  centerY - scale, Colours.White)
        graphics.DrawLine(self.offscreen_canvas, centerX - 1, centerY + scale, centerX + 1,  centerY + scale, Colours.White)
        graphics.DrawLine(self.offscreen_canvas, centerX, centerY - scale, centerX,  centerY + scale, dispColour)
        
        graphics.DrawLine(self.offscreen_canvas, centerX - 1, (centerY + scale) - percent, centerX + 1,  (centerY + scale) - percent, dispColour)

    def weatherClock(self):
        # Reset matrix canvas
            self.offscreen_canvas.Clear()
            self.offscreen_canvas.brightness = self.__brightness
            
            #*#*#*#*#*#*#*#*#*#*#
            # Data code
            
            # Get current time
            self.__seconds = time.strftime("%S", time.localtime())
            self.__minutes = time.strftime("%M", time.localtime())
            self.__hours = time.strftime("%H", time.localtime())
            
            # Every second
            if (self.__seconds != self.__lastSeconds) or self.__firstRun: 
                self.__clearDisplay = True
                self.__lastSeconds = self.__seconds
            # ******************
            
            # Every minute
            if (self.__minutes != self.__lastMinutes) or self.__firstRun: 
                # Get wind direction and speed
                self.__windDirection = self.getRestData(self.__restGetWeatherDirection)
                self.__windSpeed = self.getRestData(self.__restGetWindSpeed)
                self.__weatherName = self.getRestData(self.__restGetWeatherName)
                # ******************
                
                # Get day and night
                self.__isDay = int(self.getRestData(self.__restIsDay))
                
                if self.__isDay == 0:
                    self.__brightness = self.__brightnessNight
                    print("Night")
                else:
                    self.__brightness = self.__brightnessDay
                    print("Day")
                # ******************
                
                self.__lastMinutes = self.__minutes
            # ******************
            
            # Every sample minute
            if (int(self.__minutes) in self.__sampleMinutes and self.__minutes != self.__lastMinutesSample) or self.__firstRun: 
                # Get weather data
                self.getWeatherData()
                # ******************
                
                self.__lastMinutesSample = self.__minutes
            # ******************

            # Every hour
            if (self.__hours != self.__lastHours) or self.__firstRun:                 
                self.__lastHours = self.__hours
            # ******************
            
            #*#*#*#*#*#*#*#*#*#*#
            # Draw code 
            
            # Draw time
            left = 0
            self.displayTime(left, self.__fontHeight, time.localtime(),  Colours.Green)
            # ******************

            # Get the current temp
            left = 6
            self.displayTemp(left, 12, str(self.__currentTemp), str(self.__min),  str(self.__max),  Colours.Green)
            # ******************
            
            # Draw weather symbol
            left += 12
            self.drawWeatherSymbol(left, 12, self.__weatherName, Colours.Green)
            # ******************
            
            # Wind direction
            left += 12
            self.drawWindSpeed(left, 12, self.__windDirection, self.__windSpeed, 4, Colours.White)
            left += 12
            self.drawWindDirBig(left, 12, self.__windDirection, self.__windSpeed, 5, Colours.White)
            # ******************
            
            # Draw night and day
            left += 12
            self.drawDayNight(left, 12, self.__isDay)
            # ******************
            
            # Draw humidity
            self.drawPercentH(38, 0, self.__humidity, 10, Colours.Blue)
            #*******************
            
            # Draw humidity
            self.drawPercentH(38, 3, self.__clouds, 10, Colours.Orange)
            #*******************
            
            # Draw pressure
            self.drawPercentV(62, 9, self.__pressure, 18, self.__typhoon, self.__siberia, Colours.Red)
            #*******************
            
            # Draw graph body
            self.drawWeatherData(gHeight=12)
            # ******************
            #*#*#*#*#*#*#*#*#*#*#
            
            # End of main loop
            # ******************
            self.__firstRun = False

            time.sleep(0.2)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)
    
    def run(self):
        # Let's start here
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

        while True:
            self.weatherClock()


# Main function
if __name__ == "__main__":
    graphics_test = GraphicsTest()
    if (not graphics_test.process()):
        graphics_test.print_help()
