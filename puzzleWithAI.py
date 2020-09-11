import random
import time
import copy
import AI
import AI_best
from tkinter import Frame, Label, CENTER

import logic
import constants as c


class GameGrid(Frame):
    def __init__(self):
        Frame.__init__(self)

        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_down)

        # self.gamelogic = gamelogic
        self.commands = {c.KEY_UP: logic.up, c.KEY_DOWN: logic.down,
                         c.KEY_LEFT: logic.left, c.KEY_RIGHT: logic.right,
                         c.KEY_UP_ALT: logic.up, c.KEY_DOWN_ALT: logic.down,
                         c.KEY_LEFT_ALT: logic.left, c.KEY_RIGHT_ALT: logic.right,
                         c.KEY_H: logic.left, c.KEY_L: logic.right,
                         c.KEY_K: logic.up, c.KEY_J: logic.down}

        self.intervalTime = 1 # (ms)
        self.totalStep = 0
        self.uselessStep = 0
        
        self.grid_cells = []
        self.init_grid()
        self.init_matrix()
        self.update_grid_cells()

        self.after(self.intervalTime, self.AI_Expectimax)
        self.mainloop()

    class vitualKeyboardSignal:
        def __init__(self):
            self.char = ""

    def AI_Random(self): # randomly play
        a=self.vitualKeyboardSignal()
        AIcommands = ['w', 'a', 's', 'd']
        a.char = AIcommands[random.randint(0, 3)]
        self.key_down(a)
        if logic.game_state(self.matrix) == 'not over':
            self.after(self.intervalTime, self.AI_Random)

    def AI_Rule1(self): # randomly play
        a=self.vitualKeyboardSignal()
        AIcommands = ['w', 'a', 's', 'd']
        AIRule = ['w', 'a', 'w', 'w', 'a']
        a.char = AIRule[self.totalStep % len(AIRule)]
        self.totalStep += 1
        if self.key_down(a):
            self.uselessStep = 0
        else:
            self.uselessStep += 1
        if self.uselessStep > 6:
            a.char = 'd'
            if self.key_down(a):
                self.uselessStep = 0
            else:
                self.uselessStep += 1
        if self.uselessStep > 20:
            a.char = 'd'
            self.key_down(a)
            self.uselessStep = 0

        if logic.game_state(self.matrix) == 'not over':
            self.after(self.intervalTime, self.AI_Rule1)

    def calcRandomExpection(self, matrix, i):
        AIcommands = ['w', 'a', 's', 'd']

        step = 0
        matrix2 = copy.deepcopy(self.matrix)
        matrix2, done = self.commands[repr(i)](matrix2)

        if done:
            step += 1
            logic.add_two(matrix2)
            if logic.game_state(matrix2) == 'win':
                del matrix2
                return step + 100000
            if logic.game_state(matrix2) == 'lose':
                del matrix2
                return step
        else:
            return -1

        while logic.game_state(matrix2) != 'lose':
            matrix2, done = self.commands[repr(AIcommands[random.randint(0, 3)])](matrix2)
            if done:
                step += 1
                logic.add_two(matrix2)
                if logic.game_state(matrix2) == 'win':
                    del matrix2
                    return step + 100000
                if logic.game_state(matrix2) == 'lose':
                    del matrix2
                    return step

    def AI_EvaluationGreedy(self):

        AIcommands = ['w', 'a', 's', 'd']

        maxstep = -1
        nextStep = 'w'

        for i in AIcommands:
            tryTimes = 5
            average = 0
            for j in range(30):
                average += self.calcRandomExpection(self.matrix, i)
            if average > maxstep:
                nextStep = i
                maxstep = average

        a=self.vitualKeyboardSignal()
        a.char = nextStep
        self.key_down(a)
        if logic.game_state(self.matrix) == 'not over':
            self.after(self.intervalTime, self.AI_EvaluationGreedy)

    def AI_Expection(self):
        a=self.vitualKeyboardSignal()
        tmp = self.matrix.copy()
        a.char = AI.getNextMove(tmp)
        self.key_down(a)
        if logic.game_state(self.matrix) == 'not over':
            self.after(self.intervalTime, self.AI_Expection)


    def AI_Expectimax(self):
        a=self.vitualKeyboardSignal()
        tmp = self.matrix.copy()
        AIBest = AI_best.AI()
        a.char = AIBest.getNextMove(tmp)
        self.key_down(a)
        if logic.game_state(self.matrix) == 'not over':
            self.after(self.intervalTime, self.AI_Expectimax)

    def init_grid(self):
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME,
                           width=c.SIZE, height=c.SIZE)
        background.grid()

        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(background, bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                             width=c.SIZE / c.GRID_LEN,
                             height=c.SIZE / c.GRID_LEN)
                cell.grid(row=i, column=j, padx=c.GRID_PADDING,
                          pady=c.GRID_PADDING)
                t = Label(master=cell, text="",
                          bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                          justify=CENTER, font=c.FONT, width=5, height=2)
                t.grid()
                grid_row.append(t)

            self.grid_cells.append(grid_row)

    def gen(self):
        return random.randint(0, c.GRID_LEN - 1)

    def init_matrix(self):
        self.matrix = logic.new_game(c.GRID_LEN)
        self.history_matrixs = list()
        self.matrix = logic.add_two(self.matrix)
        self.matrix = logic.add_two(self.matrix)

    def update_grid_cells(self):
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                new_number = self.matrix[i][j]
                if new_number == 0:
                    self.grid_cells[i][j].configure(
                        text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(text=str(
                        new_number), bg=c.BACKGROUND_COLOR_DICT[new_number],
                        fg=c.CELL_COLOR_DICT[new_number])
        self.update_idletasks()

    def key_down(self, event):
        key = repr(event.char)
        arrowKey = {"w": "↑", "a": "←", "d": "→", "s": "↓"}
        if key == c.KEY_BACK and len(self.history_matrixs) > 1:
            self.matrix = self.history_matrixs.pop()
            self.update_grid_cells()
            print('back on step total step:', len(self.history_matrixs))
            return True
        elif key in self.commands:
            self.matrix, done = self.commands[repr(event.char)](self.matrix)
            if done:
                print("key " + arrowKey[key[1]] + "  score " + str(logic.calcScore(self.matrix)))

                self.matrix = logic.add_two(self.matrix)
                # record last move
                self.history_matrixs.append(self.matrix)
                self.update_grid_cells()
                done = False
                if logic.game_state(self.matrix) == 'win':
                    self.grid_cells[1][1].configure(
                        text="You", bg=c.BACKGROUND_COLOR_CELL_WIN)
                    self.grid_cells[1][2].configure(
                        text="Win!", bg=c.BACKGROUND_COLOR_CELL_WIN)
                if logic.game_state(self.matrix) == 'lose':
                    self.grid_cells[1][1].configure(
                        text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                    self.grid_cells[1][2].configure(
                        text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                return True
            else:
                return False
        return False

    def generate_next(self):
        index = (self.gen(), self.gen())
        while self.matrix[index[0]][index[1]] != 0:
            index = (self.gen(), self.gen())
        self.matrix[index[0]][index[1]] = 2


gamegrid = GameGrid()
