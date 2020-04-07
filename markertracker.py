import cv2
import numpy as np
import itertools
from autocalibration import AutoCalibration

class markerTracker:
    def __init__(self, cap, colorRange):
        self.colorRange = colorRange
        self.cap = cap
        self.trail = []

    def getPtDist(self, x, y, n):
        distance = 0
        for i in range(n):
            distance += (x[i]-y[i])**2
        return distance**0.5

    def makeMarkerMaskFromColor(self, img):
        imgHLS = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        rangeMask = cv2.inRange(imgHLS, self.colorRange[0], self.colorRange[1])
        blurred = cv2.blur(rangeMask, (10, 10))
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
        return thresh

    def getMarkerContour(self, mask):
        contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        return contours[0]

    def getMinEnclosingCircle(self, contour):
        (x,y),radius = cv2.minEnclosingCircle(contour)
        center = (int(x),int(y))
        radius = int(radius)
        return center, radius

    def track(self):
        if not self.cap.isOpened():
            self.cap.open(0)
        _, frame = self.cap.read()
        frame = np.flip(frame, axis=1)
        cntimg = frame.copy()
        markerMask = self.makeMarkerMaskFromColor(frame)
        markerContour = self.getMarkerContour(markerMask)
        center, radius = self.getMinEnclosingCircle(markerContour)
        cv2.circle(cntimg,center,radius,(0,255,0),2)
        cv2.imshow("Image", cntimg)
        return np.array(center)

    def endTracking(self):
        cv2.destroyAllWindows()
        self.cap.release()
