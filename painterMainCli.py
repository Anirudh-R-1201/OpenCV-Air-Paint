import cv2
import numpy as np
import time
from pynput.keyboard import Key, Listener
from fingertracker import fingerTracker
from autocalibration import AutoCalibration
from painthelper import paintHelper
from markertracker import markerTracker

class painterMain:
    def __init__(self):
        self.trackerMode = 1 # 0 - Hand, 1 - Marker
        self.trackerColorMode = 0 # 0 - Average Color, 1 - Histogram Matching (Only for fingers)
        self.markerColorMode = 0 # 0 - Average Color, 1 - Color Palette
        self.paintMode = 0 # 0 - Pen Down, 1 - Pen Up, 2 - Set Color
        self.paintColor = (0, 0, 0) # HSV Marker Color
        self.maxDrawingSpeed = 500 # Pixels/refresh to lower noise
        self.coordinates = [0, 0]
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        self.cali = AutoCalibration(self.cap)
        self.ph = paintHelper()
        self.ft = None
        self.mt = None

    def getTrackerColorAndHist(self, trackerName):
        averageColor, objectHist = self.cali.calibrate(trackerName)
        colorRange = averageColor[1:3]
        return colorRange, objectHist

    def getDrawingColorAverage(self):
        averageColor, objectHist = self.cali.calibrate("Color")
        averageC = (int((240/180)*averageColor[0][0]), int((240/255)*averageColor[0][1]), int((240/255)*averageColor[0][2]))
        return averageC

    def trackFinger(self):
        numFingers, fingers, betas, handContour = self.ft.track(self.trackerColorMode)
        fingers = list(fingers)
        if numFingers > 0:
            coords = handContour[fingers[0]["pt"]][0]
            if self.ft.getPtDist(coords, self.coordinates, 2) <= self.maxDrawingSpeed:
                self.coordinates = coords*(720/540)
            self.paintMode = numFingers - 1

    def trackMarker(self):
        coords = self.mt.track()
        if self.mt.getPtDist(coords, self.coordinates, 2) <= self.maxDrawingSpeed:
            self.coordinates = coords*(720/540)

    def initialiseHand(self):
        colorRange, objectHist = self.getTrackerColorAndHist("Hand")
        self.ft = fingerTracker(self.cap, colorRange, objectHist)

    def initialiseMarker(self):
        colorRange, objectHist = self.getTrackerColorAndHist("Marker")
        self.mt = markerTracker(self.cap, colorRange)

    def painter(self):
        if self.paintMode == 0:
            self.ph.draw(self.coordinates)
        if self.paintMode == 1:
            self.ph.moveCursor(self.coordinates)
        if self.paintMode == 2 and self.markerColorMode == 0:
            self.paintColor = self.getDrawingColorAverage()
            self.ph.setColor(self.paintColor)

    def paint(self):
        if self.trackerMode == 0:
            self.initialiseHand()
        elif self.trackerMode == 1:
            self.initialiseMarker()

        if self.markerColorMode == 0:
            self.paintColor = self.getDrawingColorAverage()
            time.sleep(5)
            self.ph.setColor(self.paintColor)

        while True:
            if self.trackerMode == 0:
                self.trackFinger()
            elif self.trackerMode == 1:
                self.trackMarker()

            keyPress = cv2.waitKey(1)
            if keyPress == ord('q'):
                cv2.destroyAllWindows()
                self.cap.release()
                break
            elif keyPress == ord('d'):
                self.paintMode = 0
            elif keyPress == ord('u'):
                self.paintMode = 1
            elif keyPress == ord('p'):
                self.paintMode = 2

            self.painter()

painter = painterMain()
painter.paint()
