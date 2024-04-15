from tkinter import Button


class PlayBtn:
     def __init__(self,game,text) :
          Button(game,text=text,font='italian').pack()