from tkinter import *
from tkinter import colorchooser
import cv2
from PIL import Image, ImageTk, ImageColor
import HandTrackingModule as htm
import math
import random

root = Tk()
root.title("Tic Tac Toe")
root.geometry("700x600")
w, h = 600, 450
player, ai = "o", "x"

board = [""] * 9
boardCenters = [
    (w // 6, h // 6),
    (w // 2, h // 6),
    (5 * w // 6, h // 6),
    (w // 6, h // 2),
    (w // 2, h // 2),
    (5 * w // 6, h // 2),
    (w // 6, 5 * h // 6),
    (w // 2, 5 * h // 6),
    (5 * w // 6, 5 * h // 6),
]
boardPoints = [
    (w // 3, h // 3),
    (2 * w / 3, h // 3),
    (w // 3, 2 * h // 3),
    (2 * w // 3, 2 * h // 3),
]
isGameOver = None
gameScore = {"x": -1, "o": 1, "tie": 0}


def choose_color(currbtn):
    color_code = colorchooser.askcolor()
    currbtn.configure(bg=color_code[1])


def resetBoard():
    global board, isGameOver
    board = [""] * 9
    isGameOver = ""
    resultLabel["text"] = ""


def convertHexToBGR(color):
    temp = ImageColor.getcolor(color, "RGB")
    converted = [temp[2], temp[1], temp[0]]
    return converted


def drawSignOnFrame(img, point, sign, colorInHex):
    l = h // 9
    px, py = point
    BGRcolor = convertHexToBGR(colorInHex)
    if sign == "x":
        cv2.line(img, (px - l, py - l), (px + l, py + l), BGRcolor, 7)
        cv2.line(img, (px - l, py + l), (px + l, py - l), BGRcolor, 7)
    if sign == "o":
        cv2.circle(img, (px, py), l, BGRcolor, 7)


def drawBoardOnFrame(img, colorInHex):
    BGRcolor = convertHexToBGR(colorInHex)

    cv2.line(img, (int(w / 3), 10), (int(w / 3), h - 10), BGRcolor, 4)
    cv2.line(img, (int(2 * w / 3), 10), (int(2 * w / 3), h - 10), BGRcolor, 4)
    cv2.line(img, (10, int(h / 3)), (w - 10, int(h / 3)), BGRcolor, 4)
    cv2.line(img, (10, int(2 * h / 3)), (w - 10, int(2 * h / 3)), BGRcolor, 4)


def findCellOnBoard(x, y):
    if (x <= boardPoints[0][0]) and (y <= boardPoints[0][1]):
        return 0
    if (x >= boardPoints[0][0] and x <= boardPoints[1][0]) and (y <= boardPoints[0][1]):
        return 1
    if (x >= boardPoints[1][0]) and (y <= boardPoints[1][1]):
        return 2
    if (x <= boardPoints[0][0]) and (y >= boardPoints[0][1] and y <= boardPoints[2][1]):
        return 3
    if (x >= boardPoints[0][0] and x <= boardPoints[1][0]) and (
        y >= boardPoints[0][1] and y <= boardPoints[2][1]
    ):
        return 4
    if (x >= boardPoints[1][0]) and (y >= boardPoints[0][1] and y <= boardPoints[2][1]):
        return 5
    if (x <= boardPoints[0][0]) and (y >= boardPoints[2][1]):
        return 6
    if (x >= boardPoints[0][0] and x <= boardPoints[1][0]) and (y >= boardPoints[2][1]):
        return 7
    if (x >= boardPoints[1][0]) and (y >= boardPoints[2][1]):
        return 8


def checkForEndGame(capframe, draw=True):
    point1, point2, sign, color = None, None, None, None
    if board[0] == board[1] == board[2] != "":
        point1, point2, sign = 0, 2, board[0]
    if board[3] == board[4] == board[5] != "":
        point1, point2, sign = 3, 5, board[3]
    if board[6] == board[7] == board[8] != "":
        point1, point2, sign = 6, 8, board[6]

    if board[0] == board[3] == board[6] != "":
        point1, point2, sign = 0, 6, board[0]
    if board[1] == board[4] == board[7] != "":
        point1, point2, sign = 1, 7, board[1]
    if board[2] == board[5] == board[8] != "":
        point1, point2, sign = 2, 8, board[2]

    if board[0] == board[4] == board[8] != "":
        point1, point2, sign = 0, 8, board[0]
    if board[2] == board[4] == board[6] != "":
        point1, point2, sign = 2, 6, board[2]

    emptyCellCount = 0
    for i in range(9):
        if board[i] == "":
            emptyCellCount += 1
    if emptyCellCount == 0:
        sign = "tie"

    if sign == None:
        return None

    if draw:
        if sign == "x":
            color = XColorButton["bg"]
            resultLabel["text"] = "You Lose!"
            resultLabel["fg"] = "red"
        elif sign == "o":
            color = OColorButton["bg"]
            resultLabel["text"] = "You Win!"
            resultLabel["fg"] = "green"
        else:
            resultLabel["text"] = "Tie!"
            resultLabel["fg"] = "black"

        BGRcolor = convertHexToBGR(color)
        cv2.line(capframe, boardCenters[point1], boardCenters[point2], BGRcolor, 4)
    return sign


def minimax(capframe, depth, isMaximizing):
    global board
    result = checkForEndGame(capframe, draw=False)
    if result != None:
        return gameScore[result]
    if depth == 3:
        return 0

    if isMaximizing:
        bestScore = float("-inf")
        for i in range(9):
            if board[i] == "":
                board[i] = ai
                score = minimax(capframe, depth + 1, False)
                board[i] = ""
                bestScore = max(score, bestScore)
        return bestScore
    else:
        bestScore = float("inf")
        for i in range(9):
            if board[i] == "":
                board[i] = player
                score = minimax(capframe, depth + 1, True)
                board[i] = ""
                bestScore = min(score, bestScore)
        return bestScore


def bestMovePossible(capframe):
    global board
    bestScore = float("-inf")
    bestMove = 0
    for i in range(9):
        if board[i] == "":
            board[i] = ai
            score = minimax(capframe, 0, False)
            board[i] = ""
            if score > bestScore:
                bestScore = score
                bestMove = i
    return bestMove


# Camera Frame
camFrame = LabelFrame(root, text="Camera", width=500, height=400)
camFrame.grid(row=0, column=0, padx=10, pady=5, columnspan=3)

# Label for camera
camFrameLabel = Label(camFrame)
camFrameLabel.pack()

# Color Frame
colorPickerFrame = LabelFrame(root, text="Color", width=100, height=400)
colorPickerFrame.grid(row=1, column=0, padx=5, pady=5)

# Color Buttons
boardLabel = Label(colorPickerFrame, text="Board: ")
boardLabel.grid(row=0, column=0, padx=5, pady=5)

boardColorButton = Button(
    colorPickerFrame,
    text="",
    bg="#42f584",
    width=10,
    command=lambda: choose_color(boardColorButton),
)
boardColorButton.grid(row=0, column=1, padx=5, pady=5)

# X color
XColorLabel = Label(colorPickerFrame, text="X: ")
XColorLabel.grid(row=0, column=4, padx=5, pady=5)

XColorButton = Button(
    colorPickerFrame,
    text="",
    bg="#4254f5",
    width=10,
    command=lambda: choose_color(XColorButton),
)
XColorButton.grid(row=0, column=5, padx=5, pady=5)

# O color
OColorLabel = Label(colorPickerFrame, text="O: ")
OColorLabel.grid(row=0, column=2, padx=5, pady=5)

OColorButton = Button(
    colorPickerFrame,
    text="",
    bg="#f54b42",
    width=10,
    command=lambda: choose_color(OColorButton),
)
OColorButton.grid(row=0, column=3, padx=5, pady=5)

# Reset button
resetButton = Button(root, text="Reset", width=10, command=lambda: resetBoard())
resetButton.grid(row=1, column=1)

# Result
resultLabel = Label(root, text="", font=10)
resultLabel.grid(row=1, column=2)


cap = cv2.VideoCapture(0)
detector = htm.handDetector(detectionCon=0.75)


def showFrames():
    global isGameOver
    sucess99, capframe = cap.read()
    capframe = cv2.resize(capframe, (w, h))
    capframe = cv2.flip(capframe, 1)

    capframe = detector.findHands(capframe, draw=False)
    lmList = detector.findPosition(capframe, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(capframe, (x1, y1), 4, (255, 0, 255), cv2.FILLED)
        cv2.circle(capframe, (x2, y2), 4, (255, 0, 255), cv2.FILLED)
        cv2.circle(capframe, (cx, cy), 3, (255, 0, 255), cv2.FILLED)
        cv2.line(capframe, (x1, y1), (x2, y2), (255, 0, 255), 2)

        length = math.hypot(x2 - x1, y2 - y1)

        if length < 50 and isGameOver == None:
            cv2.circle(
                capframe, (cx, cy), 3, convertHexToBGR(XColorButton["bg"]), cv2.FILLED
            )
            playerCellIndex = findCellOnBoard(cx, cy)
            if board[playerCellIndex] == "":
                board[playerCellIndex] = player
                isGameOver = checkForEndGame(capframe)
                if isGameOver == None:
                    aiMove = bestMovePossible(capframe)
                    board[aiMove] = ai

    isGameOver = checkForEndGame(capframe)

    drawBoardOnFrame(capframe, boardColorButton["bg"])
    for i in range(9):
        if board[i] == "x":
            drawSignOnFrame(capframe, boardCenters[i], "x", XColorButton["bg"])
        if board[i] == "o":
            drawSignOnFrame(capframe, boardCenters[i], "o", OColorButton["bg"])

    cv2image = cv2.cvtColor(capframe, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)

    imgtk = ImageTk.PhotoImage(image=img)
    camFrameLabel.imgtk = imgtk
    camFrameLabel.configure(image=imgtk)

    camFrameLabel.after(10, showFrames)


showFrames()

root.mainloop()
