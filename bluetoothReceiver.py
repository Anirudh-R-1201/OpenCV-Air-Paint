import serial
import time

arduino = serial.Serial('COM9', 9600, timeout=1)

inputList = []

def addToList(x):
    if len(inputList) == 4:
        inputList = inputList[1:4]
    imputList.append(x)

def equateLists(x, y):
    if len(x) != len(y):
        return False
    for i in range(len(x)):
        if x[i] != y[i]:
            return False
    return True

while True:
    while arduino.in_waiting:
        info = arduino.readline()
        addToList(info)
        print(info)
    if equateLists(inputList, exitCondition):
        break
