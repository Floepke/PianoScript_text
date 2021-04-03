### IMPORTS ###
from tkinter import PhotoImage, Tk, Text, PanedWindow, Canvas, Scrollbar, Menu, filedialog, END, messagebox, simpledialog, EventType, colorchooser, Label, Button, INSERT
import platform, subprocess, os, datetime, sys, threading, rtmidi, math

### GUI ###
#colors
_bg = '#aaaaaa' #d9d9d9
papercolor = '#fefff0'
midinotecolor = '#b4b4b4'#b4b4b4
def choose_midi_color():
    global midinotecolor
    midinotecolor = colorchooser.askcolor(title ="Choose color", parent=root)[1]
    render('q', papercolor)


# Root
root = Tk()
root.title('PianoScript')
scrwidth = root.winfo_screenwidth()
scrheight = root.winfo_screenheight()
root.geometry(f"{int(scrwidth / 1.5)}x{int(scrheight / 1.25)}+{int(scrwidth / 6)}+{int(scrheight / 12)}")
# PanedWindow
orient = 'h'
# master
panedmaster = PanedWindow(root, orient='v', sashwidth=20, relief='flat', bg=_bg, sashcursor='arrow')
panedmaster.place(relwidth=1, relheight=1)
uppanel = PanedWindow(panedmaster, height=10000, relief='flat', bg=_bg)
panedmaster.add(uppanel)
downpanel = PanedWindow(panedmaster, relief='flat', bg=_bg)
panedmaster.add(downpanel)
	# editor pane
paned = PanedWindow(uppanel, relief='flat', sashwidth=20, sashcursor='arrow', orient='h', bg=_bg)
uppanel.add(paned)
		# Left Panel
leftpanel = PanedWindow(paned, relief='flat', width=1350, bg=_bg)
paned.add(leftpanel)
		# Right Panel
rightpanel = PanedWindow(paned, sashwidth=15, sashcursor='arrow', relief='flat', bg=_bg)
paned.add(rightpanel)
# Canvas --> leftpanel
canvas = Canvas(leftpanel, bg=_bg, relief='flat')
canvas.place(relwidth=1, relheight=1)
vbar = Scrollbar(canvas, orient='vertical', width=20, relief='flat', bg=_bg)
vbar.pack(side='right', fill='y')
vbar.config(command=canvas.yview)
canvas.configure(yscrollcommand=vbar.set)
hbar = Scrollbar(canvas, orient='horizontal', width=20, relief='flat', bg=_bg)
hbar.pack(side='bottom', fill='x')
hbar.config(command=canvas.xview)
canvas.configure(xscrollcommand=hbar.set)
# piano-keyboard-canvas
piano = Canvas(downpanel, bg='grey', relief='flat')
downpanel.add(piano)
# linux zoom
def bbox_offset(bbox):
        x1, y1, x2, y2 = bbox
        return (x1-40, y1-40, x2+40, y2+40)
def scrollD(event):
    canvas.yview('scroll', int(event.y/200), 'units')
    #canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
def scrollU(event):
    canvas.yview('scroll', -abs(int(event.y/200)), 'units')
    #canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
def zoomerP(event):
    canvas.scale("all", event.x, event.y, 1.1, 1.1)
    canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
def zoomerM(event):
    canvas.scale("all", event.x, event.y, 0.9, 0.9)
    canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
canvas.bind("<5>", scrollD)
canvas.bind("<4>", scrollU)
canvas.bind("<1>", zoomerP)
canvas.bind("<3>", zoomerM)

if platform.system() == 'Darwin':
    def _on_mousewheel(event):
        canvas.yview_scroll(-1*(event.delta), "units")
    canvas.bind("<MouseWheel>", _on_mousewheel)
# text --> rightpanel
textw = Text(rightpanel, foreground='black', background=_bg, insertbackground='red')
textw.place(relwidth=1, relheight=1)
textw.focus_set()
fontsize = 16
textw.configure(font=('Terminal', fontsize))
# openfiledialog
try:
    try:
        root.tk.call('tk_getOpenFile', '-foobarbaz')
    except TclError:
        pass

    root.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
    root.tk.call('set', '::tk::dialog::file::showHiddenVar', '1')
except:
    pass

fscreen = 0
def fullscreen(s):
    print('fullscreen')
    global fscreen
    if fscreen == 1:
        root.wm_attributes('-fullscreen', 0)
        fscreen = 0
    else:
        root.wm_attributes('-fullscreen', 1)
        fscreen = 1
    return


def menufullscreen():
    fullscreen('q')


orient = 0
def switch_orientation():
    global orient
    if orient == 0:
        paned.configure(orient='v')
        orient = 1
    elif orient == 1:
        paned.configure(orient='h')
        orient = 0

    





### MAIN CODE ###

##########################################################################
## File management                                                      ##
##########################################################################














starttemplate = '''//titles:
~title{music title}
~composer{music composer}
~copyright{public license 2021}

//grid:
~meas{4/4 4 35}

//settings:
~mpline{5}
~scale{150}
~systemspace{90}

// music: //
~hand{R}
_1 


~hand{L}
_1 '''

file = textw.get('1.0', END + '-1c')
filepath = ''


def new_file():
    print('new_file')
    global filepath
    if get_file() > '':
        save_quest()
    textw.delete('1.0', END)
    textw.insert('1.0', starttemplate, 'r')
    root.title('PianoScript - New')
    filepath = 'New'
    render('q', papercolor)
    return


def open_file():
    print('open_file')
    global filepath
    save_quest()
    f = filedialog.askopenfile(parent=root, mode='rb', title='Open', filetypes=[("PianoScript files","*.pnoscript")])
    if f:
        filepath = f.name
        root.title(f'PianoScript - {filepath}')
        textw.delete('1.0', END)
        textw.insert('1.0', f.read())
        render('q', papercolor)
    return


def save_file():
    print('save_file')
    if filepath == 'New':
        save_as()
        return
    else:
        f = open(filepath, 'w')
        f.write(get_file())
        f.close()


def save_as():
    global filepath
    f = filedialog.asksaveasfile(mode='w', parent=root, filetypes=[("PianoScript files","*.pnoscript")])
    if f:
        f.write(get_file())
        f.close()
        filepath = f.name
        root.title(f'PianoScript - {filepath}')
    return


def quit_editor():
    print('quit_editor')
    if filepath == 'New':
        save_quest()
    else:
        save_file()
    root.destroy()



def save_quest():
    if messagebox.askyesno('Wish to save?', 'Do you wish to save the current file?'):
        save_file()
    else:
        return


def get_file():
    global file
    file = textw.get('1.0', END + '-1c')
    return file


def def_score_settings():
    '''
    This function opens the preferences(default score settings)
    inside the GUI text editor
    '''
    save_quest()
    confexst = path.exists("config.ini")
    print(confexst)



















##########################################################################
## Tools                                                                ##
##########################################################################
def strip_file_from_comments(f):
    fl = ''
    for i in f.split('\n'):
        find = i.find('//')
        if find >= 0:
            i = i[:find]
            fl += i+'\n'
        else:
            fl += i+'\n'

    f = ''
    for i in fl.split('\n'):
        if i == '':
            pass
        else:
            f += i+'\n'
    return f


def duration_converter(string): # converts duration string to length in 'pianotick' format.

    calc = ''

    for i in string:
        if i == 'W':
            calc += '1024'
        if i == 'H':
            calc += '512'
        if i == 'Q':
            calc += '256'
        if i == 'E':
            calc += '128'
        if i == 'S':
            calc += '64'
        if i == 'T':
            calc += '32'
        if i == '+':
            calc += '+'
        if i == '-':
            calc += '-'
        if i == '*':
            calc += '*'
        if i == '/':
            calc += '/'
        if i == '(':
            calc += '('
        if i == ')':
            calc += ')'
        if i == '.':
            calc += '.'
        if i in ['0','1','2','3','4','5','6','7','8','9']:
            calc += i

    dur = None

    try:
        dur = eval(calc)
    except SyntaxError:
        print(f'wrong duration: {string}')
        return 0

    return dur


def string2pitch(string):
    '''dictionary that gives back the piano-key-number.'''
    pitchdict = {
    # Oct 0
    'a0':1, 'A0':2, 'z0':2, 'b0':3,
    # Oct 1
    'c1':4, 'C1':5, 'q1':5, 'd1':6, 'D1':7, 'w1':7, 'e1':8, 'f1':9, 'F1':10, 'x1':10, 'g1':11, 'G1':12, 'y1':12, 'a1':13, 'A1':14, 'z1':14, 'b1':15,
    # Oct 2
    'c2':16, 'C2':17, 'q2':17, 'd2':18, 'D2':19, 'w2':19, 'e2':20, 'f2':21, 'F2':22, 'x2':22, 'g2':23, 'G2':24, 'y2':24, 'a2':25, 'A2':26, 'z2':26, 'b2':27,
    # Oct 3
    'c3':28, 'C3':29, 'q3':29, 'd3':30, 'D3':31, 'w3':31, 'e3':32, 'f3':33, 'F3':34, 'x3':34, 'g3':35, 'G3':36, 'y3':36, 'a3':37, 'A3':38, 'z3':38, 'b3':39,
    # Oct 4
    'c4':40, 'C4':41, 'q4':41, 'd4':42, 'D4':43, 'w4':43, 'e4':44, 'f4':45, 'F4':46, 'x4':46, 'g4':47, 'G4':48, 'y4':48, 'a4':49, 'A4':50, 'z4':50, 'b4':51,
    # Oct 5
    'c5':52, 'C5':53, 'q5':53, 'd5':54, 'D5':55, 'w5':55, 'e5':56, 'f5':57, 'F5':58, 'x5':58, 'g5':59, 'G5':60, 'y5':60, 'a5':61, 'A5':62, 'z5':62, 'b5':63,
    # Oct 6
    'c6':64, 'C6':65, 'q6':65, 'd6':66, 'D6':67, 'w6':67, 'e6':68, 'f6':69, 'F6':70, 'x6':70, 'g6':71, 'G6':72, 'y6':72, 'a6':73, 'A6':74, 'z6':74, 'b6':75,
    # Oct 7
    'c7':76, 'C7':77, 'q7':77, 'd7':78, 'D7':79, 'w7':79, 'e7':80, 'f7':81, 'F7':82, 'x7':82, 'g7':83, 'G7':84, 'y7':84, 'a7':85, 'A7':86, 'z7':86, 'b7':87,
    # Oct 8
    'c8':88
    }
    ret = pitchdict[string]
    return ret


def barline_pos_list(gridlist):
    '''Returns a list of the position of every barline.'''
    barlinepos = [0]
    for grid in gridlist:
        cntr = 0
        for i in range(grid[2]):
            nxtbarln = barlinepos[-1] + grid[0]
            barlinepos.append(nxtbarln)
    return barlinepos


def newline_pos_list(gridlist, mpline):
    '''returns a list of the position of every new line/system of music.'''
    gridlist = barline_pos_list(gridlist)
    linelist = [0]
    cntr = 0
    for barline in range(len(gridlist)):
        try: cntr += mpline[barline]
        except IndexError:
            cntr += mpline[-1]
        try: linelist.append(gridlist[cntr])
        except IndexError:
            linelist.append(gridlist[-1])
            break
    if linelist[-1] == linelist[-2]:
        linelist.remove(linelist[-1])

    linelist.pop(0)

    return linelist


def staff_height(mn, mx):
    '''
    This function returns the height of a staff based on the
    lowest and highest piano-key-number.
    '''
    staffheight = 0

    if mx >= 81:
        staffheight = 225
    if mx >= 76 and mx <= 80:
        staffheight = 190
    if mx >= 69 and mx <= 75:
        staffheight = 165
    if mx >= 64 and mx <= 68:
        staffheight = 130
    if mx >= 57 and mx <= 63:
        staffheight = 105
    if mx >= 52 and mx <= 56:
        staffheight = 70
    if mx >= 45 and mx <= 51:
        staffheight = 45
    if mx >= 40 and mx <= 44:
        staffheight = 10
    if mx < 40:
        staffheight = 10
    if mn >= 33 and mn <= 39:
        staffheight += 35
    if mn >= 28 and mn <= 32:
        staffheight += 60
    if mn >= 21 and mn <= 27:
        staffheight += 95
    if mn >= 16 and mn <= 20:
        staffheight += 120
    if mn >= 9 and mn <= 15:
        staffheight += 155
    if mn >= 4 and mn <= 8:
        staffheight += 180
    if mn >= 1 and mn <= 3:
        staffheight += 195
    return staffheight


def draw_staff_lines(y, mn, mx):
    '''
    'y' takes the y-position of the uppper line of the staff.
    'mn' and 'mx' take the lowest and highest note in the staff
    so the function can draw the needed lines.
    '''

    def draw3Line(y):
        x = marginx_start
        canvas.create_line(x, y, x+(paperwidth-marginsx-marginsx), y, width=2)
        canvas.create_line(x, y+10, x+(paperwidth-marginsx-marginsx), y+10, width=2)
        canvas.create_line(x, y+20, x+(paperwidth-marginsx-marginsx), y+20, width=2)


    def draw2Line(y):
        x = marginx_start
        canvas.create_line(x, y, x+(paperwidth-marginsx-marginsx), y, width=0.5)
        canvas.create_line(x, y+10, x+(paperwidth-marginsx-marginsx), y+10, width=0.5)


    def drawDash2Line(y):
        x = marginx_start
        canvas.create_line(x, y, x+(paperwidth-marginsx-marginsx), y, width=1, dash=(6,6))
        canvas.create_line(x, y+10, x+(paperwidth-marginsx-marginsx), y+10, width=1, dash=(6,6))

    keyline = 0
    staffheight = 0

    if mx >= 81:
        draw3Line(0+y)
        draw2Line(35+y)
        draw3Line(60+y)
        draw2Line(95+y)
        draw3Line(120+y)
        draw2Line(155+y)
        draw3Line(180+y)
        keyline = 215
    if mx >= 76 and mx <= 80:
        draw2Line(0+y)
        draw3Line(25+y)
        draw2Line(60+y)
        draw3Line(85+y)
        draw2Line(120+y)
        draw3Line(145+y)
        keyline = 180
    if mx >= 69 and mx <= 75:
        draw3Line(0+y)
        draw2Line(35+y)
        draw3Line(60+y)
        draw2Line(95+y)
        draw3Line(120+y)
        keyline = 155
    if mx >= 64 and mx <= 68:
        draw2Line(0+y)
        draw3Line(25+y)
        draw2Line(60+y)
        draw3Line(85+y)
        keyline = 120
    if mx >= 57 and mx <= 63:
        draw3Line(0+y)
        draw2Line(35+y)
        draw3Line(60+y)
        keyline = 95
    if mx >= 52 and mx <= 56:
        draw2Line(0+y)
        draw3Line(25+y)
        keyline = 60
    if mx >= 45 and mx <= 51:
        draw3Line(0+y)
        keyline = 35

    drawDash2Line(keyline+y)

    if mn >= 33 and mn <= 39:
        draw3Line(keyline+25+y)
    if mn >= 28 and mn <= 32:
        draw3Line(keyline+25+y)
        draw2Line(keyline+60+y)
    if mn >= 21 and mn <= 27:
        draw3Line(keyline+25+y)
        draw2Line(keyline+60+y)
        draw3Line(keyline+85+y)
    if mn >= 16 and mn <= 20:
        draw3Line(keyline+25+y)
        draw2Line(keyline+60+y)
        draw3Line(keyline+85+y)
        draw2Line(keyline+120+y)
    if mn >= 9 and mn <= 15:
        draw3Line(keyline+25+y)
        draw2Line(keyline+60+y)
        draw3Line(keyline+85+y)
        draw2Line(keyline+120+y)
        draw3Line(keyline+145+y)
    if mn >= 4 and mn <= 8:
        draw3Line(keyline+25+y)
        draw2Line(keyline+60+y)
        draw3Line(keyline+85+y)
        draw2Line(keyline+120+y)
        draw3Line(keyline+145+y)
        draw2Line(keyline+180+y)
    if mn >= 1 and mn <= 3:
        draw3Line(keyline+25+y)
        draw2Line(keyline+60+y)
        draw3Line(keyline+85+y)
        draw2Line(keyline+120+y)
        draw3Line(keyline+145+y)
        draw2Line(keyline+180+y)
        canvas.create_line(marginx_start, keyline+205+y, marginx_start+(paperwidth-marginsx-marginsx), keyline+205+y, width=2)


def draw_papers(y, papercol):
    '''draws the paper.'''
    #canvas.create_rectangle(55, 55+y, 55+paperwidth, 55+paperheigth+y, fill='black', outline='')
    canvas.create_rectangle(40, 50+y, 40+paperwidth, 50+paperheigth+y, fill=papercol, outline='')
    #canvas.create_rectangle(70, 70+y, 70+printareawidth, 70+printareaheight+y, fill='', outline='blue')


### noteheads ###
def black_key_right(x, y):  # center coordinates, radius
    '''draws a black key on the given x/y with a stem attached.'''
    x0 = x
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    canvas.create_line(x0,y-20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black')


def black_key_right_bf(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x - 10
    y1 = y + 5
    canvas.create_line(x0,y-20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black')


def white_key_right_dga(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 10
    y1 = y + 5
    canvas.create_line(x0,y-20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')


def white_key_right_cefb(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 3.5
    x1 = x + 10
    y1 = y + 3.5
    canvas.create_line(x0,y-20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')


def black_key_left(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    canvas.create_line(x0,y+20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black') # point
    canvas.create_oval(x0+3, y0+4, x1-3, y1-4, outline='white', fill='white') # point
    #canvas.create_polygon(x, y+5, x+10, y, x, y-5, outline='black', fill='black') # triangle
    #canvas.create_polygon(x, y+5, x+5, y, x, y-5, outline='black', fill='black') # diamond
    #canvas.create_oval(x0+3, y0+4, x1-3, y1-4, outline='', fill='white')


def black_key_left_bf(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x - 10
    y1 = y + 5
    canvas.create_line(x0,y+20, x0,y, width=2)
    # canvas.create_polygon(x, y, x+5, y+5, x+10, y, x+5, y-5, outline='black', fill='black') # triangle
    #canvas.create_oval(x0-3, y0+4, x1+3, y1-4, outline='', fill='white')


def white_key_left_dga(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 10
    y1 = y + 5
    canvas.create_line(x0,y+20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white') # point
    canvas.create_oval(x0+4, y0+4, x1-4, y1-4, outline="", fill='black') # point
    #canvas.create_polygon(x, y, x+5, y+5, x+10, y, x+5, y-5, outline="black", width=2, fill='white') # diamond
    #canvas.create_polygon(x, y+5, x+10, y, x, y-5, outline="black", width=2, fill='white') # triangle
    #canvas.create_oval(x0+4, y0+4, x1-4, y1-4, outline="", fill='black')


def white_key_left_cefb(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 3.5
    x1 = x + 10
    y1 = y + 3.5
    canvas.create_line(x0,y+20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white') # point
    canvas.create_oval(x0+4, y0+4.5, x1-4, y1-4.5, outline="", fill='black') # point
    #canvas.create_polygon(x, y, x+5, y+3.5, x+10, y, x+5, y-3.5, outline="black", width=2, fill='white') # diamond
    #canvas.create_polygon(x, y+3.5, x+10, y, x, y-3.5, outline="black", width=2, fill='white') # triangle
    #canvas.create_oval(x0+4, y0+4.5, x1-4, y1-4.5, outline="", fill='black')


def note_stop(x, y):
    x += 3.5
    canvas.create_line(x-7,y-5, x, y, x-7,y+5, width=2, smooth=1) # orginal klavarscribo design
    #canvas.create_line(x,y, x,y+5, x,y+5, x,y-5, x,y-5, x,y, x,y, x-5,y+5, x-5,y+5, x,y, x,y, x-5,y-5, fill='black', width=1.5) # maybe the pianoscript design
    #canvas.create_line(x, y-10, x, y+10, fill='black', width=1.5, dash=3)


def note_y_pos(note, mn, mx, cursy):
    '''
    returns the position of the given note relative to 'cursy'(the y axis staff cursor).
    '''

    if mx >= 81:
        c4 = 230
    if mx >= 76 and mx <= 80:
        c4 = 195
    if mx >= 69 and mx <= 75:
        c4 = 170
    if mx >= 64 and mx <= 68:
        c4 = 135
    if mx >= 57 and mx <= 63:
        c4 = 110
    if mx >= 52 and mx <= 56:
        c4 = 75
    if mx >= 45 and mx <= 51:
        c4 = 50
    if mx >= 40 and mx <= 44:
        c4 = 15
    if mx < 40:
        c4 = 15

    return (cursy + c4) + (40 - note) * 5


def draw_note_actives(x0, x1, y, linenr):
    '''draws a midi note with a stop sign(vertical line at the end of the midi-note).'''
    x0 = event_x_pos(x0, linenr)
    x1 = event_x_pos(x1, linenr)
    canvas.create_rectangle(x0, y-5, x1, y+5, fill=midinotecolor, outline='')#e3e3e3
    canvas.create_line(x1, y-5, x1, y+5, width=2)


def event_x_pos(pos, linenr):
    '''returns the x position on the paper based on position in piano-ticks and line-number'''
    newlinepos = newline_pos_list(grid, mpline)
    newlinepos.insert(0, 0)
    linelength = newlinepos[linenr] - newlinepos[linenr-1]
    factor = (paperwidth-marginsx-marginsx) / linelength
    pos = pos - newlinepos[linenr-1]
    xpos = marginx_start + pos * factor
    return xpos


def prepare_file(string, startbracket, endbracket, replace):
    '''
    takes the raw save-file and returns the file with all commands written as '*'.
    (~command{value} becomes ~*******{*****})The reason is to ignore commands
    and read all other data without losing the right file-index-number.
    '''
    def replacer(s, newstring, index, nofail=False):
        # raise an error if index is outside of the string
        if not nofail and index not in range(len(s)):
            raise ValueError("index outside given string")

        # if not erroring, but the index is still not in the correct range..
        if index < 0:  # add it to the beginning
            return newstring + s
        if index > len(s):  # add it to the end
            return s + newstring

        # insert the new string between "slices" of the original
        return s[:index] + newstring + s[index + 1:]

    findex = -1
    for sym in string:
        findex += 1
        if sym == startbracket:
            rindex = findex
            for i in string[findex+1:]:
                rindex += 1
                if i == endbracket:
                    break
                else:
                    string = replacer(string, replace, rindex)
    return string


def repeat_dot(x, y):  # center coordinates, radius
    '''draws a repeat-dot. Used to engrave the repeat signs.'''
    x0 = x
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black')


def addmeas_processor(string):
    '''
    This function processes the ~meas{} command. It translates the time signature to length
    in piano-ticks. the function returns 'length in piano-tick', 'grid-division' and 
    'amount of measures to create'.
    '''

    def measure_length(tsig, tickperquarter):
        tsig = tsig.split('/')
        w = 0
        n = int(tsig[0])
        d = int(tsig[1])
        if d < 4:
            w = (n * d) / (d / 2)
        if d == 4:
            w = (n * d) / d
        if d > 4:
            w = (n * d) / (d * 2)
        return int(tickperquarter * w)

    string = string.split()

    length = measure_length(string[0], 256)
    grid = string[1]
    amount = string[2]

    return length, grid, amount


def diff(x, y):
    if x >= y:
        return x - y
    else:
        return y - x


def continuation_dot(x, y):
    '''
    The continuation dot is a concept where the dot is printed when another note is starting
    when the current note is still sounding. The dot remebers you that the note is still sounding.
    '''
    x0 = x - 2
    y0 = y - 2
    x1 = x + 2
    y1 = y + 2
    canvas.create_oval(x0, y0, x1, y1, fill='black', outline='black')


def create_mp_list(string):
    '''used to create a list of numbers from a string. 
    could have been written in the function where its used.'''
    string = string.split(' ')
    lst = []
    for i in string:
        lst.append(eval(i))
    return lst


def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    save_quest()
    python = sys.executable
    os.execl(python, python, * sys.argv)


def is_in_range(x, y, z):
    '''
    returns true if z is in between x and y.
    '''
    if x < z and y > z:
        return True
    else:
        return False


def get_staff_height(line):
    #create linenotelist
    linenotelist = []
    for note in line:
        if note[1] == 'note' or note[1] == 'split' or note[1] == 'invis':
            linenotelist.append(note[4])
    if linenotelist:
        minnote = min(linenotelist)
        maxnote = max(linenotelist)
    else:
        minnote = 40
        maxnote = 44
    return staff_height(minnote, maxnote), minnote, maxnote

def get_ts_pos(gridlist):
    tstimes = []
    time = 0
    for ts in gridlist:
        tstimes.append(time)
        time = ts[0]*ts[2]
    return tstimes


#-----------------
# MAIN
#-----------------
















## score variables ##
# titles:
title = ''
subtitle = ''
composer = ''
copyright = ''
# settings:
mpline = 5
systemspacing = 90
scale = 100/100
titlespace = 60
fillpage = 300 # fillpagetreshold
printtitle = 1 # on/off
printcomposer = 1 # on/off
printcopyright = 1 # on/off
measurenumbering = 1 # on/off
dotts = 0 # on/off
midirecord = 1
#keywidth = 17.5
# music:
grid = []
msg = []
pagespace = []


## constants ##
mm = root.winfo_fpixels('1m')
paperheigth = mm * 297 * (scale)  # a4 210x297 mm
paperwidth = mm * 210 * (scale)
marginsx = 40
marginsy = 60
printareawidth = paperwidth - (marginsx*2)
printareaheight = paperheigth - (marginsy*2)
marginx_start = 40 + marginsx
number2pitch = {1: 'a0', 2: 'z0', 3: 'b0',
     4: 'c1', 5: 'C1', 6: 'd1', 7: 'D1', 8: 'e1', 9: 'f1', 10: 'F1', 11: 'g1', 12: 'G1', 13: 'a1', 14: 'A1', 15: 'b1', 
     16: 'c2', 17: 'C2', 18: 'd2', 19: 'D2', 20: 'e2', 21: 'f2', 22: 'F2', 23: 'g2', 24: 'G2', 25: 'a2', 26: 'A2', 27: 'b2', 
     28: 'c3', 29: 'C3', 30: 'd3', 31: 'D3', 32: 'e3', 33: 'f3', 34: 'F3', 35: 'g3', 36: 'G3', 37: 'a3', 38: 'A3', 39: 'b3', 
     40: 'c4', 41: 'C4', 42: 'd4', 43: 'D4', 44: 'e4', 45: 'f4', 46: 'F4', 47: 'g4', 48: 'G4', 49: 'a4', 50: 'A4', 51: 'b4', 
     52: 'c5', 53: 'C5', 54: 'd5', 55: 'D5', 56: 'e5', 57: 'f5', 58: 'F5', 59: 'g5', 60: 'G5', 61: 'a5', 62: 'A5', 63: 'b5', 
     64: 'c6', 65: 'C6', 66: 'd6', 67: 'D6', 68: 'e6', 69: 'f6', 70: 'F6', 71: 'g6', 72: 'G6', 73: 'a6', 74: 'A6', 75: 'b6', 
     76: 'c7', 77: 'C7', 78: 'd7', 79: 'D7', 80: 'e7', 81: 'f7', 82: 'F7', 83: 'g7', 84: 'G7', 85: 'a7', 86: 'A7', 87: 'b7', 
     88: 'c8'}


renderno = 0


def render(x, papercol='#fefffe'):
    global scale_S, renderno, pagespace, title, subtitle, composer, copyright, mpline, systemspacing, scale, grid, msg, paperheigth, paperwidth, marginsy, marginsx, printareaheight, printareawidth, printtitle, printcomposer, printcopyright, measurenumbering
    grid = []
    msg = []
    title = ''
    subtitle = ''
    composer = ''
    copyright = ''
    pagespace = []
    mpline = 4
    systemspacing = 90
    scale = 150
    titlespace = 60


    def reading():
        global scale_S, renderno, pagespace, title, subtitle, composer, copyright, mpline, systemspacing, scale, grid, msg, paperheigth, paperwidth, marginsy, marginsx, printareaheight, printareawidth, printtitle, printcomposer, printcopyright, measurenumbering, marginx_start
        file = strip_file_from_comments(get_file())

        msgprep = []

        # read commands ~command{value}
        cmdstring = file
        index = -1
        for sym in cmdstring:
            index += 1
            if sym == '~':
                try:
                    cmdname = ''
                    cmdstr = ''
                    for i in cmdstring[index+1:]:
                        if i == '{':
                            break
                        else:
                            cmdname += i
                    for i in cmdstring[index+1+len(cmdname)+1:]:
                        if i == '}':
                            break
                        else:
                            cmdstr += i
                    msgprep.append([index, cmdname, cmdstr])
                except: pass


        # read music
        musicstring = prepare_file(file, '~', '}', ' ')
        index = -1
        for sym in musicstring:
            index += 1
            # note
            if sym in ['a', 'A', 'b', 'c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G', 'q', 'w', 'x', 'y', 'z']:
                if musicstring[index+1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                    if musicstring[index+2] == '-':
                        msgprep.append([index, 'note', string2pitch(musicstring[index]+musicstring[index+1]), 'bound'])
                    else:
                        msgprep.append([index, 'note', string2pitch(musicstring[index]+musicstring[index+1]), 'loose'])

            # split
            if sym == '=':
                msgprep.append([index, 'split'])

            # cursor
            if sym == '_':
                dig = ''
                for i in musicstring[index+1:]:
                    if i in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        dig += i
                    else:
                        if dig == '':
                            msgprep.append([index, 'cursor', 0])
                            break
                        else:

                            msgprep.append([index, 'cursor', eval(dig)])
                            break

            # durations
            if sym == 'W':
                if musicstring[index+1] == '.' and not musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'W*1.5'])
                elif musicstring[index+1] == '.' and musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'W*1.75'])
                else:
                    msgprep.append([index, 'dur', 'W'])
            if sym == 'H':
                if musicstring[index+1] == '.' and not musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'H*1.5'])
                elif musicstring[index+1] == '.' and musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'H*1.75'])
                else:
                    msgprep.append([index, 'dur', 'H'])
            if sym == 'Q':
                if musicstring[index+1] == '.' and not musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'Q*1.5'])
                elif musicstring[index+1] == '.' and musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'Q*1.75'])
                else:
                    msgprep.append([index, 'dur', 'Q'])
            if sym == 'E':
                if musicstring[index+1] == '.' and not musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'E*1.5'])
                elif musicstring[index+1] == '.' and musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'E*1.75'])
                else:
                    msgprep.append([index, 'dur', 'E'])
            if sym == 'S':
                if musicstring[index+1] == '.' and not musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'S*1.5'])
                elif musicstring[index+1] == '.' and musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'S*1.75'])
                else:
                    msgprep.append([index, 'dur', 'S'])
            if sym == 'T':
                if musicstring[index+1] == '.' and not musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'T*1.5'])
                elif musicstring[index+1] == '.' and musicstring[index+2] == '.':
                    msgprep.append([index, 'dur', 'T*1.75'])
                else:
                    msgprep.append([index, 'dur', 'T'])

            # rest
            if sym == 'r':
                msgprep.append([index, 'rest'])


        # sort messages on index to ensure the order
        msgprep = sorted(msgprep, key=lambda x: x[0])

        #default values for events
        hand = 'R'
        duration = 256
        cursor = 0
        for event in msgprep:
            # titles
            if event[1] == 'title':
                title = event[2]

            if event[1] == 'composer':
                composer = event[2]

            if event[1] == 'copyright':
                copyright = event[2]

            # invisible note
            if event[1] == 'invis':
                try: 
                    note = string2pitch(event[2])
                    msg.append([index, 'invis', cursor, 'dummy', note, hand])
                except:
                    ...

            # printtitle
            if event[1] == 'printtitle':
                try: 
                    val = eval(event[2])
                    printtitle = val
                except:
                    ...

            # printcomposer
            if event[1] == 'printcomposer':
                try: 
                    val = eval(event[2])
                    printcomposer = val
                except:
                    ...

            # printcopyright
            if event[1] == 'printcopyright':
                try: 
                    val = eval(event[2])
                    printcopyright = val
                except:
                    ...

            # measurenumbering
            if event[1] == 'measurenumbering':
                try: 
                    val = eval(event[2])
                    measurenumbering = val
                except:
                    ...

            # addmeas
            if event[1] == 'meas':
                length, grids, amount = addmeas_processor(event[2])
                grid.append([length, eval(grids), eval(amount)])


            # slur
            if event[1] == 'slur':
                try: 
                    ystart, middle, yend = event[2].split()
                    ystart = eval(ystart)
                    middle = eval(middle)
                    yend = eval(yend)
                    msg.append([event[0], 'slur', cursor, cursor+duration, ystart, middle, yend])
                except ValueError:
                    ...
                

            # bpm
            if event[1] == 'bpm':
                msg.append([index, 'bpm', cursor, event[2]])

            # hand
            if event[1] == 'hand':
                hand = event[2]

            # mpline
            if event[1] == 'mpline':
                try: 
                    mpline = create_mp_list(event[2])
                except: pass

            # systemspace
            if event[1] == 'systemspace':
                try: systemspacing = eval(event[2])
                except: pass

            # scale
            if event[1] == 'scale':
                scale = eval(event[2])/100
                paperheigth = mm * 297 * scale # a4 210x297 mm
                paperwidth = mm * 210 * scale
                marginsx = 40 * scale
                marginsy = 60 * scale
                printareawidth = paperwidth - (marginsx - marginsx) * scale
                printareaheight = paperheigth - marginsy
                marginx_start = 40 + marginsx

            # cursor
            if event[1] == 'cursor':
                if event[2] == 0:
                    cursor -= duration
                else:
                    try: cursor = barline_pos_list(grid)[event[2]-1]
                    except IndexError: print('ERROR: cursor out of range; try increasing the measure amount')

            # duration
            if event[1] == 'dur':
                duration = duration_converter(event[2])

            # note and auto-split
            if event[1] == 'note':
                is_split = False
                splitpoints = []
                for i in barline_pos_list(grid):
                    if is_in_range(cursor, round(cursor)+round(duration), i):
                        splitpoints.append(i)
                        is_split = True

                if is_split == False:
                    msg.append([event[0], 'note', cursor, cursor+duration, event[2], hand, event[3]])
                elif is_split == True:
                    msg.append([event[0], 'note', cursor, splitpoints[0], event[2], hand, event[3]])
                    dur = duration - diff(cursor, splitpoints[0])
                    for i in range(len(splitpoints)):
                        start = splitpoints[i]
                        end = 0
                        try: 
                            end = splitpoints[i+1]
                        except IndexError:
                            msg.append([event[0], 'split', start, start+dur, event[2], hand])
                            break
                        msg.append([event[0], 'split', start, end, event[2], hand])
                        dur -= diff(start, end)

                cursor += duration

            # rest
            if event[1] == 'rest':
                cursor += duration

            # split
            if event[1] == 'split':
                notes = []
                time = 0
                for i in reversed(msg):
                    if i[1] == 'note' and notes == []:
                        notes.append(i[4])
                        time = i[2]
                    if i[1] == 'note' and i[2] == time:
                        notes.append(i[4])
                    elif i[1] == 'note' and i[2] != time:
                        break
                for i in notes:
                    msg.append([event[0], 'split', cursor, cursor+duration, i])
                cursor += duration

            # bar (all bartypes)
            if event[1] == 'bar':
                if event[2] == '|:':
                    msg.append([event[0], 'bgn_rpt', cursor])
                if event[2] == ':|':
                    msg.append([event[0], 'end_rpt', cursor-0.1])
                if event[2] == '|':
                    msg.append([event[0], 'barline', cursor])
                if event[2] == ';':
                    msg.append([event[0], 'smalldash', cursor])
                if event[2] == '[':
                    msg.append([event[0], 'bgn_hook', cursor])
                if event[2] == ']':
                    msg.append([event[0], 'end_hook', cursor-0.1])

            # text (all types)
            if event[1] == 'text':
                if event[2] == 'f':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'ff':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'fff':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'ffff':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'p':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'pp':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'ppp':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'pppp':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'mf':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                elif event[2] == 'mf':
                    msg.append([event[0], 'dynamic', cursor, event[2]])
                else:
                    msg.append([event[0], 'text', cursor, event[2]])
            if event[1] == 'textB':
                msg.append([event[0], 'textB', cursor, event[2]])
            if event[1] == 'textI':
                msg.append([event[0], 'textI', cursor, event[2]])

        # creating time signature text msg
        tspos = get_ts_pos(grid)


















        #adding barline messages with correct begin time
        for barline in barline_pos_list(grid):
            msg.insert(0, ['index', 'barline', barline])


        # adding grid messages
        icount = -1
        cursor = 0
        grdpart = []
        for i in grid:
            oldpos = 0

            for add in range(i[2]):
                length = i[0]
                divide = i[1]
                if divide == 0:
                    divide = 1
                amount = i[1]
                for line in range(amount):
                    gridpart = length / divide
                    time = cursor + (gridpart * (line+1))
                    grdpart.append(['dashline', time])
                cursor += length

        for barline in grdpart:
            msg.insert(0, ['index', 'dash', barline[1]])


        # sort on starttime of event to get the barlines in the right order
        msg.sort(key=lambda x: x[2])


        ##  placing messages in lists of 'lines' ##
        newlinepos = newline_pos_list(grid, mpline)
        msgs = msg
        msg = []
        bottpos = 0
        for newln in newlinepos:
            hlplst = []
            for note in msgs:
                if note[2] >= bottpos and note[2] < newln:
                    hlplst.append(note)
            msg.append(hlplst)
            bottpos = newln


        ## fitting the 'lines' into pages ##
        lineheight = []
        for line in msg:

            notelst = []
            for note in line:
                if note[1] == 'note' or note[1] == 'split' or note[1] == 'invis':
                    notelst.append(note[4])
                else:
                    pass
            try: lineheight.append(staff_height(min(notelst), max(notelst)))
            except ValueError: lineheight.append(10)

        msgs = msg
        msg = []
        cursy = 40 * (scale)
        pagelist = []
        icount = 0
        resspace = 0
        for line, height in zip(msgs, lineheight):
            icount += 1
            cursy += height + systemspacing
            if icount == len(lineheight):#if this is the last iteration
                if cursy <= printareaheight:
                    pagelist.append(line)
                    msg.append(pagelist)
                    resspace = printareaheight - cursy
                    pagespace.append(resspace)
                    break
                elif cursy > printareaheight:
                    msg.append(pagelist)
                    pagelist = []
                    pagelist.append(line)
                    msg.append(pagelist)
                    pagespace.append(resspace)
                    cursy = 0
                    resspace = printareaheight - cursy
                    pagespace.append(resspace)
                    break
                else:
                    pass
            else:
                if cursy <= printareaheight:#does fit on paper
                    pagelist.append(line)
                    resspace = printareaheight - cursy
                elif cursy > printareaheight:#does not fit on paper
                    msg.append(pagelist)
                    pagelist = []
                    pagelist.append(line)
                    cursy = 0
                    cursy += height + systemspacing
                    pagespace.append(resspace)
                else:
                    pass



    reading()










    def drawing():
        canvas.delete('all')

        def draw_paper():

            counter = 0
            cursy = 0

            for page in msg:
                counter += 1
                draw_papers(cursy, papercol)
                if printcopyright == 1:
                    canvas.create_text(marginx_start, cursy+20+paperheigth, text=f'page {counter} of {len(msg)} | {title} | {copyright} - PianoScript sheet', anchor='w', font=("Courier", 16, "normal"))
                #canvas.create_rectangle(70, cursy+5+paperheigth, 70+printareawidth, cursy+35+paperheigth)

                cursy += paperheigth + 50

            if printtitle == 1:
                canvas.create_text(marginx_start, 90, text=title, anchor='w', font=("Courier", 20, "normal"))
            if printcomposer == 1:
                canvas.create_text(marginx_start+printareawidth-marginsx-marginsx, 90, text=composer, anchor='e', font=("Courier", 20, "normal"))
            #canvas.create_line(10, 400, 10, 400+pagespace[1])

        def draw_note_active():
            cursy = 90 + titlespace
            lcounter = 0
            pcounter = 0
            for page in msg:
                pcounter += 1
                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    for note in line:
                        if note[1] == 'note':
                            draw_note_actives(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
                            prevnote = note[3]
                        if note[1] == 'split':
                            draw_note_actives(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
                            continuation_dot(event_x_pos(note[2], lcounter)+5, note_y_pos(note[4], minnote, maxnote, cursy))

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpage:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpage:

                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_barlines_and_text():
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            bcounter = 0

            for page in msg:
                pcounter += 1


                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    for note in line:

                        if note[1] == 'barline':
                            bcounter += 1
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight, width=2)
                            if measurenumbering == 1:
                                canvas.create_text(event_x_pos(note[2]+12.5, lcounter), cursy-20, text=bcounter, anchor='w', font=('Terminal', 14, 'normal'))

                        if note[1] == 'bgn_rpt':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40, width=2)
                            repeat_dot(event_x_pos(note[2], lcounter)+5, cursy+staffheight+15)
                            repeat_dot(event_x_pos(note[2], lcounter)+5, cursy+staffheight+30)

                        if note[1] == 'end_rpt':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40, width=2)
                            repeat_dot(event_x_pos(note[2], lcounter)-12.5, cursy+staffheight+15)
                            repeat_dot(event_x_pos(note[2], lcounter)-12.5, cursy+staffheight+30)

                        if note[1] == 'bgn_hook':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40,
                                event_x_pos(note[2], lcounter), cursy+staffheight+40, event_x_pos(note[2], lcounter)+80, cursy+staffheight+40, width=2)

                        if note[1] == 'end_hook':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40,
                                event_x_pos(note[2], lcounter), cursy+staffheight+40, event_x_pos(note[2], lcounter)-80, cursy+staffheight+40, width=2)

                        if note[1] == 'textB':
                            canvas.create_text(event_x_pos(note[2], lcounter)+10, cursy+staffheight+25, text=note[3], anchor='w', font='Helvetica 18 bold')

                        if note[1] == 'textI':
                            canvas.create_text(event_x_pos(note[2], lcounter)+10, cursy+staffheight+25, text=note[3], anchor='w', font='Helvetica 18 italic')

                        if note[1] == 'text':
                            canvas.create_text(event_x_pos(note[2], lcounter)+10, cursy+staffheight+25, text=note[3], anchor='w', font='Helvetica 18')

                        if note[1] == 'bpm':
                            canvas.create_text(event_x_pos(note[2], lcounter)+10, cursy+staffheight+25, text=f'bpm = {note[3]}', anchor='w', font='Helvetica 18')


                    canvas.create_line(marginx_start+(paperwidth-marginsx-marginsx), cursy, marginx_start+(paperwidth-marginsx-marginsx), cursy+staffheight, width=2)

                    if lcounter == len(newline_pos_list(grid, mpline)):
                        canvas.create_line(marginx_start+(paperwidth-marginsx-marginsx), cursy, marginx_start+(paperwidth-marginsx-marginsx), cursy+staffheight, width=5)


                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpage:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpage:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_staff():
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            for page in msg:
                pcounter += 1


                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)
                    
                    draw_staff_lines(cursy, minnote, maxnote)

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpage:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpage:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_note_start():
            black = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 
            48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
            white_dga = [6,11,13,18,23,25,30,35,37,42,47,49,54,59,61,66,71,73,78,83,85,88]
            white_be = [3,8,15,20,27,32,39,44,51,56,63,68,75,80,87]
            white_cf = [1,4,9,16,21,28,33,40,45,52,57,64,69,76,81]

            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            for page in msg:
                pcounter += 1

                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    notelst = []
                    for note in line:
                        if note[1] == 'note':
                            notelst.append(note)

                    notelst.sort(key=lambda x: x[0])

                    old_x = 0
                    old_y = 0
                    boundloose = 0

                    for note in notelst:
                        
                        if note[1] == 'note':
                            #note_stop(event_x_pos(note[3], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))

                            if note[4] in white_dga:

                                if note[5] == 'R':
                                    white_key_right_dga(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
                                elif note[5] == 'L':
                                    white_key_left_dga(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
                                else:
                                    pass

                            if note[4] in white_cf:

                                if note[5] == 'R':
                                    white_key_right_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)-1.5)
                                elif note[5] == 'L':
                                    white_key_left_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)-1.5)
                                else:
                                    pass

                            if note[4] in white_be:

                                if note[5] == 'R':
                                    white_key_right_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)+1.5)
                                elif note[5] == 'L':
                                    white_key_left_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)+1.5)
                                else:
                                    pass

                            if note[4] in black:


                                if note[5] == 'R':
                                    black_key_right(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
                                elif note[5] == 'L':
                                    black_key_left(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
                                else:
                                    pass


                            if boundloose == 1:
                                if note[5] == 'R':
                                    canvas.create_line(old_x, old_y, event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)-20, width=3)
                                elif note[5] == 'L':
                                    canvas.create_line(old_x, old_y, event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)+20, width=3)

                            if note[6] == 'bound':
                                boundloose = 1
                                old_x = event_x_pos(note[2], lcounter)
                                if note[5] == 'R':
                                    old_y = note_y_pos(note[4], minnote, maxnote, cursy)-20
                                elif note[5] == 'L':
                                    old_y = note_y_pos(note[4], minnote, maxnote, cursy)+20
                                else:
                                    pass
                            elif note[6] == 'loose':
                                boundloose = 0
                            else:
                                pass

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpage:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpage:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_grid_lines():
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            for page in msg:
                pcounter += 1

                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    for gridline in line:
                        if gridline[1] == 'dash':
                            canvas.create_line(event_x_pos(gridline[2],
                                                lcounter),
                                                cursy,
                                                event_x_pos(gridline[2],
                                                lcounter),
                                                cursy+staffheight,
                                                dash=(6, 6))
                        if gridline[1] == 'smalldash':
                            canvas.create_line(event_x_pos(gridline[2],
                                                lcounter),
                                                cursy+(staffheight*0.20),
                                                event_x_pos(gridline[2],
                                                lcounter),
                                                cursy+staffheight-(staffheight*0.20),
                                                dash=(2, 2))

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpage:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpage:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_slur():
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            for page in msg:
                pcounter += 1

                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    for slur in line:
                        if slur[1] == 'slur':
                            xpos2 = event_x_pos(slur[2], lcounter) + (diff(event_x_pos(slur[2], lcounter), event_x_pos(slur[3], lcounter)) / 2)
                            canvas.create_line(event_x_pos(slur[2], lcounter), cursy-20+slur[4], xpos2, cursy-20+slur[5], event_x_pos(slur[3], lcounter), cursy-20+slur[6], smooth=1, width=2.5)

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpage:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpage:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_continuation_dot():
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            for page in msg:
                pcounter += 1

                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    notelst = []
                    for note in line:
                        if note[1] == 'note' or note[1] == 'split':
                            notelst.append(note)
                    notelst.sort(key=lambda x: x[0])

                    for note in notelst:
                        if note[5] == 'R':
                            for dot in notelst:
                                bgn_current = round(note[2])
                                end_current = round(note[3])
                                bgn_other = round(dot[2])
                                end_other = round(dot[3])
                                if bgn_other > bgn_current and bgn_other < end_current and dot[5] == 'R':
                                    continuation_dot(event_x_pos(bgn_other, lcounter)+5, note_y_pos(note[4], minnote, maxnote, cursy))
                                if end_other > bgn_current and end_other < end_current and dot[5] == 'R':
                                    continuation_dot(event_x_pos(end_other, lcounter)+5, note_y_pos(note[4], minnote, maxnote, cursy))
                        if note[5] == 'L':
                            for dot in notelst:
                                bgn_current = round(note[2])
                                end_current = round(note[3])
                                bgn_other = round(dot[2])
                                end_other = round(dot[3])
                                if bgn_other > bgn_current and bgn_other < end_current and dot[5] == 'L':
                                    continuation_dot(event_x_pos(bgn_other, lcounter)+5, note_y_pos(note[4], minnote, maxnote, cursy))
                                if end_other > bgn_current and end_other < end_current and dot[5] == 'L':
                                    continuation_dot(event_x_pos(end_other, lcounter)+5, note_y_pos(note[4], minnote, maxnote, cursy))

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpage:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpage:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        # drawing order
        draw_paper()
        draw_note_active()
        draw_barlines_and_text()
        draw_staff()
        draw_grid_lines()
        draw_note_start()
        draw_slur()
        draw_continuation_dot()

    drawing()
    canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
    return len(msg)











#------------------
# EXPORT FUNCTIONS
#------------------


def exportPS():
    print('exportPS')

    f = filedialog.asksaveasfile(mode='w', parent=root, filetypes=[("Postscript","*.ps")], initialfile=title)

    if f:
        name = f.name[:-3]
        counter = 0

        for export in range(render('q')):
            counter += 1
            print('printing page ', counter)
            canvas.postscript(file=f"{name} p{counter}.ps", colormode='gray', x=40, y=50+(export*(paperheigth+50)), width=paperwidth, height=paperheigth, rotate=False)

        os.remove(f.name)

    else:

        pass

    return





def exportPDF():
    print('exportPDF')
    f = filedialog.asksaveasfile(mode='w', parent=root, filetypes=[("pdf file","*.pdf")], initialfile=title, initialdir='~/Desktop')
    if f:
        n = render('q', 'white')
        pslist = []
        for rend in range(n):
            canvas.postscript(file=f"tmp{rend}.ps", x=40, y=50+(rend*(paperheigth+50)), width=paperwidth, height=paperheigth, rotate=False)
            process = subprocess.Popen(["ps2pdfwr", "-sPAPERSIZE=a4", "-dFIXEDMEDIA", "-dEPSFitPage", f"tmp{rend}.ps"])
            process.wait()
            os.remove(f"tmp{rend}.ps")
            pslist.append(f"tmp{rend}.pdf")
            cmd = 'pdfunite '
            for i in range(len(pslist)):
                cmd += pslist[i] + ' '
            cmd += f'"{f.name}"'
            process = subprocess.Popen(cmd, shell=True)
            process.wait()
        for x in pslist:
            os.remove(x)
        return
            
    else:
        return

def autosave():
    root.after(60000, autosave)
    if filepath == 'New':
        return
    save_file()
    
def renderkey(q):
    render('q', papercolor)





# MIDI input
midi_record_toggle = 0
def midi_toggle(q='q'):
    global midi_record_toggle
    if midi_record_toggle == 1:
        midi_record_toggle = 0
        canvas.configure(bg=_bg)
        return 0
    elif midi_record_toggle == 0:
        midi_record_toggle = 1
        canvas.configure(bg='brown')
        return 1

def midi_input():

    class Collector(threading.Thread):
        def __init__(self, device, port):
            threading.Thread.__init__(self)
            self.setDaemon(True)
            self.port = port
            self.portName = device.getPortName(port)
            self.device = device
            self.quit = False

        def run(self):
            self.device.openPort(self.port)
            self.device.ignoreTypes(True, False, True)
            while True:
                if self.quit:
                    return
                msg = self.device.getMessage(2500)
                if msg:
                    if msg.isNoteOn():
                        if midi_record_toggle == 1:
                            note = msg.getNoteNumber() - 20
                            textw.insert(textw.index(INSERT), number2pitch[note])
                            render('q', papercolor)

    dev = rtmidi.RtMidiIn()
    for i in range(dev.getPortCount()):
        device = rtmidi.RtMidiIn()
        print('OPENING',dev.getPortName(i))
        collector = Collector(device, i)
        collector.start()

    sys.stdin.read(1)
    for c in collectors:
        c.quit = True


threading.Thread(target=midi_input).start()












#------------------
# Piano Keyboard
#------------------
'''This is the mouse click keyboard input. it draws a keyboard on a canvas
widget and when hoovering it highlights the selected key. Left click
will insert a note, rightclick will add to the chord(for writing chords)'''
keywidth = 17.5
black = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 
            48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
def draw_piano_keyboard(keylength=80, x=0, y=0):
    piano.delete('all')
    greykeys = [4, 6, 8, 9, 11, 13, 15, 28, 30, 32, 33, 35, 37, 39, 52, 54, 56, 57, 59, 61, 63,
            76, 78, 80, 81, 83, 85, 87]

    piano.create_rectangle(x,y,x+(keywidth*88),y+keylength, fill='white')

    x0 = x
    piano.create_rectangle(x+(3*keywidth),y,x+(15*keywidth),y+keylength, fill='lightgrey', outline='')
    piano.create_rectangle(x+(27*keywidth),y,x+(39*keywidth),y+keylength, fill='lightgrey', outline='')
    piano.create_rectangle(x+(51*keywidth),y,x+(63*keywidth),y+keylength, fill='lightgrey', outline='')
    piano.create_rectangle(x+(75*keywidth),y,x+(87*keywidth),y+keylength, fill='lightgrey', outline='')
    
    x = x0
    for i in range(88):
        i += 1
        if i in black:
            piano.create_rectangle(x,y,x+keywidth,y+60, width=2, fill='black', outline='')
            x += keywidth
        else:
            x += keywidth

draw_piano_keyboard()



def mouse_note_input(event):
    global chord
    note = math.floor(event.x / keywidth + 1)
    if note <= 88:
        if event.num == 1:
            textw.insert(textw.index(INSERT), number2pitch[note])
            render('q', papercolor)
            return
        if event.num == 3:
            textw.insert(textw.index(INSERT), '_'+number2pitch[note])
            render('q', papercolor)
            chord = 1
            return


def mouse_note_highlight(event):
    global keywidth
    keywidth = piano.winfo_width()/88
    x = event.x
    y = event.y
    note = math.floor(x / keywidth)
    if note <= 87:
        draw_piano_keyboard()
        if y > 10:
            if note+1 in black:
                piano.create_rectangle(note*keywidth, 0, note*keywidth+keywidth, 60, fill='#24a6d1', outline='')
            else:
                piano.create_rectangle(note*keywidth, 0, note*keywidth+keywidth, 80, fill='#24a6d1', outline='')










##########################################################################
## Insert barchecks                                                     ##
##########################################################################
'''A tool for quickly inserting a bunch of barchecks to the file
to make life easier!'''
def inserting_barchecks():
    startnum = int(simpledialog.askfloat("From...", "Insert a number from which to insert barchecks to the file.", parent=root))
    endnum = int(simpledialog.askfloat("To...", "Insert how many barchecks you want to insert.", parent=root))
    for i in range(endnum):
        textw.insert(textw.index(INSERT), '_'+str(startnum)+' '+'\n')
        startnum += 1















# Menu
menubar = Menu(root, relief='flat', bg=_bg)
root.config(menu=menubar)

fileMenu = Menu(menubar, tearoff=0)

fileMenu.add_command(label='new', command=new_file)
fileMenu.add_command(label='open', command=open_file)
fileMenu.add_command(label='save', command=save_file)
fileMenu.add_command(label='save as', command=save_as)

fileMenu.add_separator()

submenu = Menu(fileMenu, tearoff=0)
submenu.add_command(label="postscript", command=exportPS)
submenu.add_command(label="pdf (linux only)", command=exportPDF)
fileMenu.add_cascade(label='export', menu=submenu, underline=0)

fileMenu.add_separator()

fileMenu.add_command(label="note color", underline=0, command=choose_midi_color)
fileMenu.add_command(label="horizontal/vertical", underline=0, command=switch_orientation)
fileMenu.add_command(label="insert barcheck tool", underline=0, command=inserting_barchecks)
fileMenu.add_command(label="fullscreen/windowed (F11)", underline=0, command=menufullscreen)
fileMenu.add_command(label="toggle midi input (esc)", underline=0, command=midi_toggle)

fileMenu.add_separator()

fileMenu.add_command(label="exit", underline=0, command=quit_editor)
menubar.add_cascade(label="menu", underline=0, menu=fileMenu)






new_file()
autosave()
root.bind('<Key>', renderkey)
root.bind('<Escape>', midi_toggle)
root.bind('<F11>', fullscreen)
piano.bind('<Button-1>', mouse_note_input)
piano.bind('<Button-3>', mouse_note_input)
piano.bind('<Motion>', mouse_note_highlight)
root.mainloop()
