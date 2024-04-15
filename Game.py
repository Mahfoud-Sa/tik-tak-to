from tkinter import*
from random import*
from time import sleep
from tkinter import messagebox as msg

from Buttons import *
from Buttons.play_btn import PlayBtn
class XO:
    
    def __init__(self):
        self.game= Tk()
        self.game.title('Tic Tac Toe')
        self.game.maxsize(1000,620)
        self.game.minsize(600,400)
        self.game.iconphoto(False,PhotoImage(file="assets/icons/icon.png"))
        self.label_1=Label(self.game,text='Tik tak toe \nGame',font='Helvetica 16 bold ').pack()
        self.btn=PlayBtn(self.game,'Play with Friend')
        self.btn_1=PlayBtn(self.game,'Play with computer')
        self.btn_2=PlayBtn(self.game,'Score')
        
    
    def start(self):
        self.game.mainloop()
