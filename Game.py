from tkinter import*
from random import*
from time import sleep
from tkinter import messagebox as msg
class XO:
    
    def __init__(self):
        self.game= Tk()
        self.game.title('Tic Tac Toe')
        self.game.maxsize(1000,620)
        self.game.minsize(600,400)
        self.game.iconphoto(False,PhotoImage(file="assets/icons/icon.png"))

        # self.game.resizable(0,0)

    def start(self):
        self.game.mainloop()
