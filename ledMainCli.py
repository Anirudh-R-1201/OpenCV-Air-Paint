import cv2
import numpy as np
import serial
from fingertracker import fingerTracker
from autocalibration import AutoCalibration

class ledMain:
    def __init__(self):
        self.trackerMode = 0 # 0 - Angle, 1 - Number of fingers
        self.trackerColorMode = 0 # 0 - Average, 1 - Histogram
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        self.cali = AutoCalibration(self.cap)
        self.ft = None
        #self.serial = serial.Serial('COM9', 38400, timeout=1)
        self.brightness = 0
        self.betaRange = [120, 180]

    def transmitBrightness(self):
        self.serial.write(str(self.brightness).encode('utf-8'))

    def getTrackerColorAndHist(self, trackerName):
        averageColor, objectHist = self.cali.calibrate(trackerName)
        colorRange = averageColor[1:3]
        return colorRange, objectHist

    def trackFinger(self):
        numFingers, fingers, betas, handContour = self.ft.track(self.trackerColorMode)
        return numFingers, int(255*(betas[0]-self.betaRange[0])/(self.betaRange[1] - self.betaRange[0]))

    def initialiseHand(self):
        colorRange, objectHist = self.getTrackerColorAndHist("Hand")
        self.ft = fingerTracker(self.cap, colorRange, objectHist)

    def ledControl(self):
        self.initialiseHand()
        while True:
            numFingers, angle = self.trackFinger()
            if self.trackerMode == 0:
                self.brightness = angle
                if self.brightness < 0:
                    self.brightness = 0
                if self.brightness > 255:
                    self.brightness = 255
            else:
                self.brightness = numFingers*(255/5)
            print(self.brightness)
            if cv2.waitKey(10) == 27:
                cv2.destroyAllWindows()
                self.cam.release()
                break

led = ledMain()
led.ledControl()
