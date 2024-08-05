from tkinter import*
from random import*
from time import sleep
from os import path

import webbrowser

from tkinter import messagebox as msg
cot,counter,xp,op,cox,u1,selcet_computer=[0,0,0,0,0,1,0]
them=[('cyan','gray'),('gray','cyan'),('gray','orange'),('orange','gray'),('orange','green'),('green','orange'),('gray','brown'),('brown','gray'),('purple','gray'),('gray','purple')]
m=[[0,0,0],
   [0,0,0],
   [0,0,0]]

def two_players(event=1):
    if counter == 0:
        c1.bind("<Button-1>", drew_)
    elif counter == 1:
        c1.bind("<Button-1>", drew__)

def who_to_play(event=1):
    global counter,rad2
    if counter % 2 == 0:
        rad2.select()
        drew_(event)
    elif counter % 2 != 0:
        x1.after(300,play_computer)
    else:
        pass

def try_won():
    if m[0][0] == 'x' and m[0][1] == 'x' and m[0][2] ==0:
        drew21(0,2)
    elif m[1][0] == 'x' and m[1][1] == 'x' and m[1][2] ==0:
        drew21(1,2)
    elif m[2][0] == 'x' and m[2][1] == 'x' and m[2][2] ==0:
        drew21(2,2)
    elif m[0][2] == 'x' and m[0][1] == 'x' and m[0][0] ==0:
        drew21(0,0)
    elif m[1][2] == 'x' and m[1][1] == 'x' and m[1][0] ==0:
        drew21(1,0)
    elif m[2][2] == 'x' and m[2][1] == 'x' and m[2][0] ==0:
        drew21(2,0)
    elif m[0][0] == 'x' and m[0][2] == 'x' and m[0][1] ==0:
        drew21(0,1)
    elif m[1][0] == 'x' and m[1][2] == 'x' and m[1][1] ==0:
        drew21(1,1)
    elif m[2][0] == 'x' and m[2][2] == 'x' and m[2][1] ==0:
        drew21(2,1)
    #افقي
    elif m[2][0] == 'x' and m[1][0] == 'x' and m[0][0] ==0:
        drew21(0,0)
    elif m[2][1] == 'x' and m[1][1] == 'x' and m[0][1] ==0:
        drew21(0,1)
    elif m[2][2] == 'x' and m[1][2] == 'x' and m[0][2] ==0:
        drew21(0,2)
    elif m[0][0] == 'x' and m[1][0] == 'x' and m[2][0] ==0:
        drew21(2,0)
    elif m[0][1] == 'x' and m[1][1] == 'x' and m[2][1] ==0:
        drew21(2,1)
    elif m[0][2] == 'x' and m[1][2] == 'x' and m[2][2] ==0:
        drew21(2,2)
    elif m[2][0] == 'x' and m[0][0] == 'x' and m[1][0] ==0:
        drew21(1,0)
    elif m[2][1] == 'x' and m[0][1] == 'x' and m[1][1] ==0:
        drew21(1,1)
    elif m[2][2] == 'x' and m[0][2] == 'x' and m[1][2] ==0:
        drew21(1,2)
    # اكس
    elif m[0][0] == 'x' and m[1][1] == 'x' and m[2][2] ==0:
        drew21(2,2)
    elif m[2][2] == 'x' and m[1][1] == 'x' and m[0][0] ==0:
        drew21(0,0)
    elif m[2][2] == 'x' and m[0][0] == 'x' and m[1][1] ==0:
        drew21(1,1)
    elif m[0][2] == 'x' and m[1][1] == 'x' and m[2][0] ==0:
        drew21(2,0)
    elif m[2][0] == 'x' and m[1][1] == 'x' and m[0][2] ==0:
        drew21(0,2)
    elif m[2][2] == 'x' and m[0][2] == 'x' and m[1][1] ==0:
        drew21(1,1)
        ##منع الفوز
    # فقي
    else:
        if m[0][0] == 'o' and m[0][1] == 'o' and m[0][2] == 0:
            drew21(0, 2)
        elif m[1][0] == 'o' and m[1][1] == 'o' and m[1][2] == 0:
            drew21(1, 2)
        elif m[2][0] == 'o' and m[2][1] == 'o' and m[2][2] == 0:
            drew21(2, 2)
        elif m[0][2] == 'o' and m[0][1] == 'o' and m[0][0] == 0:
            drew21(0, 0)
        elif m[1][2] == 'o' and m[1][1] == 'o' and m[1][0] == 0:
            drew21(1, 0)
        elif m[2][2] == 'o' and m[2][1] == 'o' and m[2][0] == 0:
            drew21(2, 0)
        elif m[0][0] == 'o' and m[0][2] == 'o' and m[0][1] == 0:
            drew21(0, 1)
        elif m[1][0] == 'o' and m[1][2] == 'o' and m[1][1] == 0:
            drew21(1, 1)
        elif m[2][0] == 'o' and m[2][2] == 'o' and m[2][1] == 0:
            drew21(2, 1)
# افقي
        elif m[2][0] == 'o' and m[1][0] == 'o' and m[0][0] == 0:
            drew21(0, 0)
        elif m[2][1] == 'o' and m[1][1] == 'o' and m[0][1] == 0:
            drew21(0, 1)
        elif m[2][2] == 'o' and m[1][2] == 'o' and m[0][2] == 0:
            drew21(0, 2)
        elif m[0][0] == 'o' and m[1][0] == 'o' and m[2][0] == 0:
            drew21(2, 0)
        elif m[0][1] == 'o' and m[1][1] == 'o' and m[2][1] == 0:
            drew21(2, 1)
        elif m[0][2] == 'o' and m[1][2] == 'o' and m[2][2] == 0:
            drew21(2, 2)

        elif m[2][0] == 'o' and m[0][0] == 'o' and m[1][0] == 0:
            drew21(1, 0)
        elif m[2][1] == 'o' and m[0][1] == 'o' and m[1][1] == 0:
            drew21(1, 1)
        elif m[2][2] == 'o' and m[0][2] == 'o' and m[1][2] == 0:
            drew21(1, 2)
# اكس
        elif m[0][0] == 'o' and m[1][1] == 'o' and m[2][2] == 0:
            drew21(2, 2)
        elif m[2][2] == 'o' and m[1][1] == 'o' and m[0][0] == 0:
            drew21(0, 0)
        elif m[2][2] == 'o' and m[0][0] == 'o' and m[1][1] == 0:
            drew21(1, 1)
        elif m[0][2] == 'o' and m[1][1] == 'o' and m[2][0] == 0:
            drew21(2, 0)
        elif m[2][0] == 'o' and m[1][1] == 'o' and m[0][2] == 0:
            drew21(0, 2)
        elif m[2][2] == 'o' and m[0][2] == 'o' and m[1][1] == 0:
            drew21(1, 1)
        else:
            choice_randomaly()

def choice_randomaly():
    global m,c1
    if m[0][0]!='x' and m[0][2]!='x' and m[2][0]!='x' and m[2][2]!='x':
        c= [[0, 0], [0, 2], [2, 0], [2, 2]]
        while 1:
            row, colum = c[randrange(4)]
            if m[row][colum] == 0:
                break
    else:
        while 1:
            row,colum=randrange(3),randrange(3)
            if m[row][colum] == 0:
                break
    drew21(row,colum)

def play_computer(event=1):
    global m,counter
    try_won()
    counter+=1
    chick_won()
    who_to_play()

def them_(event=1):
    global them,u1
    u1 = randrange(10)
    drew_lines(them[u1][1])
    c.configure(background=them[u1][1])
    c1.configure(background=them[u1][0])

def radcall():
    global counter
    radva = radvar.get()
    if radva == 0:
        counter = 0
    elif radva == 1:
        counter = 1

def delet_():

    c1.delete(x1, ALL)
    drew_lines(them[u1][1])

def chick_won():
    global xp,op, counter, cot,m,them,u1,cox
    cox+=1
    if (m[0][0]=='o' and m[0][1]=='o' and m[0][2]=='o') or(m[1][0]=='o' and m[1][1]=='o' and m[1][2]=='o') or(m[2][0]=='o' and m[2][1]=='o' and m[2][2]=='o')or(m[0][0]=='o' and m[1][1]=='o' and m[2][2]=='o')or(m[0][2]=='o' and m[1][1]=='o' and m[2][0]=='o')or(m[0][0]=='o' and m[1][0]=='o' and m[2][0]=='o')or(m[0][1]=='o' and m[1][1]=='o' and m[2][1]=='o')or(m[0][2]=='o' and m[1][2]=='o' and m[2][2]=='o'):
        op+=1
        owin.configure(text="O\n{}".format(op))
        c1.after(1000,delet_)
        counter=0
        cot=0
        cox=0
        rad2.select()
        m = [[0, 0, 0],
             [0, 0, 0],
             [0, 0, 0]]
    elif (m[0][0]=='x' and m[0][1]=='x' and m[0][2]=='x') or(m[1][0]=='x' and m[1][1]=='x' and m[1][2]=='x') or(m[2][0]=='x' and m[2][1]=='x' and m[2][2]=='x')or(m[0][0]=='x' and m[1][1]=='x' and m[2][2]=='x')or(m[0][2]=='x' and m[1][1]=='x' and m[2][0]=='x')or(m[0][0]=='x' and m[1][0]=='x' and m[2][0]=='x')or(m[0][1]=='x' and m[1][1]=='x' and m[2][1]=='x')or(m[0][2]=='x' and m[1][2]=='x' and m[2][2]=='x'):
        xp += 1
        xwin.configure(text="X\n{}".format(xp))
        c1.after(600, delet_)
        counter,cot,cox= 1,0,0
        m = [[0, 0, 0],
             [0, 0, 0],
             [0, 0, 0]]
        drew_lines(them[u1][1])
        rad3.select()
        cox=0
    elif cox == 9:
        c1.after(600, delet_)
        counter,cot,cox = 0,0,0
        m = [[0, 0, 0],
             [0, 0, 0],
             [0, 0, 0]]
        drew_lines(them[u1][1])
    won()

def won():
    global xp,op,them,u1,counter
    if xp > op:
        xwin.configure(background='green')
        owin.configure(background='red')

    elif op > xp:
        owin.configure(background='green')
        xwin.configure(background='red')


    elif op ==xp:
        owin.configure(background=them[u1][0])
        xwin.configure(background=them[u1][0])

def c_clean(event,):
    c.delete(ALL)

def play_1(event):
    global cot,u
    u = change_color()
    if cot ==0:
        c.delete(x1,ALL)
    elif event.y > 250:
        c.configure(background=u)
    else:
        x, y, r = event.x, event.y, randrange(1, 40, 10)
        if cot % 2 == 0:
            c.create_oval(x - r, y - r, x + r, y + r, width=randrange(15, 30, 5), outline=change_color())
        else:
            c.create_line(x + r, y - r, x - r, y + r, width=randrange(15, 30, 5), fill=change_color())
            c.create_line(x - r, y - r, x + r, y + r, width=randrange(15, 30, 5), fill=change_color())
    cot+=1

def Exit():
    #c1.bind("<Button-1>",o)
    global cot,counter,xp,op,m
    cot, counter,xp,op= 0, 0, 0, 0
    m = [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]
    owin.configure(text="""O
        0        """,background='cyan')
    xwin.configure(text="""X
        0        """,background='cyan')
    c1.configure(height=30, width=600)
    c.configure(height=300, width=600)
    drew_ox(20)
    b1.configure(command=xo,text='Play')
    c1.delete(x1,ALL)
    xwin.destroy()
    owin.destroy()
    rad2.destroy()
    rad3.destroy()
    rad1.destroy()

def xo():
    global u1,them,counter,cox
    c1.bind("<Button-1>", two_players)
    cox=0
    b1.configure(command=Exit,text='Exit')
    c1.delete(x1,ALL)
    c.configure(height=30, width=600)
    c1.configure(height=300, width=600)
    c.delete(x1,ALL)
    x1.after(40,drew_inf)
    drew_lines(them[u1][1])
    counter=0

def change_color():
    '''داله اختيار لون عشوائي'''
    c=randrange(7)
    p=randrange(200000,999999,76549)
    colors=['cyan','green','brown','gray','dark gray','orange','purple']
    co = colors[c]
    #return '#'+str(p)
    return co

def change_color_xo():
    '''داله اختيار لون عشوائي'''
    c=randrange(5)
    colors=['dark grey','red','black','yellow','white','blue']
    co = colors[c]
    return co

def drew_x(event,ca):
    rad2.select()
    u=change_color_xo()
    ca.create_line(int(event.x)+15,int(event.y)-15,int(event.x)-15,int(event.y)+15,width=20,fill=u)
    ca.create_line(int(event.x)-15,int(event.y)-15,int(event.x)+15,int(event.y)+15,width=20,fill=u)

def drew_o(event,ca):
    rad3.select()
    ca.create_oval(int(event.x)-15,int(event.y)-15,int(event.x)+15,int(event.y)+15,width=10,outline=change_color_xo())

def drew_ox(i):
    for i in range(i):
        x,y,r=randrange(10,600),randrange(10,600),randrange(1,40,10)
        c.create_oval(x-r,y-r,x+r,y+r,width=randrange(15,30,5),outline=change_color())
        x,y,r=randrange(10,600),randrange(10,600),randrange(40)
        c.create_line(x+r,y-r,x-r,y+r,width=randrange(15,30,5),fill=change_color())
        c.create_line(x-r,y-r,x+r,y+r,width=randrange(15,30,5),fill=change_color())

def drew_lines(color):
    c1.create_line(250, 30, 250, 240, width=5, fill=color)
    c1.create_line(350, 30, 350, 240, width=5, fill=color)
    c1.create_line(170, 90, 450, 90, width=5, fill=color)
    c1.create_line(170, 170, 450, 170, width=5, fill=color)

def drew21(row,colum):
    row,colum=row,colum
    u = change_color_xo()
    c1.create_line(((colum * 100) + 200) + 15, (30 + (row * 100)) - 15, ((colum * 100) + 200) - 15,
                   (30 + (row * 100)) + 15, width=20, fill=u)
    c1.create_line(((colum * 100) + 200) - 15, (30 + (row * 100)) - 15, ((colum * 100) + 200) + 15,
                   (30 + (row * 100)) + 15, width=20, fill=u)
    m[row][colum] = 'x'

def drew_(event=1):
    global m,counter
    if 0:
        pass
    else:
        if event.y > 250 or event.x > 248 and event.x < 253 or event.x > 347 and event.x < 352 or event.y > 167 and event.y < 173 or event.y > 87 and event.y < 93:
            them_(event)
        if (event.y > 30 and event.y < 85 and (event.x > 170 and event.x < 245)):
             r,c=0,0
             if m[r][c] == 0:
                 drew_o(event, c1)
                 m[r][c] = 'o'
                 counter = 1
                 chick_won()
             if sele.get() == 1:
                 who_to_play()
             else:
                 two_players()
        elif (event.y > 30 and event.y < 85 and (event.x > 250 and event.x < 345)):
            r, c = 0, 1
            if m[r][c] == 0:
                drew_o(event, c1)
                m[r][c] = 'o'
                counter = 1
                chick_won()
                if sele.get() == 1:
                    who_to_play()
                else:
                    two_players()
        elif (event.y > 30 and event.y < 85 and (event.x > 350 and event.x < 445)):
            r, c = 0, 2
            if m[r][c] == 0:
                drew_o(event, c1)
                m[r][c] = 'o'
                counter = 1
                chick_won()
                if sele.get() == 1:
                    who_to_play()
                else:
                    two_players()
        elif (event.y > 90 and event.y < 160 and (event.x > 170 and event.x < 245)):
            r, c = 1, 0
            if m[r][c] == 0:
                drew_o(event, c1)
                m[r][c] = 'o'
                counter = 1
                chick_won()
                if sele.get() == 1:
                    who_to_play()
                else:
                    two_players()
        elif (event.y > 90 and event.y < 160 and (event.x > 250 and event.x < 345)):
            r, c = 1, 1
            if m[r][c] == 0:
                drew_o(event, c1)
                m[r][c] = 'o'
                counter = 1
                chick_won()
                if sele.get() == 1:
                    who_to_play()
                else:
                    two_players()
        elif (event.y > 90 and event.y < 160 and (event.x > 350 and event.x < 445)):
            r, c = 1, 2
            if m[r][c] == 0:
                drew_o(event, c1)
                m[r][c] = 'o'
                counter = 1
                chick_won()
                if sele.get() == 1:
                    who_to_play()
                else:
                    two_players()
        elif (event.y > 150 and event.y < 220 and (event.x > 170 and event.x < 245)):
            r, c = 2, 0
            if m[r][c] == 0:
                drew_o(event, c1)
                m[r][c] = 'o'
                counter = 1
                chick_won()
                if sele.get() == 1:
                    who_to_play()
                else:
                    two_players()
        elif (event.y > 150 and event.y < 220 and (event.x > 250 and event.x < 345)):
            r, c = 2, 1
            if m[r][c] == 0:
                drew_o(event, c1)
                m[r][c] = 'o'
                counter = 1
                chick_won()
                if sele.get() == 1:
                    who_to_play()
                else:
                    two_players()
        elif (event.y > 150 and event.y < 220 and (event.x > 350 and event.x < 445)):
            r, c = 2, 2
            if m[r][c] == 0:
               drew_o(event, c1)
               m[r][c] = 'o'
               counter = 1
               chick_won()
               if sele.get() == 1:
                    who_to_play()
               else:
                    two_players()
        else:
            pass

def drew__(event):
    global m,counter
    if event.y > 250 or event.x > 248 and event.x < 253 or event.x > 347 and event.x < 352 or event.y > 167 and event.y < 173 or event.y > 87 and event.y < 93:
        them_(event)
    if (event.y > 30 and event.y < 85 and (event.x > 170 and event.x < 245)):
       r,c=0,0
       if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter = 0
           chick_won()
           two_players()
    elif (event.y > 30 and event.y < 85 and (event.x > 250 and event.x < 345)):
       r, c = 0, 1
       if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter = 0
           chick_won()
           two_players()
    elif (event.y > 30 and event.y < 85 and (event.x > 350 and event.x < 445)):
        r, c = 0, 2
        if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter=0
           chick_won()
           two_players()
    elif (event.y > 90 and event.y < 160 and (event.x > 170 and event.x < 245)):
        r, c = 1, 0
        if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter=0
           chick_won()
           two_players()
    elif (event.y > 90 and event.y < 160 and (event.x > 250 and event.x < 345)):
        r, c = 1, 1
        if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter=0
           chick_won()
           two_players()
    elif (event.y > 90 and event.y < 160 and (event.x > 350 and event.x < 445)):
        r, c = 1, 2
        if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter=0
           chick_won()
           two_players()
    elif (event.y > 150 and event.y < 220 and (event.x > 170 and event.x < 245)):
        r, c = 2, 0
        if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter=0
           chick_won()
           two_players()
    elif (event.y > 150 and event.y < 220 and (event.x > 250 and event.x < 345)):
        r, c = 2, 1
        if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter=0
           chick_won()
           two_players()
    elif (event.y > 150 and event.y < 220 and (event.x > 350 and event.x < 445)):
        r, c = 2, 2
        if m[r][c] == 0:
           drew_x(event, c1)
           m[r][c] = 'x'
           counter=0
           chick_won()
           two_players()
    else:
        pass

def drew(event,r,c):
    global counter, c1, l

    if counter % 2 == 0:
        drew_o(event, c1)
        counter += 1
        m[r][c] = 'o'
    elif counter % 2 != 0:
        play_computer()
        m[r][c] = 'x'

def drew_inf():
    global rad1,rad2, rad3, owin, xwin,counter
   # rad1=Checkbutton(text='play with computer', variable=sele, command=change_select)
    rad2 = Radiobutton(x1, text='', variable=radvar, value=0, command=radcall)
    rad3 = Radiobutton(x1, text='', variable=radvar, value=1, command=radcall)
    owin = Label(text="O\n0", background='cyan')
    xwin = Label(text="X\n0", background='cyan')
    owin.grid(column=0, row=1,ipadx=20,ipady=3)
    xwin.grid(column=2, row=1,ipadx=20,ipady=3)
    rad3.grid(column=2, row=2)
    #rad3.select()
    counter=0
    rad2.grid(column=0, row=2)
    rad1.grid(column=0,columnspan=3,row=7,sticky='w')

def change_select():
    global selcet_computer,them,u1,op,xp,counter,cot,cox,m

    selectvar = sele.get()
    counter = 0
    cot = 0
    cox = 0
    op=0
    xp=0
    xwin.configure(background=them[u1][0])
    owin.configure(background=them[u1][0])
    owin.configure(text="O\n{}".format(op))
    xwin.configure(text="X\n{}".format(xp))
    c1.delete(x1, ALL)
    drew_lines(them[u1][1])
    m = [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]
    if selectvar == 1:
        c1.bind("<Button-1>", who_to_play)
    else:
        selcet_computer = 0
        c1.bind("<Button-1>",two_players)

def About():
    a=msg.showinfo('Hello Word','Hello Word \n I Have Develope this simple X/O Game and I hope you engoy It \n by Eng.Mahfoud Mohammed Binsabbah \n2020 ')
    b=msg.askyesno('????','Do you like this game?\nGive me start on github repository,you can clone the repo it\'s okay.')
    if b !=0:
       webbrowser.open('https://github.com/Mahfoud-Sa/XO_Game.git')

def change_BackGround():
    them_()
    #a=msg.showinfo('Take it easy','You can change the them \nby pressing down the xo plan')

#=======The main game program======#
x1= Tk()
x1.title('X/O')
path_to_img = path.abspath(path.join(path.dirname(__file__), 'icon.png'))
x1.iconphoto(False, PhotoImage(file=path_to_img))
#x1.iconbitmap("assets/icons/icon.ico")
x1.resizable(0,0)
menu_bar=Menu(x1)
x1.configure(menu=menu_bar)

Help_=Menu(menu_bar,tearoff=0)
Help_.add_command(label='Chang BackGround Them',command=change_BackGround)
Help_.add_command(label='About',command=About)
Help_.add_separator()
Help_.add_command(label='Exit',command=x1.destroy)
menu_bar.add_cascade(label='Help',menu=Help_)
s1=Label(text='Hello Word',font='italian',relief='groove')
b1=Button(x1,text='Play',font='italian',command=xo)
c=Canvas(height=300,width=600,background='cyan')
c1=Canvas(height=30, width=600, background='gray')

s2 = Label(text='...x=')
sele=IntVar()
radvar=IntVar()
###
drew_ox(20)
c.bind("<Button>",play_1)
#c.bind("<Button-3>",c_clean)
c.bind("<Button-3>",c_clean)


#المواقع
s1.grid(column=1,row=0)
b1.grid(column=1,row=1,rowspan=1,ipadx=9)

c.grid(column=0,row=4,columnspan=3)
c1.grid(column=0, row=5, columnspan=3)

x1.mainloop()
#الاصدار 0,4
#محفوظ محمد بن سباح
