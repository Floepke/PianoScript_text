#--------------------
# Imports
#--------------------


from tkinter import Tk, Text, PanedWindow, Canvas, Scrollbar, Menu, filedialog, END, messagebox, simpledialog
from tkinter import colorchooser, INSERT, DoubleVar, Label, Image
import tkinter.ttk as ttk
import platform, subprocess, os, sys, threading, math, datetime, time, errno
from mido import MidiFile
# if platform.system() == 'Linux':
#     import rtmidi
if platform.system() == 'Windows':
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
from shutil import which


#--------------------
# GUI
#--------------------


#colors
_bg = '#aaaaaa' #d9d9d9
papercolor = '#555555'


# Root
root = Tk()
root.title('PianoScript')
ttk.Style(root).theme_use("alt")
scrwidth = root.winfo_screenwidth()
scrheight = root.winfo_screenheight()
root.geometry("%sx%s+%s+%s" % (int(scrwidth / 1.5), int(scrheight / 1.25), int(scrwidth / 6), int(scrheight / 12)))
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
leftpanel = PanedWindow(paned, relief='flat', width=1300, bg=_bg)
paned.add(leftpanel)
        # Right Panel
rightpanel = PanedWindow(paned, sashwidth=15, sashcursor='arrow', relief='flat', bg=_bg)
paned.add(rightpanel)
# Canvas --> leftpanel
canvas = Canvas(leftpanel, bg=papercolor, relief='flat')
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
# linux scroll
if platform.system() == 'Linux':
    canvas.bind("<5>", scrollD)
    canvas.bind("<4>", scrollU)
    canvas.bind("<1>", zoomerP)
    canvas.bind("<3>", zoomerM)
# mac scroll
if platform.system() == 'Darwin':
    def _on_mousewheel(event):
        canvas.yview_scroll(-1*(event.delta), "units")
    canvas.bind("<MouseWheel>", _on_mousewheel)
# windows scroll
if platform.system() == 'Windows':
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta)/120), "units")
    canvas.bind("<MouseWheel>", _on_mousewheel)
    canvas.bind("<Button-1>", zoomerP)
    canvas.bind("<Button-3>", zoomerM)

# text --> rightpanel
textw = Text(rightpanel, foreground='yellow', background='black', insertbackground='red', undo=True, maxundo=100, autoseparators=True)
textw.place(relwidth=1, relheight=1)
textw.focus_set()
fsize = 16
if platform.system() == 'Linux':
    textw.configure(font=('Terminal', fsize))
elif platform.system() == 'Windows':
    textw.configure(font=('courier', fsize))
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


#--------------------
# File management
#--------------------


default = '''~shadeofgrey{70} //0=black; 100=white
~numberingonoff{1}
~hand{R} // L/R
~mpsystem{5} // measures per line
~systemspace{90} // minimum space between systems
~papersize{125} // size of paper
~fillpagetreshold{300} // devides the systems over the whole page if the restspace is smaller then this value
~windowsgsexe{C:/Program Files/gs/gs9.54.0/bin/gswin64c.exe} // enter the windows ghostscript executable here

// This file gets loaded before each pnoscript-file
// so you can apply default settings in this file
// 
// PDF EXPORT--------
// For windows: install 'ghostscript' and enter the path
// to the 'gswin64c.exe/gswin32c.exe' executable inside 'windowsgsexe' command(use '/')
// For linux: sudo apt-get install [package name]'''


starttemplate = '''// titles:
~title{...title...}
~composer{...composer...}
~copyright{copyrights reserved 2021}

// grid:
~grid{32 4/4 4}

//settings:
~mpsystem{5}
~papersize{150}
~systemspace{90}
~shadeofgrey{70}

// music: //
~hand{R}
_1 



~hand{L}
_1 ''' # % datetime.datetime.now().year


file = textw.get('1.0', END + '-1c')
filepath = ''


def new_file():
    print('new_file')
    global filepath
    if get_file() > '':
        save_quest()
    textw.delete('1.0', END)
    textw.insert('1.0', starttemplate, 'r')
    textw.edit_reset()
    root.title('PnoScript - New')
    filepath = 'New'
    return


def open_file():
    print('open_file')
    global filepath
    save_quest()
    f = filedialog.askopenfile(parent=root, mode='Ur', title='Open', filetypes=[("PianoScript files","*.pnoscript")], initialdir='~/Desktop/')
    if f:
        filepath = f.name
        root.title('PnoScript - %s' % f.name)
        f = open(f.name, 'r', newline=None)
        textw.delete('1.0', END)
        textw.insert('1.0', f.read())
        textw.edit_reset()
        f.close()
        render('normal', papercolor)
    return


def save_file():
    print('save_file')
    if filepath == 'New':
        f = save_as()
        if f == 0:
            print('save_file; canceled')
        return
    else:
        point = '.'
        for i in range(25):
            root.title('PnoScript - Saving%s' % point)
            point += '.'
            root.update_idletasks()
            time.sleep(0.01)
        root.title('PnoScript - %s' % filepath)
        f = open(filepath, 'w', newline=None)
        f.write(get_file())
        f.close()


def save_as():
    print('save_as')
    global filepath
    f = filedialog.asksaveasfile(parent=root, mode='w', filetypes=[("PianoScript files","*.pnoscript")], initialdir='~/Desktop/')
    if f:
        filepath = f.name
        root.title('PnoScript - %s' % f.name)
        f = open(f.name, 'w')
        f.write(get_file())
        f.close()
        return


def quit_editor():
    print('quit_editor')
    global whileloops
    whileloops = 0
    time.sleep(0.1)
    if filepath == 'New':
        ...#save_quest()
    else:
        save_file()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", quit_editor)



def save_quest():
    if messagebox.askyesno('Wish to save?', 'Do you wish to save the current file?'):
        save_file()
    else:
        return


def autosave(time=60000):
    root.after(time, autosave)
    if filepath == 'New':
        return
    save_file()


def get_file():
    global file
    file = textw.get('1.0', END + '-1c')
    return file







#----------------------------------------------------
# Tools (functions that are used by other functions)
#----------------------------------------------------


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
    
    if string == '':
        return 0

    calc = ''

    for i in string:
        if i in ['0','1','2','3','4','5','6','7','8','9', '+', '-', '*', '/', '(', ')', '.']:
            calc += i
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

    dur = None

    try:
        dur = eval(calc)
    except SyntaxError:
        print('wrong duration: %s' % string)
        return 0

    return dur


def string2pitch(string, transp):
    '''dictionary that gives back the piano-key-number.
    It applies also global transpose'''
    pitchdict = {
    # Oct 0
    'a0':1, 'A0':2, 'b0':3,
    # Oct 1
    'c1':4, 'C1':5, 'd1':6, 'D1':7, 'e1':8, 'f1':9, 'F1':10, 'g1':11, 'G1':12, 'a1':13, 'A1':14, 'b1':15,
    # Oct 2
    'c2':16, 'C2':17, 'd2':18, 'D2':19, 'e2':20, 'f2':21, 'F2':22, 'g2':23, 'G2':24, 'a2':25, 'A2':26, 'b2':27,
    # Oct 3
    'c3':28, 'C3':29, 'd3':30, 'D3':31, 'e3':32, 'f3':33, 'F3':34, 'g3':35, 'G3':36, 'a3':37, 'A3':38, 'b3':39,
    # Oct 4
    'c4':40, 'C4':41, 'd4':42, 'D4':43, 'e4':44, 'f4':45, 'F4':46, 'g4':47, 'G4':48, 'a4':49, 'A4':50, 'b4':51,
    # Oct 5
    'c5':52, 'C5':53, 'd5':54, 'D5':55, 'e5':56, 'f5':57, 'F5':58, 'g5':59, 'G5':60, 'a5':61, 'A5':62, 'b5':63,
    # Oct 6
    'c6':64, 'C6':65, 'd6':66, 'D6':67, 'e6':68, 'f6':69, 'F6':70, 'g6':71, 'G6':72, 'a6':73, 'A6':74, 'b6':75,
    # Oct 7
    'c7':76, 'C7':77, 'd7':78, 'D7':79, 'e7':80, 'f7':81, 'F7':82, 'g7':83, 'G7':84, 'a7':85, 'A7':86, 'b7':87,
    # Oct 8
    'c8':88
    }
    ret = pitchdict[string] + transp
    if ret < 1:
        ret = 1
    if ret > 88:
        ret = 88
    return ret


def pitch2string(num, transp):
    '''dictionary that gives back the piano-key-string'''
    num2string = {1: 'a0', 2: 'A0', 3: 'b0',
    4: 'c1', 5: 'C1', 6: 'd1', 7: 'D1', 8: 'e1', 9: 'f1', 10: 'F1', 11: 'g1', 12: 'G1', 13: 'a1', 14: 'A1', 15: 'b1',
    16: 'c2', 17: 'C2', 18: 'd2', 19: 'D2', 20: 'e2', 21: 'f2', 22: 'F2', 23: 'g2', 24: 'G2', 25: 'a2', 26: 'A2', 27: 'b2',
    28: 'c3', 29: 'C3', 30: 'd3', 31: 'D3', 32: 'e3', 33: 'f3', 34: 'F3', 35: 'g3', 36: 'G3', 37: 'a3', 38: 'A3', 39: 'b3',
    40: 'c4', 41: 'C4', 42: 'd4', 43: 'D4', 44: 'e4', 45: 'f4', 46: 'F4', 47: 'g4', 48: 'G4', 49: 'a4', 50: 'A4', 51: 'b4',
    52: 'c5', 53: 'C5', 54: 'd5', 55: 'D5', 56: 'e5', 57: 'f5', 58: 'F5', 59: 'g5', 60: 'G5', 61: 'a5', 62: 'A5', 63: 'b5',
    64: 'c6', 65: 'C6', 66: 'd6', 67: 'D6', 68: 'e6', 69: 'f6', 70: 'F6', 71: 'g6', 72: 'G6', 73: 'a6', 74: 'A6', 75: 'b6',
    76: 'c7', 77: 'C7', 78: 'd7', 79: 'D7', 80: 'e7', 81: 'f7', 82: 'F7', 83: 'g7', 84: 'G7', 85: 'a7', 86: 'A7', 87: 'b7',
    88: 'c8'}
    ret = num2string[num + transp]
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
        staffheight = 260
    if mx >= 76 and mx <= 80:
        staffheight = 220
    if mx >= 69 and mx <= 75:
        staffheight = 190
    if mx >= 64 and mx <= 68:
        staffheight = 150
    if mx >= 57 and mx <= 63:
        staffheight = 120
    if mx >= 52 and mx <= 56:
        staffheight = 80
    if mx >= 45 and mx <= 51:
        staffheight = 50
    if mx >= 40 and mx <= 44:
        staffheight = 10
    if mx < 40:
        staffheight = 10
    if mn >= 33 and mn <= 39:
        staffheight += 40
    if mn >= 28 and mn <= 32:
        staffheight += 70
    if mn >= 21 and mn <= 27:
        staffheight += 110
    if mn >= 16 and mn <= 20:
        staffheight += 140
    if mn >= 9 and mn <= 15:
        staffheight += 180
    if mn >= 4 and mn <= 8:
        staffheight += 210
    if mn >= 1 and mn <= 3:
        staffheight += 230
    return staffheight


def draw_staff_lines(y, mn, mx, keyboard):
    '''
    'y' takes the y-position of the uppper line of the staff.
    'mn' and 'mx' take the lowest and highest note in the staff
    so the function can draw the needed lines.
    'keyboard' draws a miniature pianokeyboard at the end of the 
    line when set to 1. If 0 there is no piano keyboard.
    '''

    def draw3Line(y):
        x = marginx_start
        canvas.create_line(x, y, x+(paperwidth-marginsx-marginsx), y, width=2, capstyle='round')
        canvas.create_line(x, y+10, x+(paperwidth-marginsx-marginsx), y+10, width=2, capstyle='round')
        canvas.create_line(x, y+20, x+(paperwidth-marginsx-marginsx), y+20, width=2, capstyle='round')
        if keyboard == 1:
            canvas.create_line(x+(paperwidth-marginsx-marginsx), y, x+(paperwidth-marginsx-marginsx)+(scale*12), y, width=4, capstyle='round')
            canvas.create_line(x+(paperwidth-marginsx-marginsx), y+10, x+(paperwidth-marginsx-marginsx)+(scale*12), y+10, width=4, capstyle='round')
            canvas.create_line(x+(paperwidth-marginsx-marginsx), y+20, x+(paperwidth-marginsx-marginsx)+(scale*12), y+20, width=4, capstyle='round')


    def draw2Line(y):
        x = marginx_start
        canvas.create_line(x, y, x+(paperwidth-marginsx-marginsx), y, width=0.5, capstyle='round')
        canvas.create_line(x, y+10, x+(paperwidth-marginsx-marginsx), y+10, width=0.5, capstyle='round')
        if keyboard == 1:
            canvas.create_line(x+(paperwidth-marginsx-marginsx), y, x+(paperwidth-marginsx-marginsx)+(scale*12), y, width=4, capstyle='round')
            canvas.create_line(x+(paperwidth-marginsx-marginsx), y+10, x+(paperwidth-marginsx-marginsx)+(scale*12), y+10, width=4, capstyle='round')


    def drawDash2Line(y):
        x = marginx_start
        if platform.system() == 'Linux' or platform.system() == 'Darwin':
            canvas.create_line(x, y, x+(paperwidth-marginsx-marginsx), y, width=1, dash=(6,6), capstyle='round')
            canvas.create_line(x, y+10, x+(paperwidth-marginsx-marginsx), y+10, width=1, dash=(6,6), capstyle='round')
        elif platform.system() == 'Windows':
            canvas.create_line(x, y, x+(paperwidth-marginsx-marginsx), y, width=1, dash=4, capstyle='round')
            canvas.create_line(x, y+10, x+(paperwidth-marginsx-marginsx), y+10, width=1, dash=4, capstyle='round')
        if keyboard == 1:
            canvas.create_line(x+(paperwidth-marginsx-marginsx), y, x+(paperwidth-marginsx-marginsx)+(scale*12), y, width=4, capstyle='round')
            canvas.create_line(x+(paperwidth-marginsx-marginsx), y+10, x+(paperwidth-marginsx-marginsx)+(scale*12), y+10, width=4, capstyle='round')

    keyline = 0
    staffheight = staff_height(mn,mx)

    if mx >= 81:
        draw3Line(0+y)
        draw2Line(40+y)
        draw3Line(70+y)
        draw2Line(110+y)
        draw3Line(140+y)
        draw2Line(180+y)
        draw3Line(210+y)
        keyline = 250
    if mx >= 76 and mx <= 80:
        draw2Line(0+y)
        draw3Line(30+y)
        draw2Line(70+y)
        draw3Line(100+y)
        draw2Line(140+y)
        draw3Line(170+y)
        keyline = 210
    if mx >= 69 and mx <= 75:
        draw3Line(0+y)
        draw2Line(40+y)
        draw3Line(70+y)
        draw2Line(110+y)
        draw3Line(140+y)
        keyline = 180
    if mx >= 64 and mx <= 68:
        draw2Line(0+y)
        draw3Line(30+y)
        draw2Line(70+y)
        draw3Line(100+y)
        keyline = 140
    if mx >= 57 and mx <= 63:
        draw3Line(0+y)
        draw2Line(40+y)
        draw3Line(70+y)
        keyline = 110
    if mx >= 52 and mx <= 56:
        draw2Line(0+y)
        draw3Line(30+y)
        keyline = 70
    if mx >= 45 and mx <= 51:
        draw3Line(0+y)
        keyline = 40

    drawDash2Line(keyline+y)

    if mn >= 33 and mn <= 39:
        draw3Line(keyline+30+y)
    if mn >= 28 and mn <= 32:
        draw3Line(keyline+30+y)
        draw2Line(keyline+70+y)
    if mn >= 21 and mn <= 27:
        draw3Line(keyline+30+y)
        draw2Line(keyline+70+y)
        draw3Line(keyline+100+y)
    if mn >= 16 and mn <= 20:
        draw3Line(keyline+30+y)
        draw2Line(keyline+70+y)
        draw3Line(keyline+100+y)
        draw2Line(keyline+140+y)
    if mn >= 9 and mn <= 15:
        draw3Line(keyline+30+y)
        draw2Line(keyline+70+y)
        draw3Line(keyline+100+y)
        draw2Line(keyline+140+y)
        draw3Line(keyline+170+y)
    if mn >= 4 and mn <= 8:
        draw3Line(keyline+30+y)
        draw2Line(keyline+70+y)
        draw3Line(keyline+100+y)
        draw2Line(keyline+140+y)
        draw3Line(keyline+170+y)
        draw2Line(keyline+210+y)
    if mn >= 1 and mn <= 3:
        draw3Line(keyline+30+y)
        draw2Line(keyline+70+y)
        draw3Line(keyline+100+y)
        draw2Line(keyline+140+y)
        draw3Line(keyline+170+y)
        draw2Line(keyline+210+y)
        canvas.create_line(marginx_start, keyline+240+y, marginx_start+(paperwidth-marginsx-marginsx), keyline+240+y, width=2)
        if keyboard == 1:
            canvas.create_line(marginx_start+(paperwidth-marginsx-marginsx), keyline+240+y, marginx_start+(paperwidth-marginsx-marginsx)+(scale*12), keyline+240+y, width=4, capstyle='round')

    if keyboard == 1:
        canvas.create_rectangle(marginx_start+(paperwidth-marginsx-marginsx), y-20, marginx_start+(paperwidth-marginsx-marginsx)+(marginsx/1.5), y+staffheight+20)


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
    canvas.create_line(x0,y-20, x0,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black')


def black_key_right_hlf(x, y):  # center coordinates, radius
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5 - 5
    y1 = y + 5
    canvas.create_line(x0+5,y-20, x0+5,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black')


def white_key_right_dga(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 10
    y1 = y + 5
    canvas.create_line(x0,y-20, x0,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')


def white_key_right_cefb(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 3.5
    x1 = x + 10
    y1 = y + 3.5
    canvas.create_line(x0,y-20, x0,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')


def black_key_left(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    canvas.create_line(x0,y+20, x0,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black') # normal
    canvas.create_oval(x0+3, y0+4, x1-3, y1-4, outline='white', fill='white') # point
    #canvas.create_polygon(x, y+5, x+10, y, x, y-5, outline='black', fill='black') # triangle
    #canvas.create_polygon(x, y+5, x+5, y, x, y-5, outline='black', fill='black') # diamond
    #canvas.create_oval(x0+3, y0+4, x1-3, y1-4, outline='', fill='white')


def black_key_left_hlf(x, y):  # center coordinates, radius
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5 - 5
    y1 = y + 5
    canvas.create_line(x0+5,y+20, x0+5,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black') # normal
    canvas.create_oval(x0+3, y0+4, x1-3, y1-4, outline='white', fill='white') # point
    # canvas.create_polygon(x, y, x+5, y+5, x+10, y, x+5, y-5, outline='black', fill='black') # triangle
    #canvas.create_oval(x0-3, y0+4, x1+3, y1-4, outline='', fill='white')


def white_key_left_dga(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 10
    y1 = y + 5
    canvas.create_line(x0,y+20, x0,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
    canvas.create_oval(x0+4, y0+4, x1-4, y1-4, outline="", fill='black') # point
    #canvas.create_polygon(x, y, x+5, y+5, x+10, y, x+5, y-5, outline="black", width=2, fill='white') # diamond
    #canvas.create_polygon(x, y+5, x+10, y, x, y-5, outline="black", width=2, fill='white') # triangle
    #canvas.create_oval(x0+4, y0+4, x1-4, y1-4, outline="", fill='black')


def white_key_left_cefb(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 3.5
    x1 = x + 10
    y1 = y + 3.5
    canvas.create_line(x0,y+20, x0,y, width=2, capstyle='round')
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
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

    ylist = [495, 490, 485, 475, 470, 465, 460, 455, 445, 440, 435, 430, 425, 420, 415, 
    405, 400, 395, 390, 385, 375, 370, 365, 360, 355, 350, 345, 335, 330, 325, 320, 315, 
    305, 300, 295, 290, 285, 280, 275, 265, 260, 255, 250, 245, 235, 230, 225, 220, 215, 
    210, 205, 195, 190, 185, 180, 175, 165, 160, 155, 150, 145, 140, 135, 125, 120, 115, 
    110, 105, 95, 90, 85, 80, 75, 70, 65, 55, 50, 45, 40, 35, 25, 20, 15, 10, 5, 0, -5, -15]

    sub = 0

    if mx >= 81:
        sub = 0
    if mx >= 76 and mx <= 80:
        sub = 40
    if mx >= 69 and mx <= 75:
        sub = 70
    if mx >= 64 and mx <= 68:
        sub = 110
    if mx >= 57 and mx <= 63:
        sub = 140
    if mx >= 52 and mx <= 56:
        sub = 180
    if mx >= 45 and mx <= 51:
        sub = 210
    if mx <= 44:
        sub = 250

    return cursy + ylist[note-1] - sub


def diff(x, y):
    if x >= y:
        return x - y
    else:
        return y - x


def note_active_gradient(x0, x1, y, linenr):
    '''draws a midi note with gradient'''
    x0 = event_x_pos(x0, linenr)
    x1 = event_x_pos(x1, linenr)
    width = diff(x0, x1)
    if width == 0:
        width = 1
    (r1,g1,b1) = root.winfo_rgb('white')
    (r2,g2,b2) = root.winfo_rgb(midinotecolor)
    r_ratio = float(r2-r1) / width
    g_ratio = float(g2-g1) / width
    b_ratio = float(b2-b1) / width
    for i in range(math.ceil(width)):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
        canvas.create_line(x0+i,y-5,x0+i,y+5, fill=color)
    canvas.create_line(x1, y-5, x1, y+5, width=2)
    canvas.create_line(x0, y-5, x0, y+5, width=2, fill='white')


def note_active_grey(x0, x1, y, linenr):
    '''draws a midi note with a stop sign(vertical line at the end of the midi-note).'''
    x0 = event_x_pos(x0, linenr)
    x1 = event_x_pos(x1, linenr)
    canvas.create_rectangle(x0, y-5, x1, y+5, fill=midinotecolor, outline='')#e3e3e3
    canvas.create_line(x1, y-5, x1, y+5, width=2)
    canvas.create_line(x0, y-5, x0, y+5, width=2, fill=midinotecolor)


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


def addmeas_processor(string):
    '''
    This function processes the ~grid{} command. It translates the time signature to length
    in piano-ticks. the function returns 'length in piano-tick', 'grid-division' and 
    'amount of measures to create'.
    '''

    string = string.split()

    amount = string[0]
    length = measure_length(string[1], 256)
    grid = string[2]
    try:
        beam = string[3]
    except:
        beam = 0
    
    try:
        visible = string[4]
    except:
        visible = 1

    return length, grid, amount, visible, beam


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

def get_ts_pos_and_ts(gridlist, tsname):
    tstimes = []
    tsnames = []
    tslength = []
    tsvis = []
    time = 0
    for ts in gridlist:
        tstimes.append(time)
        tslength.append(ts[0])
        time += ts[0]*ts[2]
        tsvis.append(ts[3])
    tstimes = zip(tstimes, tslength, tsname, tsvis)
    return tstimes

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None

def grey_color(grey):
    '''This function returns a colorcode based on a number from 0-100.
    0=white, 100=black'''
    if grey <= 100:
        color = ''
        r = '{:02x}'.format(round(grey / 100 * 255))
        g = '{:02x}'.format(round(grey / 100 * 255))
        b = '{:02x}'.format(round(grey / 100 * 255))
        color = '#'+r+g+b
        return color
    return '#000000'

def bbox_text(i):
    x0 = canvas.bbox(i)[0]
    y0 = canvas.bbox(i)[1]+5
    x1 = canvas.bbox(i)[2]
    y1 = canvas.bbox(i)[3]-5
    return (x0, y0, x1, y1)

def prepare_beams(thelist):
    returnlist = []

    def isnewline(thelist):
        old = 0
        index = 0
        for tup in thelist:
            if old > tup[0]:
                return True
            else:
                old = tup[0]
        return False

    for beam in thelist:
        if isnewline(beam) == False:
            returnlist.append(beam)
        else:
            old = 0
            index = 0
            curr_beam = []
            for tup in beam:
                if index == 0:#first iteration
                    curr_beam.append(tup)
                    old = tup[0]
                elif old > tup[0]:#if newline
                    returnlist.append(curr_beam)
                    curr_beam = []
                    curr_beam.append(tup)
                    old = tup[0]
                elif index+1 == len(beam):#last iteration
                    curr_beam.append(tup)
                    returnlist.append(curr_beam)
                else:
                    curr_beam.append(tup)
                    old = tup[0]
                index += 1
    return returnlist

def interpolation(x, y, z):
        return (z - x) / (y - x)


def get_tkinter_text_index(fstring,curs_pos):
    '''
    This function returns the index number of 
    a string using tkinters line.column notation
    as second argument. 
    fstring = tkinter text widget text
    curs_pos = tkinter_text_widget.index('insert')
    '''
    curs_pos = curs_pos.split('.')
    line = eval(curs_pos[0])
    column = eval(curs_pos[1])
    out = 0
    for sym in fstring:
        if line == 1:
            return out + column
        else:
            if sym == '\n':
                line -= 1
        out += 1














#--------------------
# Render function
#--------------------


## score variables ##
# titles:
title = ''
subtitle = ''
composer = ''
copyright = ''
# settings:
transpose = 0
mpline = 5
systemspacing = 90
scale = 100/100
titlespace = 60
midinotecolor = '#b4b4b4'#b4b4b4
fillpagetreshold = 300 # fillpagetreshold
printtitle = 1 # on/off
printcomposer = 1 # on/off
printcopyright = 1 # on/off
measurenumbering = 1 # on/off
dotts = 0 # on/off
midirecord = 1
whileloops = 1


# render lists:
grid = []
msg = []
pagespace = []
pagenumbering = []
tsnamelist = []


## constants ##
mm = root.winfo_fpixels('1m')
paperheigth = mm * 297 * (scale)  # a4 210x297 mm
paperwidth = mm * 210 * (scale)
marginsx = 40
marginsy = 60
printareawidth = paperwidth - (marginsx*2)
printareaheight = paperheigth - (marginsy*2)
marginx_start = marginsx * 2
number2pitch = {1: 'a0', 2: 'A0', 3: 'b0',
     4: 'c1', 5: 'C1', 6: 'd1', 7: 'D1', 8: 'e1', 9: 'f1', 10: 'F1', 11: 'g1', 12: 'G1', 13: 'a1', 14: 'A1', 15: 'b1', 
     16: 'c2', 17: 'C2', 18: 'd2', 19: 'D2', 20: 'e2', 21: 'f2', 22: 'F2', 23: 'g2', 24: 'G2', 25: 'a2', 26: 'A2', 27: 'b2', 
     28: 'c3', 29: 'C3', 30: 'd3', 31: 'D3', 32: 'e3', 33: 'f3', 34: 'F3', 35: 'g3', 36: 'G3', 37: 'a3', 38: 'A3', 39: 'b3', 
     40: 'c4', 41: 'C4', 42: 'd4', 43: 'D4', 44: 'e4', 45: 'f4', 46: 'F4', 47: 'g4', 48: 'G4', 49: 'a4', 50: 'A4', 51: 'b4', 
     52: 'c5', 53: 'C5', 54: 'd5', 55: 'D5', 56: 'e5', 57: 'f5', 58: 'F5', 59: 'g5', 60: 'G5', 61: 'a5', 62: 'A5', 63: 'b5', 
     64: 'c6', 65: 'C6', 66: 'd6', 67: 'D6', 68: 'e6', 69: 'f6', 70: 'F6', 71: 'g6', 72: 'G6', 73: 'a6', 74: 'A6', 75: 'b6', 
     76: 'c7', 77: 'C7', 78: 'd7', 79: 'D7', 80: 'e7', 81: 'f7', 82: 'F7', 83: 'g7', 84: 'G7', 85: 'a7', 86: 'A7', 87: 'b7', 
     88: 'c8'}
windowsgsexe = ''


def render(rendertype='normal', papercol=papercolor): # rendertype can be type 'normal' or 'export', papercol=papercolor
    global scale_S, renderno, pagespace, title, subtitle, composer, copyright
    global mpline, systemspacing, scale, grid, msg, paperheigth, paperwidth
    global marginsy, marginsx, printareaheight, printareawidth, printtitle
    global printcomposer, printcopyright, measurenumbering, pagenumbering, transpose
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
    tsnamelist.clear()
    fontsize = 18
    if rendertype == 'export':
        fontsize = 26


    def reading():
        global scale_S, renderno, pagespace, title, subtitle, composer, copyright, fillpagetreshold
        global mpline, systemspacing, scale, grid, msg, paperheigth, paperwidth, windowsgsexe
        global marginsy, marginsx, printareaheight, printareawidth, printtitle, default, transpose
        global printcomposer, printcopyright, measurenumbering, marginx_start, midinotecolor
        
        def create_dir_win():
            global default

            if not os.path.exists('~Documents/pianoscript/default.pnoscript'):
                try:
                    os.makedirs('~Documents/pianoscript/default.pnoscript')
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise


        def create_dir_lin():
            global default

            if not os.path.exists(os.path.expanduser('~Documents/pianoscript/')):
                print('!')
                try:
                    os.makedirs(os.path.expanduser('~Documents/pianoscript/'))
                except OSError as exc: # Guard against race condition
                    print('!!')
                    if exc.errno != errno.EEXIST:
                        raise

            if platform.system() == 'Windows':
                create_dir_win()
            elif platform.system() == 'Linux':
                create_dir_lin()

            with open('~Documents/pianoscript/default.pnoscript', "w") as f:
                f.write(default)
            default = open(os.path.expanduser('~Documents/pianoscript/default.pnoscript'), 'r').read()

        



        file = strip_file_from_comments(default+get_file())

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
        bracket = 0
        for sym in musicstring:
            index += 1
            # antisymetric rhythm
            if sym == '<':
                bracket = 1
                ind2 = index
                antisymetric = []
                for i in musicstring[index+1:]: # reading antisemitric figure
                    ind2 += 1
                    if i in ['a', 'A', 'b', 'c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G', 'r', '=', '_']:
                        if i == 'r':
                            antisymetric.append(0)
                            continue
                        elif i == '=':
                            antisymetric.append(-1)
                            continue
                        elif i == '_':
                            antisymetric.append(-2)
                        elif musicstring[ind2+1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                            note = string2pitch(musicstring[ind2]+musicstring[ind2+1], transpose)
                            antisymetric.append(note)
                    elif i == '>':
                        msgprep.append([index, 'antisym', antisymetric])
                        break
                continue
            if sym == '>':
                bracket = 0
            if bracket == 1:
                continue

            # note
            if sym in ['a', 'A', 'b', 'c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G']:
                if musicstring[index+1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                    msgprep.append([index, 'note', string2pitch(musicstring[index]+musicstring[index+1], transpose)])

            # split (gets deleted from program)
            if sym == '=':
                msgprep.append([index, 'equal'])

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

            # beam
            if sym == '[':
                msgprep.append([index, 'beam_on'])
            if sym == ']':
                msgprep.append([index, 'beam_off'])

            # slur
            if sym == '(':
                msgprep.append([index, 'slur_on'])
            if sym == ')':
                msgprep.append([index, 'slur_off'])

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
            # antisymetric rhythm
            if event[1] == 'antisym':
                try:    
                    div = 0
                    for i in event[2]:
                        if i == -2:
                            div -= 1
                        else:
                            div += 1
                    dur = duration / div
                    pos = cursor
                    last = 0
                    for note in event[2]:
                        if note == 0:
                            pos += dur
                        elif note == -1:
                            if last == 0:
                                pos += dur
                            else:
                               msg.append([event[0], 'equal', pos, pos+dur, last, hand])
                               pos += dur 
                        elif note == -2:
                            div -= 1
                            pos -= dur
                        else:
                            msg.append([event[0], 'note', pos, pos+dur, note, hand])
                            pos += dur
                            last = note
                    cursor += duration
                except:
                    ...

            # titles
            if event[1] == 'title':
                title = event[2]

            if event[1] == 'composer':
                composer = event[2]

            if event[1] == 'copyright':
                copyright = event[2]

            # transpose
            if event[1] == 'transpose':
                try:
                    transpose = eval(event[2])
                except:
                    ...

            # invisible note
            if event[1] == 'invis':
                try: 
                    note = string2pitch(event[2], transpose)
                    msg.append([index, 'invis', cursor, 'dummy', note, hand])
                except:
                    ...

            # set shadeofgrey
            if event[1] == 'shadeofgrey':
                try:
                    midinotecolor = grey_color(eval(event[2]))
                except:
                    ...

            # set windowsgsexe
            if event[1] == 'windowsgsexe':
                try:
                    windowsgsexe = event[2]
                except:
                    ...

            # printtitle
            if event[1] == 'printtitle':
                try: 
                    printtitle = eval(event[2])
                except:
                    ...

            # printcomposer
            if event[1] == 'printcomposer':
                try: 
                    printcomposer = eval(event[2])
                except:
                    ...

            # printcopyright
            if event[1] == 'printcopyright':
                try: 
                    printcopyright = eval(event[2])
                except:
                    ...

            # measurenumbering
            if event[1] == 'numberingonoff':
                try: 
                    measurenumbering = eval(event[2])
                except:
                    ...

            # fillpagetreshold
            if event[1] == 'fillpagetreshold':
                try: 
                    fillpagetreshold = eval(event[2])
                except:
                    ...

            # addmeas
            if event[1] == 'grid':
                try:
                    length, grids, amount, visible, beam = addmeas_processor(event[2])
                    grid.append([length, eval(grids), eval(amount), visible, beam])
                    tsnamelist.append(event[2].split()[1])
                except:
                    ...


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
            
            # beam
            if event[1] == 'beam_on':
                msg.append([event[0], 'beam_on', round(cursor), hand])
                
            if event[1] == 'beam_off':
                msg.append([event[0], 'beam_off', round(cursor)-0.00000001, hand])
                

            # slur
            if event[1] == 'slur_on':
                msg.append([event[0], 'slur_on', cursor, hand])
            if event[1] == 'slur_off':
                msg.append([event[0], 'slur_off', cursor, hand])

            # bpm
            if event[1] == 'bpm':
                msg.append([index, 'bpm', cursor, event[2]])

            # hand
            if event[1] == 'hand':
                hand = event[2]

            # mpline
            if event[1] == 'mpsystem':
                try: 
                    mpline = create_mp_list(event[2])
                except: pass

            # systemspace
            if event[1] == 'systemspace':
                try: systemspacing = eval(event[2])
                except: pass

            # scale
            if event[1] == 'papersize':
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
                    except IndexError: print('ERROR: cursor out of range; try increasing the measure amount in ~grid{}')

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
                    msg.append([event[0], 'note', cursor, cursor+duration, event[2], hand])
                elif is_split == True:
                    msg.append([event[0], 'note', cursor, splitpoints[0], event[2], hand])
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
            if event[1] == 'equal':
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
                    msg.append([event[0], 'equal', cursor, cursor+duration, i])
                cursor += duration

            # bar (all bartypes)
            if event[1] == 'bar':
                if event[2] == '|:':
                    msg.append([event[0], 'bgn_rpt', cursor])
                if event[2] == ':|':
                    msg.append([event[0], 'end_rpt', cursor-0.1])
                if event[2] == '|':
                    msg.append([event[0], 'man_barline', cursor])
                if event[2] == ';':
                    msg.append([event[0], 'smalldash', cursor])
                if event[2] == '[':
                    msg.append([event[0], 'bgn_hook', cursor])
                if event[2] == ']':
                    msg.append([event[0], 'end_hook', cursor-0.1])

            # text (all types)
            if event[1] == 'text' or event[1] == 'textB' or event[1] == 'textI':
                text = ''
                xoffset = 0
                yoffset = 0
                size = 0
                if '%' in event[2]:
                    text = event[2].split('%')[0]
                    try: xoffset = eval(event[2].split('%')[1].split()[0])
                    except: ...
                    try: yoffset = eval(event[2].split('%')[1].split()[1])
                    except: ...
                    try: size = eval(event[2].split('%')[1].split()[2])
                    except: ...
                else:
                    text = event[2]
                msg.append([event[0], event[1], cursor, text, xoffset, yoffset, size])

        # creating time signature text msg
        tspos = get_ts_pos_and_ts(grid, tsnamelist)
        for i in tspos:
            msg.append(['index', 'tstext', i[0], i[1], i[2], i[3]])

        # skip bar numbering
        barlineposlist = barline_pos_list(grid)
        counter = 1
        pagenumbering.clear()
        for i in range(len(barlineposlist)):
            pagenumbering.append(i)
            counter += 1
        for event in msgprep:   
            if event[1] == 'skipbarcount':
                try:
                    bar = eval(event[2])
                    ind = pagenumbering.index(bar)
                    pagenumbering.insert(ind, 0)
                    pagenumbering.pop()
                except:
                    ...

        if len(grid) == 0:
            return
















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


        # placing msgs in lists of beam grouping based on ~maes{} command
        


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
                draw_papers(cursy, "#ffffff")
                if printcopyright == 1:
                    canvas.create_text(marginx_start, cursy+20+paperheigth, text='page %s of %s | %s | %s' % (counter, len(msg), title, copyright), anchor='w', font=("Courier", fontsize, "normal"))

                cursy += paperheigth + 50

            if printtitle == 1:
                canvas.create_text(marginx_start, 90, text=title, anchor='w', font=("Courier", fontsize, "normal"))
            if printcomposer == 1:
                canvas.create_text(marginx_start+printareawidth-marginsx-marginsx, 90, text=composer, anchor='e', font=("Courier", fontsize, "normal"))
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
                        if rendertype == 'normal':
                            if note[1] == 'note':
                                note_active_grey(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
                            if note[1] == 'split':
                                note_active_grey(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
                                continuation_dot(event_x_pos(note[2], lcounter)+5, note_y_pos(note[4], minnote, maxnote, cursy))
                            if note[1] == 'equal':
                                note_active_grey(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
                        elif rendertype == 'export':
                            if note[1] == 'note':
                                note_active_gradient(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
                            if note[1] == 'split':
                                note_active_gradient(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
                                continuation_dot(event_x_pos(note[2], lcounter)+5, note_y_pos(note[4], minnote, maxnote, cursy))
                            if note[1] == 'equal':
                                note_active_grey(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:

                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_barlines():
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
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight, width=2, capstyle='round')
                            if measurenumbering == 1:
                                bnum = pagenumbering[bcounter]
                                if bnum > 0:
                                    canvas.create_text(event_x_pos(note[2], lcounter)+5, cursy-20, text=bnum, anchor='w', font=('Courier', fontsize-6, 'normal'))

                        if note[1] == 'man_barline':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight, width=2, capstyle='round')
                        
                        if note[1] == 'bgn_rpt':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40, width=2, capstyle='round')
                            repeat_dot(event_x_pos(note[2], lcounter)+5, cursy+staffheight+15)
                            repeat_dot(event_x_pos(note[2], lcounter)+5, cursy+staffheight+30)

                        if note[1] == 'end_rpt':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40, width=2, capstyle='round')
                            repeat_dot(event_x_pos(note[2], lcounter)-12.5, cursy+staffheight+15)
                            repeat_dot(event_x_pos(note[2], lcounter)-12.5, cursy+staffheight+30)

                        if note[1] == 'bgn_hook':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40,
                                event_x_pos(note[2], lcounter), cursy+staffheight+40, event_x_pos(note[2], lcounter)+80, cursy+staffheight+40, width=2, capstyle='round')

                        if note[1] == 'end_hook':
                            canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight+40,
                                event_x_pos(note[2], lcounter), cursy+staffheight+40, event_x_pos(note[2], lcounter)-80, cursy+staffheight+40, width=2, capstyle='round')


                    canvas.create_line(marginx_start+(paperwidth-marginsx-marginsx), cursy, marginx_start+(paperwidth-marginsx-marginsx), cursy+staffheight, width=2, capstyle='round')

                    if lcounter == len(newline_pos_list(grid, mpline)):
                        canvas.create_line(marginx_start+(paperwidth-marginsx-marginsx), cursy, marginx_start+(paperwidth-marginsx-marginsx), cursy+staffheight, width=5, capstyle='round')


                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_text():
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

                        if note[1] == 'tstext':
                            start = event_x_pos(note[2], lcounter)
                            end = event_x_pos(note[2]+note[3], lcounter)
                            if note[5] == 1:
                                canvas.create_text(start+15, cursy+staffheight+25, text=note[4], anchor='w', font=('Courier', fontsize-4, 'bold'))
                                canvas.create_line(start, cursy+staffheight, 
                                                    start, cursy+staffheight+40, 
                                                    start, cursy+staffheight+40, 
                                                    end, cursy+staffheight+40,
                                                    end, cursy+staffheight+40,
                                                    end, cursy+staffheight, width=2)

                        if note[1] == 'textB':
                            if rendertype == 'normal':
                                i=canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6], 'bold'), fill='white')
                            if rendertype == 'export':
                                i=canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6]-9, 'bold'), fill='white')
                            b=bbox_text(i)
                            r=canvas.create_rectangle(b,fill="white", outline='')
                            canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6], 'bold'))

                        if note[1] == 'textI':
                            if rendertype == 'normal':
                                i=canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6], 'italic'), fill='white')
                            if rendertype == 'export':
                                i=canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6]-9, 'italic'), fill='white')
                            b=bbox_text(i)
                            r=canvas.create_rectangle(b,fill="white", outline='')
                            canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6], 'italic'))

                        if note[1] == 'text':
                            if rendertype == 'normal':
                                i=canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6], 'normal'), fill='white')
                            if rendertype == 'export':
                                i=canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6]-9, 'normal'), fill='white')
                            b=bbox_text(i)
                            r=canvas.create_rectangle(b,fill="white", outline='')
                            canvas.create_text(event_x_pos(note[2], lcounter)+10+note[4], cursy+staffheight+25+note[5], text=note[3], anchor='w', font=('Courier', fontsize+note[6], 'normal'))

                        if note[1] == 'bpm':
                            canvas.create_text(event_x_pos(note[2], lcounter)+10, cursy+staffheight+25, text='bpm = %s' % note[3], anchor='w', font='Courier 18')


                    canvas.create_line(marginx_start+(paperwidth-marginsx-marginsx), cursy, marginx_start+(paperwidth-marginsx-marginsx), cursy+staffheight, width=2)

                    if lcounter == len(newline_pos_list(grid, mpline)):
                        canvas.create_line(marginx_start+(paperwidth-marginsx-marginsx), cursy, marginx_start+(paperwidth-marginsx-marginsx), cursy+staffheight, width=5)


                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
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
                    
                    if lcounter == 1: 
                        draw_staff_lines(cursy, minnote, maxnote, 1)
                    else:
                        draw_staff_lines(cursy, minnote, maxnote, 0)

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100

        

        def draw_note_start():
            black = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 
            48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
            black_DFA = [2, 5, 7, 10, 14, 17, 19, 22, 26, 29, 31, 34, 38, 41, 43, 46, 
            50, 53, 55, 58, 62, 65, 67, 70, 74, 77, 79, 82, 86]
            black_G = [12, 24, 36, 48, 60, 72, 84]
            white = [1,4,9,16,21,28,33,40,45,52,57,64,69,76,81,
            6,11,13,18,23,25,30,35,37,42,47,49,54,59,61,66,71,73,78,
            83,85,88,3,8,15,20,27,32,39,44,51,56,63,68,75,80,87]
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

                            notex = event_x_pos(note[2], lcounter)
                            notey = note_y_pos(note[4], minnote, maxnote, cursy)

                            if note[4] in white:

                                if note[5] == 'R':
                                    white_key_right_dga(notex, notey)
                                elif note[5] == 'L':
                                    white_key_left_dga(notex, notey)
                                else:
                                    pass

                    # second for loop so the black keys are always on top of white
                    for note in notelst:
                        
                        if note[1] == 'note':

                            notex = event_x_pos(note[2], lcounter)
                            notey = note_y_pos(note[4], minnote, maxnote, cursy)

                            # connect stems of the same hand if they start at the same time.
                            for stem in notelst:
                                if round(stem[2]) == round(note[2]) and note[5] == stem[5]:
                                    currenty = notey
                                    stemy = note_y_pos(stem[4], minnote, maxnote, cursy)
                                    canvas.create_line(notex, currenty, notex, stemy, width=2)

                            # write the black notes on top of the white
                            if note[4] in black:
                                if note[5] == 'R':
                                    notetype = 0
                                    for bkey in notelst:
                                        if bkey[2] == note[2]:
                                            if bkey[4] == note[4]+1 or bkey[4] == note[4]-1:
                                                black_key_right_hlf(notex, notey)
                                                notetype = 1
                                    if not notetype == 1:
                                        black_key_right(notex, notey)
                                if note[5] == 'L':
                                    notetype = 0
                                    for bkey in notelst:
                                        if bkey[2] == note[2]:
                                            if bkey[4] == note[4]+1 or bkey[4] == note[4]-1:
                                                black_key_left_hlf(notex, notey)
                                                notetype = 1
                                    if not notetype == 1:
                                        black_key_left(notex, notey)

                                    



                            #### This piece of code adds beams to beamlist

                            # if boundloose == 1:
                            #     if note[5] == 'R':
                            #         canvas.create_line(old_x, old_y, notex, notey-20, width=3)
                            #     elif note[5] == 'L':
                            #         canvas.create_line(old_x, old_y, notex, notey+20, width=3)

                            # if note[6] == 'bound':
                            #     boundloose = 1
                            #     old_x = event_x_pos(note[2], lcounter)
                            #     if note[5] == 'R':
                            #         old_y = note_y_pos(note[4], minnote, maxnote, cursy)-20
                            #     elif note[5] == 'L':
                            #         old_y = note_y_pos(note[4], minnote, maxnote, cursy)+20
                            #     else:
                            #         pass
                            # elif note[6] == 'loose':
                            #     boundloose = 0
                            # else:
                            #     pass

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_hand_split_whitespace():
            '''
            Draws a white line if the note is on a barline 
            to make visible where the hand split point is.
            '''
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

                    for note in notelst:
                        
                        if note[1] == 'note':
                            
                            barlineposlist = barline_pos_list(grid)
                            notex = event_x_pos(note[2], lcounter)
                            notey = note_y_pos(note[4], minnote, maxnote, cursy)

                            if note[5] == 'R':
                                if note[2] in barlineposlist:
                                    canvas.create_line(notex, notey, notex, notey+7.5, fill='white', width=2)
                                    canvas.create_line(notex, notey-20, notex, notey-25, fill='white', width=2)
                            elif note[5] == 'L':
                                if note[2] in barlineposlist:
                                    canvas.create_line(notex, notey, notex, notey-7.5, fill='white', width=2)
                                    canvas.create_line(notex, notey+20, notex, notey+25, fill='white', width=2)
                            else:
                                pass


                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_grid_lines():
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            barlineposlist = barline_pos_list(grid)
            for page in msg:
                pcounter += 1

                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    for gridline in line:
                        if gridline[1] == 'dash':
                            if gridline[2] not in barlineposlist:
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
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
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
                            canvas.create_line(event_x_pos(slur[2], lcounter), cursy-20+slur[4], xpos2, cursy-20+slur[5], event_x_pos(slur[3], lcounter), cursy-20+slur[6], smooth=1, width=2.5, capstyle='round')

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_continuation_dot():
            '''
            This function prints a dot if anoter note from the same hand is starting when the current
            note is still sounding. Not sure if this is going to be part of the notation.
            '''
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
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100


        def draw_beam_r():
            '''
            This function prints a beam for all bounded notes seperated by unbounded notes.
            '''
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            beamlist_r = []
            beam_r = ['dummy', 'beam_off', 'dummy', 'R']
            helplist = []

            for page in msg:
                pcounter += 1

                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    for note in line:
                        if note[1] == 'beam_on' and note[3] == 'R':
                            beam_r = note
                        if note[1] == 'beam_off' and note[3] == 'R':
                            beam_r = note
                        
                        if beam_r[1] == 'beam_on' and beam_r[3] == 'R':
                            if note[1] == 'note' and note[5] == 'R':
                                helplist.append((event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)))
                        elif beam_r[1] == 'beam_off' and beam_r[3] == 'R':
                            if helplist:
                                #print(helplist, '!')
                                beamlist_r.append(helplist)
                                helplist = []

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100

            # prepare beamlist; splitting newline beams
            beamlist_r = prepare_beams(beamlist_r)            

            for beam in beamlist_r:
                beam.sort(key=lambda i: i[1])
                high = beam[0]
                low = beam[-1]
                beam.sort(key=lambda i: i[0])
                first = beam[0]
                last = beam[-1]
                degree = 10
                stemlength = 20
                canvas.create_line(first[0], high[1]-stemlength,
                                    last[0], high[1]-stemlength-degree,
                                    width=4, capstyle='round')
                for i in beam:
                    canvas.create_line(i[0], 
                                        i[1], 
                                        i[0], 
                                        high[1]-stemlength-(degree*interpolation(first[0], last[0], i[0])), 
                                        width=2, 
                                        capstyle='round')


        def draw_beam_l():
            '''
            This function prints a beam for all bounded notes seperated by unbounded notes.
            '''
            cursy = 90 + titlespace
            pcounter = 0
            lcounter = 0
            beamlist_r = []
            beam_r = ['dummy', 'beam_off', 'dummy', 'L']
            helplist = []

            for page in msg:
                pcounter += 1

                for line in page:
                    lcounter += 1
                    staffheight, minnote, maxnote = get_staff_height(line)

                    for note in line:
                        if note[1] == 'beam_on' and note[3] == 'L':
                            beam_r = note
                        if note[1] == 'beam_off' and note[3] == 'L':
                            beam_r = note
                        
                        if beam_r[1] == 'beam_on' and beam_r[3] == 'L':
                            if note[1] == 'note' and note[5] == 'L':
                                helplist.append((event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)))
                        elif beam_r[1] == 'beam_off' and beam_r[3] == 'L':
                            if helplist:
                                #print(helplist, '!')
                                beamlist_r.append(helplist)
                                helplist = []

                    if len(page) == 1:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)))
                    elif pagespace[pcounter-1] < fillpagetreshold:
                        cursy += staffheight + systemspacing + (pagespace[pcounter-1] / (len(page)-1))
                    elif pagespace[pcounter-1] >= fillpagetreshold:
                        cursy += staffheight + systemspacing

                cursy = (paperheigth+50) * pcounter + 100

            # prepare beamlist; splitting newline beams
            beamlist_r = prepare_beams(beamlist_r)            

            for beam in beamlist_r:
                beam.sort(key=lambda i: i[1])
                high = beam[0]
                low = beam[-1]
                beam.sort(key=lambda i: i[0])
                first = beam[0]
                last = beam[-1]
                degree = 10
                stemlength = 20
                canvas.create_line(first[0], low[1]+stemlength,
                                    last[0], low[1]+stemlength+degree,
                                    width=4, capstyle='round')
                for i in beam:
                    canvas.create_line(i[0], 
                                        i[1], 
                                        i[0], 
                                        low[1]+stemlength+(degree*interpolation(first[0], last[0], i[0])), 
                                        width=2, 
                                        capstyle='round')


        # drawing order
        draw_paper()
        draw_note_active()
        draw_barlines()
        draw_text()
        draw_hand_split_whitespace()
        draw_staff()
        draw_grid_lines()
        draw_note_start()
        draw_slur()
        draw_beam_r()
        draw_beam_l()
        #draw_continuation_dot()

    drawing()
    #canvas.create_text(10, 10, text='None')
    canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
    return len(msg)


def autorender(q='q'):
    '''Render is done in a thread. This thread function detects
    if the text is edtited since the last render and doesnt start
    a new rendering before it fineshed one.'''
    while whileloops == 1:
        time.sleep(0.1)
        if textw.edit_modified() == True:
            try: render('normal', papercolor)
            except:
                ...
            textw.edit_modified(False)
        

threading.Thread(target=autorender).start()










#-------------------
# EXPORT FUNCTIONS |
#-------------------


def exportPS():
    print('exportPS')

    f = filedialog.asksaveasfile(mode='w', parent=root, filetypes=[("Postscript","*.ps")], initialfile=title, initialdir='~/Desktop')

    if f:
        counter = 0

        for export in range(render('export')):
            counter += 1
            print('printing page ', counter)
            canvas.postscript(file=f"{f.name}_p{counter}.ps", colormode='gray', x=40, y=50+(export*(paperheigth+50)), width=paperwidth, height=paperheigth, rotate=False)

        #os.remove(f.name)

    else:

        pass

    return





def exportPDF():
    print('exportPDF')


    if platform.system() == 'Linux':
        if is_tool('ps2pdfwr') == 0:
            messagebox.showinfo(title="Can't export PDF!", message='PianoScript cannot export the PDF because function "ps2pdfwr" is not installed on your computer.')
            return
        
        f = filedialog.asksaveasfile(mode='w', parent=root, filetypes=[("pdf file","*.pdf")], initialfile=title, initialdir='~/Desktop')
        if f:
            n = render('export', 'white')
            pslist = []
            for rend in range(n):
                canvas.postscript(file="/tmp/tmp%s.ps" % rend, x=40, y=50+(rend*(paperheigth+50)), width=paperwidth, height=paperheigth, rotate=False)
                process = subprocess.Popen(["ps2pdfwr", "-sPAPERSIZE=a4", "-dFIXEDMEDIA", "-dEPSFitPage", "/tmp/tmp%s.ps" % rend, "/tmp/tmp%s.pdf" % rend])
                process.wait()
                os.remove("/tmp/tmp%s.ps" % rend)
                pslist.append("/tmp/tmp%s.pdf" % rend)
            cmd = 'pdfunite '
            for i in range(len(pslist)):
                cmd += pslist[i] + ' '
            cmd += '"%s"' % f.name
            process = subprocess.Popen(cmd, shell=True)
            process.wait()
            # for x in pslist:
            #     os.remove(x)
            return
        else:
            return
                
    elif platform.system() == 'Windows':
        f = filedialog.asksaveasfile(mode='w', parent=root, filetypes=[("pdf file","*.pdf")], initialfile=title, initialdir='~/Desktop')
        if f:
            print(f.name)
            counter = 0
            pslist = []
            for export in range(render('export')):
                counter += 1
                print('printing page ', counter)
                canvas.postscript(file=f"{f.name}{counter}.ps", colormode='gray', x=40, y=50+(export*(paperheigth+50)), width=paperwidth, height=paperheigth, rotate=False)
                pslist.append(str('"'+str(f.name)+str(counter)+'.ps'+'"'))
            try:
                process = subprocess.Popen(f'''"{windowsgsexe}" -dQUIET -dBATCH -dNOPAUSE -dFIXEDMEDIA -sPAPERSIZE=a4 -dEPSFitPage -sDEVICE=pdfwrite -sOutputFile="{f.name}.pdf" {' '.join(pslist)}''', shell=True)
                process.wait()
                process.terminate()
                for i in pslist:
                    os.remove(i.strip('"'))
                f.close()
                os.remove(f.name)
            except:
                messagebox.showinfo(title="Can't export PDF!", message='Be sure you have selected a valid path in the default.pnoscript file. You have to set the path+gswin64c.exe. example: ~windowsgsexe{C:/Program Files/gs/gs9.54.0/bin/gswin64c.exe}')










#-------------
# MIDI input
#-------------

# midi_record_toggle = 0
# def midi_toggle(q='q'):
#     global midi_record_toggle
#     if midi_record_toggle == 1:
#         midi_record_toggle = 0
#         canvas.configure(bg=papercolor)
#         return 0
#     elif midi_record_toggle == 0:
#         midi_record_toggle = 1
#         canvas.configure(bg='brown')
#         return 1

# def midi_input():

#     dev = rtmidi.RtMidiIn()

#     class Collector(threading.Thread):
#         def __init__(self, device, port):
#             threading.Thread.__init__(self)
#             self.setDaemon(True)
#             self.port = port
#             self.portName = device.getPortName(port)
#             self.device = device
#             self.quit = False

#         def run(self):
#             self.device.openPort(self.port)
#             self.device.ignoreTypes(True, False, True)
#             while True:
#                 if whileloops == 0:
#                     print('CLOSING MIDI PORT...')
#                     return
#                 msg = self.device.getMessage(2500)
#                 if msg:
#                     if msg.isNoteOn():
#                         if midi_record_toggle == 1:
#                             note = msg.getNoteNumber() - 20
#                             if shiftkey == 0:
#                                 textw.insert(textw.index(INSERT), number2pitch[note])
#                             elif shiftkey == 1:
#                                 textw.insert(textw.index(INSERT), '_'+number2pitch[note])
#                             autorender()
    
#     for i in range(dev.getPortCount()):
#         device = rtmidi.RtMidiIn()
#         print('OPENING',dev.getPortName(i))
#         collector = Collector(device, i)
#         collector.start()

# if platform.system() == 'Linux':
#     threading.Thread(target=midi_input).start()















#-----------------
# Piano Keyboard
#-----------------
'''This is the mouse click keyboard input. it draws a keyboard on a canvas
widget and when hoovering it highlights the selected key. Left click
will insert a note on cursor position in the Text widget, while holding shift 
will add to the current chord.'''

keywidth = 17.5
keylength = 80
black = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 
            48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
shiftkey = 0
def draw_piano_keyboard(x=0, y=0):
    piano.delete('all')
    greykeys = [4, 6, 8, 9, 11, 13, 15, 28, 30, 32, 33, 35, 37, 39, 52, 54, 56, 57, 59, 61, 63,
            76, 78, 80, 81, 83, 85, 87]

    piano.create_rectangle(x,y,x+(keywidth*88),y+keylength, fill='white')
    piano.create_rectangle(x+(3*keywidth),y,x+(15*keywidth),y+keylength, fill='lightgrey', outline='')
    piano.create_rectangle(x+(27*keywidth),y,x+(39*keywidth),y+keylength, fill='lightgrey', outline='')
    piano.create_rectangle(x+(51*keywidth),y,x+(63*keywidth),y+keylength, fill='lightgrey', outline='')
    piano.create_rectangle(x+(75*keywidth),y,x+(87*keywidth),y+keylength, fill='lightgrey', outline='')
    
    x = 0
    for i in range(88):
        i += 1
        if i in black:
            piano.create_rectangle(x,y,x+keywidth,y+(keylength/3*2), width=2, fill='black', outline='')
            piano.create_text(x+(keywidth/2),10,text=number2pitch[i],anchor='c',fill='white')
            x += keywidth
        else:
            piano.create_text(x+(keywidth/2),keylength-10,text=number2pitch[i],anchor='c',fill='black')
            x += keywidth

draw_piano_keyboard()



def mouse_note_input(event):
    note = math.floor(event.x / keywidth) + 1
    if note in black:
        piano.create_rectangle((note-1)*keywidth, 0, (note-1)*keywidth+keywidth, (keylength/3*2), fill='green', width=4)
    else:
        piano.create_rectangle((note-1)*keywidth, 0, (note-1)*keywidth+keywidth, keylength, fill='green', width=4)
    if note <= 88:
        if shiftkey == 0:
            textw.insert(textw.index(INSERT), number2pitch[note])
            return
        elif shiftkey == 1:
            textw.insert(textw.index(INSERT), '_'+number2pitch[note])
            return


def mouse_note_highlight(event):
    global keywidth, keylength
    keywidth = piano.winfo_width() / 88
    keylength = piano.winfo_height()
    note = math.floor(event.x / keywidth)
    draw_piano_keyboard()
    if event.y > 10:
        if note + 1 in black:
            piano.create_rectangle(note*keywidth, 0, note*keywidth+keywidth, (keylength/3*2), fill='#24a6d1', width=2)
        else:
            piano.create_rectangle(note*keywidth, 0, note*keywidth+keywidth, keylength, fill='#24a6d1', width=2)










#--------
# Tools
#--------


def auto_inserting_barcheck(event):
    '''
    By pressing the insert key, the program 
    inserts a new barcheck with the right bar number
    '''
    print("auto_inserting_barcheck")
    curr_index = textw.index(INSERT)
    
    # searching for last '_1' (underscore + number) in file.
    bar_check_number = 1
    t_index = get_tkinter_text_index(get_file(),curr_index)
    s_text = get_file()[0:t_index]
    ind2 = len(s_text)
    digits = ['1','2','3','4','5','6','7','8','9','0']
    for sym in reversed(s_text):
        dig = ''
        if sym == '_'and s_text[ind2] in digits:
            for i in s_text[ind2:-1]:
                if i in digits:
                    dig += i
                else:
                    break
            bar_check_number = eval(dig) + 1
            break
        ind2 -= 1
    # inserting the barcheck in text widget
    curr_index = eval(curr_index)
    textw.insert(textw.index('insert'), '\n'+'_'+str(bar_check_number)+' ')
    #textw.mark_set("insert", curr_index+len(str(bar_check_number)))


def transpose_selection(event):
    # get info
    if not textw.tag_ranges("sel"):
        print('transpose_selection: there is no selection.')
        return
    selection = textw.selection_get()
    sel_first = textw.index('sel.first')
    sel_last = textw.index('sel.last')
    
    # set transpose
    transp = 0
    if event.keysym == 'bracketleft':
        transp = -1
    elif event.keysym == 'bracketright':
        transp = 1

    # remove selection
    textw.delete('sel.first','sel.last')

    # insert transposed selection
    for i in range(0,len(selection)):
        if selection[i] in ['a','A','b','c','C','d','D','e','f','F','g','G'] and selection[i+1] in ['0','1','2','3','4','5','6','7','8']:
            pitchnum = string2pitch(selection[i]+selection[i+1], transp)
            textw.insert("insert", pitch2string(pitchnum, 0))
            continue

        else:
            if selection[i-1] in ['a','A','b','c','C','d','D','e','f','F','g','G'] and selection[i] in ['0','1','2','3','4','5','6','7','8']:
                continue
            textw.insert('insert', selection[i])
    
    # reset selection
    textw.tag_add("sel", sel_first, sel_last)
    textw.focus_force()




















#--------------
# MIDI import
#--------------
def midi_import():
    # ask for save
    new_file()
    # clear textbox
    textw.delete('1.0','end') 

    # ---------------------------------------------
    # translate midi data to note messages with
    # the right start and stop (piano)ticks.
    # ---------------------------------------------
    midifile = filedialog.askopenfile(parent=root, 
        mode='Ur', 
        title='Open midi (experimental)...', 
        filetypes=[("MIDI files","*.mid")]).name
    msgs = []
    mid = MidiFile(midifile)
    tpb = mid.ticks_per_beat
    msperbeat = 1
    for i in mid:
        msgs.append(i.dict())
    ''' convert time to pianotick '''
    for i in msgs:
        i['time'] = round(tpb * (1 / msperbeat) * 1000000 * i['time'] * (256 / tpb),0)
        if i['type'] == 'set_tempo':
            msperbeat = i['tempo']    
    ''' change time values from delta to relative time. '''
    memory = 0
    for i in msgs:
        i['time'] +=  memory
        memory = i['time']
        # change every note_on with 0 velocity to note_off.
        if i['type'] == 'note_on' and i['velocity'] == 0:
            i['type'] = 'note_off'
    ''' get note_on, note_off, time_signature durations. '''
    index = 0
    for i in msgs:
        if i['type'] == 'note_on':
            for n in msgs[index:]:
                if n['type'] == 'note_off' and i['note'] == n['note']:
                    i['duration'] = n['time'] - i['time']
                    break

        if i['type'] == 'time_signature':
            for t in msgs[index+1:]:
                if t['type'] == 'time_signature' or t['type'] == 'end_of_track':
                    i['duration'] = t['time'] - i['time']
                    break
        index += 1
    
    # for debugging purposes print every midi message.
    for i in msgs:
        print(i)

    # -----------------------
    # import help functions
    # -----------------------
    def insert_text(line, column, text):
        '''Inserts text forcing the line'''
        lastln = int(textw.index('end').split('.')[0])
        if lastln <= line:
            for i in range(0,line):
                textw.insert('end', '\n')
        textw.insert('%d.%d' % (line, column), text)

    def midi_duration_converter(duration):
        '''returns a string ready for import'''
        if duration == 1024:
            return 'W'
        elif duration == 1536:
            return 'W.'
        elif duration == 1792:
            return 'W..'
        elif duration == 512:
            return 'H'
        elif duration == 768:
            return 'H.'
        elif duration == 896:
            return 'H..'
        elif duration == 256:
            return 'Q'
        elif duration == 384:
            return 'Q.'
        elif duration == 448:
            return 'Q..'
        elif duration == 128:
            return 'E'
        elif duration == 192:
            return 'E.'
        elif duration == 224:
            return 'E..'
        elif duration == 64:
            return 'S'
        elif duration == 96:
            return 'S.'
        elif duration == 112:
            return 'S..'
        elif duration == 32:
            return 'T'
        elif duration == 48:
            return 'T.'
        elif duration == 56:
            return 'T..'
        else:
            return '~dur{%d}' % duration

    def which_measure(pianotick):
        '''returns in which measure the pianotick is located'''
        gridlist = []
        for i in msgs: 
            if i['type'] == 'time_signature':
                tsig = str(i['numerator'])+'/'+str(i['denominator'])
                amount = round(i['duration'] / measure_length(tsig, 256),0)
                gridlist.append({'measure_length':round(measure_length(tsig,256),0),'amount':amount})
        out = 1
        blinelist = [0]
        memory = 0
        for grid in gridlist:
            for i in range(1,int(grid['amount'])+1):
                blinelist.append(i * grid['measure_length'] + memory)
                if i == grid['amount']:
                    memory = i * grid['measure_length']
        for i in range(0,len(blinelist)):
            if i+1 == len(blinelist):
                return out
            if pianotick >= blinelist[i] and pianotick < blinelist[i+1]:
                return out
            else:
                out += 1
        return out

    def measno2pianotick(meas_no):
        '''returns the pianotick of the measure number.'''
        gridlist = []
        for i in msgs: 
            if i['type'] == 'time_signature':
                tsig = str(i['numerator'])+'/'+str(i['denominator'])
                amount = round(i['duration'] / measure_length(tsig, 256),0)
                gridlist.append({'measure_length':round(measure_length(tsig,256),0),'amount':amount})
        out = 1
        blinelist = [0]
        memory = 0
        for grid in gridlist:
            for i in range(1,int(grid['amount'])+1):
                blinelist.append(i * grid['measure_length'] + memory)
                if i == grid['amount']:
                    memory = i * grid['measure_length']
        return blinelist[meas_no-1]

    # --------------
    # Write titles.
    # --------------
    line = 1
    column = 0
    t = midifile.split('.')[0]
    insert_text(line, column, '// titles:')
    line += 1
    insert_text(line, column, '~title{%s}' % t)
    line += 1
    insert_text(line, column, '~composer{...composer...}')
    line += 1
    insert_text(line, column, '~copyright{copyrights reserved 2021}')

    # ------------
    # Write grid.
    # ------------
    line += 2
    insert_text(line, column, '// grid')
    for i in msgs:
        if i['type'] == 'time_signature':
            tsig = str(i['numerator'])+'/'+str(i['denominator'])
            amount = round(i['duration'] / measure_length(tsig, 256),0)
            gridno = i['numerator']
            if tsig == '6/8':
                gridno = 2
            if tsig == '12/8':
                gridno = 4
            line += 1
            insert_text(line, column, '~grid{%d %s %d}' % (amount, tsig, gridno))
    
    # ----------------
    # Write settings.
    # ----------------
    line += 2
    insert_text(line, column, '// settings:')
    line += 1
    insert_text(line, column, '~mpsystem{5}')
    line += 1
    insert_text(line, column, '~papersize{150}')
    line += 1
    insert_text(line, column, '~systemspace{90}')
    line += 1
    insert_text(line, column, '~shadeofgrey{70}')        

    # -------------
    # Write notes.
    # -------------
    line += 2
    insert_text(line,0,'~hand{R}')
    line += 1
    dur_set = 0
    curs_set = 0
    curr_meas = 1
    insert_text(line,0,'_1 ')
    column = 3
    for i in msgs:  
        if i['type'] == 'note_on' and i['channel'] == 0:
            cursor_and_length = ''
            meas_no = which_measure(i['time'])
            if meas_no > curr_meas:
                line += 1
                insert_text(line,0,'_%d ' % meas_no)
                curr_meas = meas_no
                curs_set = measno2pianotick(meas_no)
            if curs_set == i['time']:#if cursor position same as note start position
                if dur_set == i['duration']:
                    ...
                else:
                    cursor_and_length = midi_duration_converter(i['duration'])
            elif curs_set > i['time']:# if cursor position later than note start position
                curs_back = curs_set - i['time']
                curs_string = midi_duration_converter(curs_back)+'_'
                if dur_set == i['duration']:
                    ...
                else:
                    curs_string += midi_duration_converter(i['duration'])
                cursor_and_length = curs_string
            elif curs_set < i['time']:# in case of a rest in between
                curs_fw = i['time'] - curs_set
                curs_string = midi_duration_converter(curs_fw)+'r'
                if dur_set == i['duration']:
                    ...
                else:
                    curs_string += midi_duration_converter(i['duration'])
                cursor_and_length = curs_string

            note = number2pitch[i['note']-20]
            ins_string = cursor_and_length+note
            insert_text(line, column, ins_string+' ')

            curs_set = i['time'] + i['duration']
            column += len(ins_string)+1
            dur_set = i['duration']
    line += 2
    insert_text(line,0,'~hand{L}')
    line += 1
    dur_set = 0
    curs_set = 0
    curr_meas = 1
    insert_text(line,0,'_1 ')
    column = 3
    for i in msgs:  
        if i['type'] == 'note_on' and i['channel'] >= 1:
            cursor_and_length = ''
            meas_no = which_measure(i['time'])
            if meas_no > curr_meas:
                line += 1
                insert_text(line,0,'_%d ' % meas_no)
                curr_meas = meas_no
                curs_set = measno2pianotick(meas_no)
            if curs_set == i['time']:#if cursor position same as note start position
                if dur_set == i['duration']:
                    ...
                else:
                    cursor_and_length = midi_duration_converter(i['duration'])
            elif curs_set > i['time']:# if cursor position later than note start position
                curs_back = curs_set - i['time']
                curs_string = midi_duration_converter(curs_back)+'_'
                if dur_set == i['duration']:
                    ...
                else:
                    curs_string += midi_duration_converter(i['duration'])
                cursor_and_length = curs_string
            elif curs_set < i['time']:# in case of a rest in between
                curs_fw = i['time'] - curs_set
                curs_string = midi_duration_converter(curs_fw)+'r'
                if dur_set == i['duration']:
                    ...
                else:
                    curs_string += midi_duration_converter(i['duration'])
                cursor_and_length = curs_string

            note = number2pitch[i['note']-20]
            ins_string = cursor_and_length+note
            insert_text(line, column, ins_string+' ')

            curs_set = i['time'] + i['duration']
            column += len(ins_string)
            dur_set = i['duration']






















#-------
# Menu
#-------
menubar = Menu(root, relief='flat', bg=_bg)
root.config(menu=menubar)

fileMenu = Menu(menubar, tearoff=0)

fileMenu.add_command(label='new', command=new_file)
fileMenu.add_command(label='open', command=open_file)
fileMenu.add_command(label='import MIDI (experimental)', command=midi_import)
fileMenu.add_command(label='save', command=save_file)
fileMenu.add_command(label='save as', command=save_as)

fileMenu.add_separator()

submenu = Menu(fileMenu, tearoff=0)
submenu.add_command(label="postscript", command=exportPS)
submenu.add_command(label="pdf", command=exportPDF)
fileMenu.add_cascade(label='export', menu=submenu, underline=0)

fileMenu.add_separator()

fileMenu.add_command(label="horizontal/vertical", underline=0, command=switch_orientation)
fileMenu.add_command(label="fullscreen/windowed (F11)", underline=0, command=menufullscreen)
# fileMenu.add_command(label="toggle midi input (esc)", underline=0, command=midi_toggle)

fileMenu.add_separator()

fileMenu.add_command(label="exit", underline=0, command=quit_editor)
menubar.add_cascade(label="menu", underline=0, menu=fileMenu)




#------------
# Shortcuts
#------------
def keypress(event):
    textw.edit_modified(True)
    global shiftkey
    if event.keysym == 'Shift_L' or event.keysym == 'Shift_R':
        shiftkey = 1
    else:
        return

def keyrelease(event):
    global shiftkey
    if event.keysym == 'Shift_L' or event.keysym == 'Shift_R':
        shiftkey = 0
    else:
        return


new_file()
autosave()
#midi_import('test.mid')
# root.bind('<Escape>', midi_toggle)
root.bind('<F11>', fullscreen)
root.bind('<KeyPress>', keypress)
root.bind('<KeyRelease>', keyrelease)
root.bind('<Control-bracketleft>', transpose_selection)
root.bind('<Control-bracketright>', transpose_selection)
textw.bind('<Insert>', auto_inserting_barcheck)
piano.bind('<Button-1>', mouse_note_input)
piano.bind('<Motion>', mouse_note_highlight)
root.mainloop()