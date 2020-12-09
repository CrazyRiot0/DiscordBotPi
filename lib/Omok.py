isOmokPlaying = False
isOmokHosting = False
OmokPlayer_White = None
OmokPlayer_White_Name = None
OmokPlayer_Black = None
OmokPlayer_Black_Name = None
Omok_Turn = None
OmokBoard_Len = 19
OmokBoard = None
NumberInCircle = ["⓪", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
                  "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳",
                  "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚",
                  "㉛", "㉜", "㉝", "㉞", "㉟", "㊱", "㊲", "㊳", "㊴", "㊵",
                  "㊶", "㊷", "㊸", "㊹", "㊺", "㊻", "㊼", "㊽", "㊾", "㊿", ]
WhiteC = "○"
BlackC = "●"
EmptySpace = "ㅤ"

def Omok_MakeBoard():
    len = OmokBoard_Len
    global OmokBoard
    OmokBoard = [[0 for x in range(len)] for y in range(len)]
    for i in range(0, len):
        for j in range(0, len):
            OmokBoard[i][j] = "┼"

    for i in range(0, len):
        OmokBoard[0][i] = "┬"
        OmokBoard[len - 1][i] = "┴"
        OmokBoard[i][0] = "├"
        OmokBoard[i][len - 1] = "┤"

    OmokBoard[0][0] = "┌"
    OmokBoard[0][len - 1] = "┐"
    OmokBoard[len - 1][0] = "└"
    OmokBoard[len - 1][len - 1] = "┘"

def Omok_PlaceInCoord(x, y, color):  # color True = White, False = Black
    global OmokBoard
    global OmokBoard_Len

    if x > OmokBoard_Len or y > OmokBoard_Len or x < 0 or y < 0:
        return -1

    x = x - 1
    y = y - 1

    if OmokBoard[y][x] == 1 or OmokBoard[y][x] == 0:
        return 0

    if color is True:
        OmokBoard[y][x] = 1
    else:
        OmokBoard[y][x] = 0

    return True

def OmokBoardInStr():
    global OmokBoard
    global OmokBoard_Len
    global NumberInCircle
    global EmptySpace
    S = ""
    S += EmptySpace
    for i in range(1, OmokBoard_Len + 1):
        S += NumberInCircle[i]
    S += "\n"

    for i in range(0, OmokBoard_Len):
        S += NumberInCircle[i + 1]
        for j in range(0, OmokBoard_Len):
            if OmokBoard[i][j] == 1:
                S += WhiteC
            elif OmokBoard[i][j] == 0:
                S += BlackC
            else:
                S += OmokBoard[i][j]
        S += "\n"
    return S

def Omok_CheckBoard():
    global OmokBoard
    global OmokBoard_Len
    for i in range(0, OmokBoard_Len):  # 가로를 보아라.
        count_w = 0
        count_b = 0
        prev = None
        for j in range(0, OmokBoard_Len):
            if OmokBoard[i][j] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[i][j] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[i][j]

    for i in range(0, OmokBoard_Len):  # 세로를 보아라.
        count_w = 0
        count_b = 0
        prev = None
        for j in range(0, OmokBoard_Len):
            if OmokBoard[j][i] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[j][i] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[i][j]

    # 대각선의 시작...
    len = OmokBoard_Len

    for i in range(0, len):
        X, Y = i, 0

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X - 1
            Y = Y + 1

    for i in range(0, len):
        X, Y = len - 1, i

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X - 1
            Y = Y + 1

    for i in range(0, len):
        X, Y = len - 1 - i, 0

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X + 1
            Y = Y + 1

    for i in range(0, len):
        X, Y = 0, i - 1

        count_w = 0
        count_b = 0
        prev = None

        while True:
            if X > len - 1 or Y > len - 1 or X < 0 or Y < 0:
                break

            if OmokBoard[X][Y] == 1:  # White
                if prev != 1:
                    count_w = 1
                else:
                    count_w = count_w + 1
            elif OmokBoard[X][Y] == 0:  # Black
                if prev != 0:
                    count_b = 1
                else:
                    count_b = count_b + 1

            if count_w >= 5:
                return 1
            if count_b >= 5:
                return 0
            prev = OmokBoard[X][Y]

            X = X + 1
            Y = Y + 1

    return -1

async def AsyncOmokCounter():
    pass
    global isOmokPlaying
    while True:
        if isOmokPlaying:
            pass
