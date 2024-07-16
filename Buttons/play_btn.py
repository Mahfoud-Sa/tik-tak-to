from tkinter import Button


class PlayBtn:
     def __init__(self,game,text,_command=None) :
          
          Button(game,
                 command=_command,
                 border='0',
                 height=1,
                 width=20,
                 text=text,font='size 8',
                 fg='#fff',
                 background='#026ec1').pack()