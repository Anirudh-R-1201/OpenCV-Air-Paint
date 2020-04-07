import pyautogui

class paintHelper:
    def __init__(self):
        self.screenWidth, self.screenHeight = pyautogui.size()
        self.canvasWidth = 1280
        self.canvasHeight = 720
        self.canvasXo = 5
        self.canvasYo = 144
        self.x, self.y = pyautogui.position()

    def setColor(self, color):
        pyautogui.moveTo(993, 69)
        pyautogui.click()
        pyautogui.moveTo(1083, 596)
        pyautogui.click()
        pyautogui.press(['backspace', 'backspace', 'backspace'])
        pyautogui.typewrite(str(color[0]), interval=0.1)
        pyautogui.moveTo(1083, 618)
        pyautogui.click()
        pyautogui.press(['backspace', 'backspace', 'backspace'])
        pyautogui.typewrite(str(color[1]), interval=0.1)
        pyautogui.moveTo(1083, 639)
        pyautogui.click()
        pyautogui.press(['backspace', 'backspace', 'backspace'])
        pyautogui.typewrite(str(color[2]), interval=0.1)
        pyautogui.moveTo(775, 664)
        pyautogui.click()


    def moveCursor(self, c):
        pyautogui.moveTo(self.canvasXo + c[0], self.canvasYo + c[1])
        self.x, self.y = pyautogui.position()

    def draw(self, c):
        pyautogui.dragTo(self.canvasXo + c[0], self.canvasYo + c[1], duration = 0)
        self.x, self.y = pyautogui.position()
