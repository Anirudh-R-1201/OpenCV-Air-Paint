import cv2
import numpy as np
import itertools
from numpy import linalg as LA
from autocalibration import AutoCalibration
from equivalence import Equivalence

skinColorUpper = lambda hue: np.array([hue, 0.8 * 255, 0.6 * 255])
skinColorLower = lambda hue: np.array([hue, 0.1 * 255, 0.05 * 255])

class fingerTracker:
    def __init__(self, cap, colorRange, objectHist):
        self.colorRange = colorRange
        self.objectHist = objectHist
        self.cap = cap
        self.trail = []

    def makeHandMaskFromColor(self, img):
        imgHLS = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        rangeMask = cv2.inRange(imgHLS, self.colorRange[0], self.colorRange[1])
        blurred = cv2.blur(rangeMask, (10, 10))
        _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
        return thresh

    def makeHandMaskFromHist(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0, 1], self.objectHist, [0, 180, 0, 256], 1)
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cv2.filter2D(dst, -1, disc, dst)
        _, thresh = cv2.threshold(dst, 150, 255, cv2.THRESH_BINARY)
        return thresh

    def getHandContour(self, handMask):
        contours,_ = cv2.findContours(handMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        return contours[0]

    def getPtDist(self, x, y, n):
        distance = 0
        for i in range(n):
            distance += (x[i]-y[i])**2
        return distance**0.5

    def getCenter(self, pointGroup, ptName = "hullPoint"):
        centerX = 0
        centerY = 0
        n = 0
        for i in pointGroup:
            centerX += i[ptName][0]
            centerY += i[ptName][1]
            n += 1
        return centerX/n, centerY/n

    def getMostCentralPoint(self, pointGroup, ptName = "hullPoint"):
        center = self.getCenter(pointGroup, ptName)
        findDiff = lambda x: self.getPtDist(center, x[ptName], 2)
        return sorted(pointGroup, key = findDiff)[0]

    def getCenterIndices(self, contour, pointGroup, ptName):
        centerX = 0
        centerY = 0
        n = 0
        for i in pointGroup:
            centerX += contour[i[ptName]][0][0]
            centerY += contour[i[ptName]][0][1]
            n += 1
        return centerX/n, centerY/n

    def getFarthestPoint(self, contour, pointGroup):
        M = cv2.moments(contour)
        center = [int(M['m10']/M['m00']), int(M['m01']/M['m00'])]
        findDiff = lambda x: self.getPtDist(center, contour[x["pt"]][0], 2)
        return sorted(pointGroup, key = findDiff, reverse=True)[0]

    def getRoughHull(self, contour, maxDist):
        hullPoints = cv2.convexHull(contour, returnPoints=False)
        hullPoints = map(lambda idx: {"hullPoint": contour[idx][0][0], "idx": idx[0]}, hullPoints)
        ptsBelongToSameCluster = lambda pt1, pt2: self.getPtDist(pt1["hullPoint"], pt2["hullPoint"], 2) < maxDist
        e_classes = Equivalence().equivalence_partition(hullPoints, ptsBelongToSameCluster)
        return map(self.getMostCentralPoint, np.array(e_classes))

    def getHullDefects(self, contour, hullPoints):
        hullIndices = np.array([[i["idx"]] for i in hullPoints])
        defects = cv2.convexityDefects(contour, hullIndices)
        hullPointDefectNeighbours = {}
        for i in hullIndices:
            hullPointDefectNeighbours[i[0]] = []
        for i in defects:
            startPointIdx = i[0][0]
            endPointIdx = i[0][1]
            defectPointIdx = i[0][2]
            hullPointDefectNeighbours.get(startPointIdx).append(defectPointIdx)
            hullPointDefectNeighbours.get(endPointIdx).append(defectPointIdx)
        dpd = map(lambda iter: {"pt": iter[0], "d1": iter[1][0], "d2": iter[1][1]}, filter(lambda i: len(i[1]) == 2, hullPointDefectNeighbours.items()))
        pdp = map(lambda iter: {"df": iter[0][2], "p1": iter[0][0], "p2": iter[0][1]}, defects)
        return dpd, pdp

    def boolVerticesByAngle(self, contour, v, maxAngleDeg):
        v1 = np.subtract(contour[v["d1"]][0], contour[v["pt"]][0])
        v2 = np.subtract(contour[v["d2"]][0], contour[v["pt"]][0])
        angle = np.arccos(np.sum(v1*v2)/(LA.norm(v1)*LA.norm(v2))) * 180 / np.pi
        return angle < maxAngleDeg

    def filterVerticesByAngle(self, contour, vertices, maxAngleDeg):
        return filter(lambda v: self.boolVerticesByAngle(contour, v, maxAngleDeg), vertices)

    def findBetas(self, contour, vertices):
        betas = []
        for v in vertices:
            v1 = np.subtract(contour[v["p1"]][0], contour[v["df"]][0])
            v2 = np.subtract(contour[v["p2"]][0], contour[v["df"]][0])
            angle = np.arccos(np.sum(v1*v2)/(LA.norm(v1)*LA.norm(v2))) * 180 / np.pi
            betas.append(angle)
        return betas

    def returnPoints(self, mask):
        handContour = self.getHandContour(mask)
        handHull = self.getRoughHull(handContour, 50)
        handHull1, handHull2 = itertools.tee(handHull, 2)
        hullDefectsDPD, hullDefectsPDP = self.getHullDefects(handContour, handHull1)
        angleFilter = self.filterVerticesByAngle(handContour, hullDefectsDPD, 60)
        betas = self.findBetas(handContour, hullDefectsPDP)
        return handContour, handHull2, angleFilter, betas

    def setColorAverage(self):
        cali = AutoCalibration("Hand")
        averageColor = cali.calibrate(0)
        self.colorRange = averageColor[1], averageColor[2]

    def setColorDefault(self, hue):
        self.colorRange = skinColorLower(0), skinColorUpper(15)

    def addToTrail(self, point):
        if len(self.trail) == 20:
            self.trail = self.trail[1:20]
        self.trail.append(point)

    def track(self, colorMode):
        if not self.cap.isOpened():
            self.cap.open(0)
        _, frame = self.cap.read()
        frame = np.flip(frame, axis=1)
        cntimg = frame.copy()
        numFingers = 0
        if colorMode == 0:
            handMask = self.makeHandMaskFromColor(frame)
        elif colorMode == 1:
            handMask = self.makeHandMaskFromHist(frame)
        handContour, handHull, angleFilter, betas = self.returnPoints(handMask)
        angleFilter1, angleFilter2 = itertools.tee(angleFilter, 2)
        cv2.drawContours(cntimg, [handContour], 0, (255, 0, 0), 2)
        cv2.drawContours(cntimg, np.array([[i["hullPoint"] for i in handHull]]), -1, (0, 255, 0), 5)
        for i in angleFilter1:
            numFingers += 1
            cv2.circle(cntimg, tuple(handContour[i["pt"]][0]), 10, (0,0,255), 3)

        for i in self.trail:
            cv2.circle(cntimg, i, 9, (255, 255, 255), -1)

        cv2.putText(cntimg, f"{betas[0]},{betas[-1]},{numFingers}", (30, 50), cv2.FONT_HERSHEY_COMPLEX, 0.85, (255,0,105), 1, cv2.LINE_AA)
        cv2.imshow("Hand Contour Average", cntimg)
        return numFingers, angleFilter2, betas, handContour

    def endTracking(self):
        cv2.destroyAllWindows()
