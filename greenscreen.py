import cv2
import numpy as np
import urllib.request as ur

def findPtDist(x, y, n):
    distance = 0
    for i in range(n):
        distance += (x[i]-y[i])**2
    return distance**0.5

def rotateArray(a, m, n):
    for i in range(n):
        t = a[0].copy()
        for i in range(m - 1):
            a[i] = a[i+1]
        a[m-1] = t
    return a

def findRectangle(vertices):
    lengths = []
    for i in range(4):
        lengths.append(findPtDist(vertices[i][0], vertices[(i+1)%4][0], 2))
    maxIndex = lengths.index(max(lengths))
    rotated = rotateArray(vertices, 4, maxIndex+1)
    return rotated


url = "https://cdn.dribbble.com/users/2582040/screenshots/5358788/darth-vader.png"
cap = cv2.VideoCapture(0)
imgResp=ur.urlopen(url)
imgNp=np.array(bytearray(imgResp.read()), dtype=np.uint8)
art=cv2.imdecode(imgNp, -1)
if len(art.shape) > 2 and art.shape[2] == 4:
    #convert the image from RGBA2RGB
    art = cv2.cvtColor(art, cv2.COLOR_BGRA2BGR)
green = cv2.imread('green.png')
#art = cv2.imread('art.jpg')
while True:
    #_, green = cap.read()

    lower_green = np.array([65,60,60])
    upper_green = np.array([80,255,255])

    greenHSV = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    blurred = cv2.GaussianBlur(greenHSV, (5, 5), 0)
    greenMask = cv2.inRange(blurred, lower_green, upper_green)
    greenMaskInv = np.invert(greenMask)
    res = cv2.bitwise_and(green,green, mask=greenMaskInv)
    (contours, _) = cv2.findContours(greenMask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    image = green

    if len(contours) > 0:

        target = None

        for c in contours:
            p = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * p, True)

            if len(approx) == 4:
                target = approx
                break

        target = findRectangle(target)

        pts = np.float32([[[0, 0]],[[0,art.shape[0]]], [[art.shape[1], art.shape[0]]], [[art.shape[1], 0]]])
        target = np.float32(target)
        M = cv2.getPerspectiveTransform(pts, target)
        dst = cv2.warpPerspective(art,M,tuple((green.shape[1], green.shape[0])))

        image = res + dst
    cv2.imshow("Image", image)
    if cv2.waitKey(1) == 27:
        break
cv2.destroyAllWindows()
cap.release()
