# Xavier Engelbrecht
# Play Tic Tac Toe

### IMPORTS ###
import os
import json
import random
import asyncio
import time
from tkinter import *
from tkinter import ttk
from pathlib import Path
from PIL import ImageTk, Image

### DECLARATIONS ###
DATASTORE = "ttt_data.json"


### CLASSES ###
class TicTacToeBoard():
    '''
  Creates a new Tic Tac Toe game with functions. Pass a list variable to start with a previously made board.
  '''
    def __init__(self, learning = False):
        '''
    If a Tic Tac Toe board isn't provided, create a new one.
    '''
        self.board = {}
        self.round = 0
        self.winner = ""
        self.win = False
        self.turn = 1
        self.learning = learning

        for x in range(1, 10):
            self.board[x] = "*"

    def setButtons(self, buttons):
        self.buttons = buttons

    def __str__(self):
        '''
    Returns a string of the game with new lines.
    '''

        board = ""

        board += " ".join([self.board[1], self.board[2], self.board[3]])
        board += "\n"
        board += " ".join([self.board[4], self.board[5], self.board[6]])
        board += "\n"
        board += " ".join([self.board[7], self.board[8], self.board[9]])

        return board

    def make_move(self, player, pos):
        '''
    Runs a few checks to make sure the provided position is valid, and then fills that space with the player's letter.
    '''

        assert type(player) == str, "Player must either be \"X\" or \"O\"."
        try:
            pos = int(pos)
        except:
            assert False, "Position must be a valid integer."
        assert (pos >= 1
                and pos <= 9), "Position must be a valid integer from 1-9."
        assert self.board[
            pos] == "*", "The provided position has already been taken."

        self.board[pos] = player.upper()

        if not self.learning:
          im = Image.open(Path("Icons/{}.png".format(player.lower())))
          ph = ImageTk.PhotoImage(im)
          self.buttons[pos].configure(image=ph)
          self.buttons[pos].photo = ph

        data = self.has_won(player)
        self.win = data[0]
        self.winner = data[1]

        if self.turn == 1:
          self.turn = 2
        else:
          self.turn = 1

    def computer(self, letter):
        if letter == "O":
            opponent = "X"
        else:
            opponent = "O"

        possibilities = {}

        def findProbability(player):
            try:
              with open(DATASTORE, "r") as file:
                  data = json.load(file)
            except json.decoder.JSONDecodeError:
              possibilities[0] = 0
              return [0]

            for x in range(1, 10):
                possibilities[x] = 0

            for number, pos in self.board.items():
                if (pos == "*"):
                    for win_style in data.values():
                        for potential, mark in win_style.items():
                            potential = int(potential)
                            if mark:
                                if (self.board[potential] == "*"):
                                    fake_board = self.board.copy()
                                    fake_board[potential] = opponent
                                    if self.has_won(opponent, fake_board)[0]:
                                        possibilities[potential] += 1

            selected_spot = [1]

            for number, probability in possibilities.items():
                if not (self.board[number] == "*"):
                    continue

                previous_chance = possibilities[selected_spot[0]]
                if probability > previous_chance:
                    selected_spot = [number]
                elif probability == previous_chance:
                    if not selected_spot[0] == number:
                        selected_spot.append(number)
                else:
                    continue

            return selected_spot

        def makeSelection(list_of_pos):
            if len(list_of_pos) == 0:
                available = []

                for number, pos in self.board.items():
                    if pos == "*":
                        available.append(number)

                if len(available) == 0:
                    return

                choice = random.choice(available)
                try:
                    return self.make_move(letter, choice)
                except Exception:
                    available.remove(choice)
                    return makeSelection(available)
            else:
                choice = random.choice(list_of_pos)
                try:
                    return self.make_move(letter, choice)
                except Exception:
                    list_of_pos.remove(choice)
                    return makeSelection(list_of_pos)

        chance = findProbability(opponent)

        available = []

        for spot in self.board.keys():
            if (self.board[spot] == "*"):
                available.append(spot)
                fake_board = self.board.copy()
                fake_board[spot] = letter

                win = self.has_won(letter, fake_board)[0]

                if win:
                    return self.make_move(letter, spot)

        if possibilities[chance[0]] == 0 and self.round == 1:
            return self.make_move(letter, random.choice(available))
        else:
            return makeSelection(findProbability(opponent))

    def saveWin(self, winner):
        if winner is None:
            return

        for pos, x in self.board.items():
            if x == winner:
                self.board[pos] = True
            else:
                self.board[pos] = False
        try:
          with open(DATASTORE, "r") as file:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
          data = {}

        with open(DATASTORE, "w") as file:
            data[len(data)] = self.board

            file.write(json.encoder.JSONEncoder().encode(data))

    def has_won(self, player, board=None):
        '''
    Checks to see if a player has won by checking for any diagonal, horizontal, or vertical 3 in a rows. Returns True if the player has won, returns False if the player has not won.
    '''

        if board is None:
            board = self.board

        player = player.upper()

        # WIN STYLE - DIAGONAL
        for pos in [1, 3]:
            if board[pos] == player:
                if board[5] == player:
                    if pos == 1:
                        if board[9] == player:
                            return True, player
                        else:
                            continue

                    if pos == 3:
                        if board[7] == player:
                            return True, player
                        else:
                            continue
                else:
                    continue
            else:
                continue

        # WIN STYLE - VERTICAL
        for pos in [1, 2, 3]:
            if board[pos] == player:
                if board[pos + 3] == player:
                    if board[pos + 6] == player:
                        return True, player
                    else:
                        continue
                else:
                    continue
            else:
                continue

        # WIN STYLE - HORIZONTAL
        for pos in [1, 4, 7]:
            if board[pos] == player:
                if board[pos + 1] == player:
                    if board[pos + 2] == player:
                        return True, player
                    else:
                        continue
                else:
                    continue
            else:
                continue

        # The player did not pass any of the win checks
        return False, player

    def game_over(self):
        '''
    Returns True if any of the players has won, or if the board no longer has any spots.
    '''
        if "*" in self.board.values():
            return False
        else:
            return True

        return False


### FUNCIONS ###
def choose(game, pos, tk, frame):
    #os.system("clear")
    if game.turn == 1 and game.board[pos] == "*":
      game.make_move("X", pos)

      if (not game.win) and (not game.game_over()):
        game.computer("O")
      

    if game.win or game.game_over():
      game.saveWin(game.winner)

      def cont():
        tk.destroy()
        play_tic_tac_toe()
      
      def end():
        tk.destroy()

      Button(frame, text= "New game?", command= cont).grid(column= 7, row= 7)
      Button(frame, text= "End", command=end).grid(column= 8, row= 7)
        


def make_UI(game):
    tk = Tk()
    tk.title("Xavier's Tic Tac Toe AI")
    tk.attributes('-fullscreen',True)

    img = PhotoImage(file=Path("Icons/x.png"))
    tk.tk.call('wm', 'iconphoto', tk._w, img)

    neutral = PhotoImage(file=Path("Icons/neutral.png"))

    tk.geometry("800x480")

    frame = ttk.Frame(tk, padding=10)

    frame.grid()

    frame.grid_rowconfigure((0,2), weight=1)
    frame.grid_columnconfigure((0,2), weight=1)

    ttk.Label(frame, text="Select an available spot.").grid(column=0, row=0)

    buttons = {}

    width = 120
    height = 120

    for number, letter in enumerate(["A", "B", "C"]):
        number += 1
        letter_label = ttk.Label(frame, text=letter).grid(column=number, row=0)
        number_label = ttk.Label(frame, text=number).grid(column=0, row=number)


    buttons[1] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 1, tk, frame))
    buttons[1].image = neutral
    buttons[1].grid(column= 1, row= 1)

    buttons[2] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 2, tk, frame))
    buttons[2].image = neutral
    buttons[2].grid(column= 2, row= 1)

    buttons[3] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 3, tk, frame))
    buttons[3].image = neutral
    buttons[3].grid(column= 3, row= 1)

    buttons[4] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 4, tk, frame))
    buttons[4].image = neutral
    buttons[4].grid(column= 1, row= 2)

    buttons[5] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 5, tk, frame))
    buttons[5].image = neutral
    buttons[5].grid(column= 2, row= 2)

    buttons[6] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 6, tk, frame))
    buttons[6].image = neutral
    buttons[6].grid(column= 3, row= 2)

    buttons[7] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 7, tk, frame))
    buttons[7].image = neutral
    buttons[7].grid(column= 1, row= 3)

    buttons[8] = Button(frame, height=height,width= width,image= neutral, command= lambda: choose(game, 8, tk, frame))
    buttons[8].image = neutral
    buttons[8].grid(column= 2, row= 3)

    buttons[9] = Button(frame, height=height,width= width, image= neutral, command= lambda: choose(game, 9, tk, frame))
    buttons[9].image = neutral
    buttons[9].grid(column= 3, row= 3)

    return tk, buttons


def play_tic_tac_toe(learning= False):
    '''
  Main function that takes user input.
  '''
  
    game = TicTacToeBoard(learning)
    if not learning:
      uis = make_UI(game)
      tk = uis[0]
      buttons = uis[1]
      game.setButtons(buttons)
      tk.mainloop()

    while learning:
      game.round += 1

      game.computer("X")

      os.system("clear")
      print(game)
    
      if (not game.win) and (not game.game_over()):
          game.computer("O")

      os.system("clear")
      print(game)
      if game.win or (game.game_over()):
          if not game.game_over() and not game.win:
              game.winner = None
          break

    if learning:
      game.saveWin(game.winner)
      play_tic_tac_toe(True)
      

play_tic_tac_toe()
