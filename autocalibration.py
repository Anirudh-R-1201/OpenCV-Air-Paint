import numpy as np
import cv2
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
import colorsys

class AutoCalibration:
    def __init__(self, cap):
        self.cap = cap

    def averageColor(self, objectColor):
        objectHSVColor = cv2.cvtColor(objectColor, cv2.COLOR_BGR2HSV)
        average = objectHSVColor.mean(axis=0).mean(axis=0)
        for i in range(len(average)):
            average[i] = int(average[i])

        lower_average = np.array([average[0] - 50, average[1] - 75, average[2] - 150])
        upper_average = np.array([average[0] + 50, average[1] + 75, average[2] + 150])
        return average, lower_average, upper_average

    def histogramColor(self, objectColor):
        objectHSVColor = cv2.cvtColor(objectColor, cv2.COLOR_BGR2HSV)
        objectHist = cv2.calcHist([objectHSVColor], [0,1], None, [12, 15], [0, 180, 0, 256])
        cv2.normalize(objectHist, objectHist, 0, 255, cv2.NORM_MINMAX)
        return objectHist

    #def histogramPeakColor(objectColor):

    def calibrate(self, objectName):
        objectColor = None
        while True:
            if not self.cap.isOpened():
                self.cap.open(0)
            _, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            boxedFrame = frame
            cv2.putText(boxedFrame, f"Place region of {objectName} inside the box.", (30, 50), cv2.FONT_HERSHEY_COMPLEX, 0.85, (255, 0, 105), 1, cv2.LINE_AA)
            cv2.rectangle(boxedFrame, (75, 75), (100, 100), (255, 0, 255), 2)
            cv2.imshow("Frame", boxedFrame)
            keyPress = cv2.waitKey(10)
            if keyPress == 108:
                objectColor = frame[78:98, 78:98]
                break
            if keyPress == 27:
                break

        cv2.destroyWindow("Frame")
        return self.averageColor(objectColor), self.histogramColor(objectColor)

'''
objectHSVColor = cv2.cvtColor(objectColor, cv2.COLOR_BGR2HSV)
average = objectHSVColor.mean(axis=0).mean(axis=0)
lower_average = np.array([average[0] - 50, average[1] - 75, average[2] - 150])
upper_average = np.array([average[0] + 50, average[1] + 75, average[2] + 150])

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_average, upper_average)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
    res = cv2.bitwise_and(frame,frame, mask= opening)

    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()

color = ('b','g','r')
for i,col in enumerate(color):
    histr = cv2.calcHist([objectColor], [i], None, [256], [0, 256])
    plt.plot(histr, color=col)
    plt.xlim([0, 256])
plt.show()

cv2.imshow("", objectColor)

img = cv2.cvtColor(objectColor, cv2.COLOR_BGR2RGB)
img = objectColor.reshape((img.shape[0] * img.shape[1], 3))
clt = KMeans(n_clusters = 1)
clt.fit(img)
newCenter = colorsys.rgb_to_hsv(clt.cluster_centers_[0][0]/255, clt.cluster_centers_[0][1]/255, clt.cluster_centers_[0][2]/255)
newCenter = np.array(newCenter)
print(clt.cluster_centers_[0], newCenter)

objectHist = cv2.calcHist([objectHSVColor], [0,1], None, [12, 15], [0, 180, 0, 256])
cv2.normalize(objectHist, objectHist, 0, 255, cv2.NORM_MINMAX)
totalV = 0
xMean = 0
yMean = 0
for i in range(12):
    for j in range(15):
        xMean += i*objectHist[i][j]
        yMean += j+objectHist[i][j]
        totalV += objectHist[i][j]

xMean = xMean/totalV
yMean = yMean/totalV
print(xMean, yMean)

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    objectSegment = cv2.calcBackProject([hsvFrame], [0,1], objectHist, [0, 180, 0, 256], 1)
    kern = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    cv2.filter2D(objectSegment, -1, kern, objectSegment)
    _, threshObjectSegment = cv2.threshold(objectSegment,120,255,cv2.THRESH_BINARY)
    threshObjectSegment = cv2.merge((threshObjectSegment,threshObjectSegment,threshObjectSegment))
    locatedObject = cv2.bitwise_and(frame, threshObjectSegment)
    cv2.imshow("Object", locatedObject)

    keyPress = cv2.waitKey(10)
    if keyPress == 27:
        cv2.destroyAllWindows()
        break
cap.release()
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
