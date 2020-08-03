import sys, os, platform, itertools
from mido import MidiFile
from decimal import Decimal
from tkinter import END, filedialog, messagebox, scrolledtext, Scrollbar, simpledialog
from itertools import tee, islice, chain

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk

    py3 = False
except ImportError:
    import tkinter.ttk as ttk

    py3 = True

import tkinter.font as font



#########################################################
# Build Graphical Userinterface                         #
#########################################################

# Color management
_bg = 'grey85'  # X11 color: 'gray85'
_fg = '#000000'  # X11 color: 'black'
_compcolor = 'gray85' # X11 color: 'gray85'
_ana1color = 'gray85' # X11 color: 'gray85'
_ana2color = '#ececec' # Closest X11 color: 'gray92'
bgr = "white"

root = tk.Tk()

def buildGUI():
    root.style = ttk.Style()
    root.style.theme_use('default')  # winnative
    root.style.configure('.', background=_bg)
    root.style.configure('.', foreground=_fg)
    root.style.configure('.', font="TkDefaultFont")
    root.style.map('.', background=
    [('selected', _compcolor), ('active', _ana2color)])
    root.geometry(f"{int(root.winfo_screenwidth())}x{int(root.winfo_screenheight())}+0+0")
    root.resizable(1, 1)
    root.configure(relief="ridge")
    root.configure(highlightcolor="black")
    root.protocol("WM_DELETE_WINDOW", exitRoot)

    frame = tk.Frame(root).pack(expand=True, fill='both')

    root.CanvasPage = tk.Canvas(frame)
    root.CanvasPage.place(relx=0, rely=0, relheight=1
            , relwidth=1, bordermode='ignore')
    root.CanvasPage.configure(borderwidth="2")
    root.CanvasPage.configure(relief="flat")
    root.CanvasPage.configure(selectbackground="#f4f4f4")
    root.CanvasPage.configure(takefocus="0", bg=bgr)


    vbar=Scrollbar(root.CanvasPage,orient='horizontal', width=15)
    vbar.pack(side='bottom',fill='x')
    vbar.config(command=root.CanvasPage.xview)
    root.CanvasPage.configure(xscrollcommand=vbar.set)

    root.menubar = tk.Menu(root,font="TkMenuFont",bg=_bg,fg=_fg)
    root.configure(menu = root.menubar)

    
    root.bind('<Left>', lambda event : root.CanvasPage.xview('scroll', -1, 'units'))
    root.bind('<Right>', lambda event : root.CanvasPage.xview('scroll', 1, 'units'))
    if platform.system() == 'Linux':
        root.bind('<4>', lambda event : root.CanvasPage.xview('scroll', -1, 'units'))
        root.bind('<5>', lambda event : root.CanvasPage.xview('scroll', 1, 'units'))


    root.sub_menu = tk.Menu(root,tearoff=0)
    root.menubar.add_cascade(menu=root.sub_menu,
            activebackground="#ececec",
            activeforeground="#000000",
            background=_bg,
            font="TkMenuFont",
            foreground="#000000",
            label="Menu")
    root.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background=_bg,
            font="TkMenuFont",
            foreground="#000000",
            label="Open", 
            command=openFile)
    root.sub_menu.add_separator(
            background=_bg)
    root.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background=_bg,
            font="TkMenuFont",
            foreground="#000000",
            label="Print")
    root.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background=_bg,
            font="TkMenuFont",
            foreground="#000000",
            label="Export Pdf")
    root.sub_menu.add_separator(
            background=_bg)
    root.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background=_bg,
            compound="left",
            font="TkMenuFont",
            foreground="#000000",
            label="About", 
            command=printX)
    root.sub_menu.add_separator(
            background=_bg)
    root.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background=_bg,
            font="TkMenuFont",
            foreground="#000000",
            label="Quit", 
            command=exitRoot)
    root.sub_menu12 = tk.Menu(root,tearoff=0)
    root.menubar.add_cascade(menu=root.sub_menu12,
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            compound="left",
            font="TkMenuFont",
            foreground="#000000",
            label="Set...")
    root.sub_menu12.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            compound="left",
            font="TkMenuFont",
            foreground="#000000",
            label="Scale",
            command=printX)

#########################################################
# File functions (openFile, saveFile, saveFileAs etc...)#
#########################################################
# opened file
openedfile = []
def openFile():
    print('openFile')
    # run basic functionality
    file = filedialog.askopenfile(parent=root, 
                                  mode='rb', 
                                  title='Select a MIDI-file', 
                                  filetypes=[("MIDI-file", "*.mid")])
    openedfile.clear()
    openedfile.append(file.name)
    print(openedfile)
    root.CanvasPage.delete('all')
    renderMusic("tralala")


def exitRoot():# Working
    root.destroy()

#########################################################
# tools(functions)                                      #
#########################################################
def difference(x, y):
    if x>=y:
        return x-y
    if y>x:
        return y-x


def quartersFitInMeasure(numerator, denominator):
    w = 0
    n = numerator
    d = denominator
    if d < 4:
        w = (n*d)/(d/2)
    if d == 4:
        w = (n*d)/d
    if d > 4:
        w = (n*d)/(d*2)
    return w

corr1 = 1

def black_key(x, y):  # center coordinates, radius
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    root.CanvasPage.create_oval(x0, y0, x1, y1, outline='black', fill='black')
    root.CanvasPage.create_line(x0+corr1,y, x0+corr1,y-40, width=2)

def black_key_left(x, y):  # center coordinates, radius
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    root.CanvasPage.create_oval(x0, y0, x1, y1, outline='black', fill='black')
    root.CanvasPage.create_oval(x0+4, y0+4, x1-4, y1-4, outline='white', fill='white')
    root.CanvasPage.create_line(x0+corr1,y, x0+corr1,y+40, width=2)

def white_key(x, y):  # center coordinates, radius
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    root.CanvasPage.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
    root.CanvasPage.create_line(x0+corr1,y, x0+corr1,y-40, width=2)

def white_key_left(x, y):  # center coordinates, radius
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    root.CanvasPage.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
    root.CanvasPage.create_oval(x0+4, y0+4, x1-4, y1-4, outline="black")
    root.CanvasPage.create_line(x0+corr1,y, x0+corr1,y+40, width=2)

def noteStop(x, y):
    root.CanvasPage.create_line(x-5,y-5, x, y, x,y, x-5,y+5, width=2) # orginal klavarscribo design
    #root.CanvasPage.create_line(x,y, x,y+5, x,y+5, x,y-5, x,y-5, x,y, x,y, x-5,y+5, x-5,y+5, x,y, x,y, x-5,y-5, fill='black', width=2) # maybe the pianoscript design


def previous_and_next(some_iterable):
        prevs, items, nexts = tee(some_iterable, 3)
        prevs = chain([None], prevs)
        nexts = chain(islice(nexts, 1, None), [None])
        return zip(prevs, items, nexts)

#########################################################
# Main program function                                 #
#########################################################

## layout settings ##
paperlength = 297 * (root.winfo_fpixels('1m')+0.1) # a4 210x297 mm
paperwidth = 210 * (root.winfo_fpixels('1m')+0.1)
allmargins = 35
printareawidth = paperwidth - (allmargins * 2)
printareaheight = paperlength - (allmargins * 2)

## score settings ##
octavesinmeasure = 4
startoctave = 2
measuresperline = 4
measurewidth = printareawidth / measuresperline
ii = 100

# default scale settings
yscale = 5
xscale = [5]

def renderMusic(tralala):
    root.CanvasPage.delete('all')
    mid = MidiFile(openedfile[0])
    midimsg = []
    

    def setChannel():# this function changes the channel of MIDItracks to later on make the seperation for left and right hand.
        print('setChannel')

    def translateMIDI():
        #### put all needed messages in a list ####
        ### storage 1 ###
        mem1=0
        midimsgs = []
        miditempo = []
        ticksperbeat = mid.ticks_per_beat
        msperbeat = 1


        
        # place messages in dict.
        for i in mid:
            midimsgs.append(i.dict())
        # change time values from delta to relative time.
        for i in midimsgs:
            time = i['time'] + mem1
            i['time'] = time
            mem1 = i['time']
        # change every note_on with 0 velocity to note_off.
            if i['type'] == 'note_on' and i['velocity'] == 0:
                i['type'] = 'note_off'
        # Add all usable messages in midimsg; the main midimessagelist.
            if i['type'] == 'note_on' or i['type'] == 'note_off':
                midimsg.append([i['type'], i['time'], i['note'], i['velocity'], i['channel']])
            if i['type'] == 'time_signature':
                midimsg.append([i['type'], i['time'], i['numerator'], i['denominator'], i['clocks_per_click'], i['notated_32nd_notes_per_beat']])
            if i['type'] == 'set_tempo':
                midimsg.append( [i['type'], i['time'], (i['tempo'])] )
            if i['type'] == 'track_name':
                midimsg.append([i['type'], i['time'], i['name']])
            if i['type'] == 'end_of_track':
                midimsg.append([i['type'], i['time']])
        
        

        
        #### Converting time to ticks ####
        ### storage 2 ###
        mem2 = [0]
        blck = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
        wht = [1, 3, 4, 6, 8, 9, 11, 13, 15, 16, 18, 20, 21, 23, 25, 27, 28, 30, 32, 33, 35, 37, 39, 40, 42, 44, 45, 47, 49, 51, 52, 54, 56, 57, 59, 61, 63, 64, 66, 68, 69, 71, 73, 75, 76, 78, 80, 81, 83, 85, 87, 88]



        ## convert time to ticks. (tickgenerator) ##
        for i in midimsg:
            if i[0] == 'set_tempo':
                msperbeat = i[2]
            i[1] = round((ticksperbeat * (1 / msperbeat) * 1000000 * i[1]), 0)

        ## define last noteoff time in ticks which is the length of the entire track. ##
        for i in midimsg:
            if i[0] == 'note_off':
                mem2.append(i[1])
                entirelength = mem2[-1]
        
        
        #### Engraving the barlines ####
        ### storage 3 ###
        timechange = []
        tctime = []
        numerator = 4
        denominator = 4
        num = 0
        den = 0
        barx = 0
        recx = 0
        

        ## add current timesig ##
        measurecount = entirelength / (quartersFitInMeasure(numerator, denominator) * mid.ticks_per_beat)
        sizeofmeasureinticks = quartersFitInMeasure(numerator, denominator) * mid.ticks_per_beat
        recwidth = sizeofmeasureinticks / 4

        for _ in range(int(measurecount)):
            root.CanvasPage.create_line(barx*(xscale[0]/50)-1.5, 0, barx*(xscale[0]/50)-1.5, 500, width=2)
            root.CanvasPage.create_text(barx*(xscale[0]/50)+15, 100, text=_+1)
            barx += sizeofmeasureinticks
            # create count rectangles
            tanglex = sizeofmeasureinticks/4
            # root.CanvasPage.create_rectangle(tanglex, 0, tanglex+100, 500, outline='', fill='#e3e3e3')
            recx += recwidth/4


        #### Engraving the staff ####
        ### storage 4 ###
        allnotes = []
        entirelength = 0
        measurecount = 0
        mem4 = [0]



        ## define highest notes and lowest for writing the right stafflines ##
        for i in midimsg:
            if i[0] == 'note_on':
                allnotes.append(i[2])


        ## define last noteoff time in ticks which is the length of the entire track ##
        for i in midimsg:
            if i[0] == 'note_off':
                mem2.append(i[1])
            entirelength = mem2[-1]


        ## write the needed stafflines (the cleff is always printed) ##
        if allnotes:
            if min(allnotes) <= 23:
                root.CanvasPage.create_line(0, 440, entirelength*(xscale[0]/50), 440, width=2.4)
            if min(allnotes) <= 28:
                root.CanvasPage.create_line(0, 425, entirelength*(xscale[0]/50), 425, width=1)
                root.CanvasPage.create_line(0, 415, entirelength*(xscale[0]/50), 415, width=1)
            if min(allnotes) <= 35:
                root.CanvasPage.create_line(0, 400, entirelength*(xscale[0]/50), 400, width=2.4)
                root.CanvasPage.create_line(0, 390, entirelength*(xscale[0]/50), 390, width=2.4)
                root.CanvasPage.create_line(0, 380, entirelength*(xscale[0]/50), 380, width=2.4)
            if min(allnotes) <= 50:
                root.CanvasPage.create_line(0, 365, entirelength*(xscale[0]/50), 365, width=1,)
                root.CanvasPage.create_line(0, 355, entirelength*(xscale[0]/50), 355, width=1,)
            if min(allnotes) <= 57:
                root.CanvasPage.create_line(0, 340, entirelength*(xscale[0]/50), 340, width=2.4)
                root.CanvasPage.create_line(0, 330, entirelength*(xscale[0]/50), 330, width=2.4)
                root.CanvasPage.create_line(0, 320, entirelength*(xscale[0]/50), 320, width=2.4)
            if min(allnotes) <= 52:
                root.CanvasPage.create_line(0, 305, entirelength*(xscale[0]/50), 305, width=1)
                root.CanvasPage.create_line(0, 295, entirelength*(xscale[0]/50), 295, width=1)
            if min(allnotes) <= 59:
                root.CanvasPage.create_line(0, 280, entirelength*(xscale[0]/50), 280, width=2.4)
                root.CanvasPage.create_line(0, 270, entirelength*(xscale[0]/50), 270, width=2.4)
                root.CanvasPage.create_line(0, 260, entirelength*(xscale[0]/50), 260, width=2.4)
            root.CanvasPage.create_line(0, 245, entirelength*(xscale[0]/50), 245, width=1, dash=(5, 5))
            root.CanvasPage.create_line(0, 235, entirelength*(xscale[0]/50), 235, width=1, dash=(5, 5))
            if max(allnotes) >= 65:
                root.CanvasPage.create_line(0, 220, entirelength*(xscale[0]/50), 220, width=2.4)
                root.CanvasPage.create_line(0, 210, entirelength*(xscale[0]/50), 210, width=2.4)
                root.CanvasPage.create_line(0, 200, entirelength*(xscale[0]/50), 200, width=2.4)
            if max(allnotes) >= 72:
                root.CanvasPage.create_line(0, 185, entirelength*(xscale[0]/50), 185, width=1)
                root.CanvasPage.create_line(0, 175, entirelength*(xscale[0]/50), 175, width=1)
            if max(allnotes) >= 77:
                root.CanvasPage.create_line(0, 160, entirelength*(xscale[0]/50), 160, width=2.4)
                root.CanvasPage.create_line(0, 150, entirelength*(xscale[0]/50), 150, width=2.4)
                root.CanvasPage.create_line(0, 140, entirelength*(xscale[0]/50), 140, width=2.4)
            if max(allnotes) >= 84:
                root.CanvasPage.create_line(0, 125, entirelength*(xscale[0]/50), 125, width=1)
                root.CanvasPage.create_line(0, 115, entirelength*(xscale[0]/50), 115, width=1)
            if max(allnotes) >= 89:
                root.CanvasPage.create_line(0, 100, entirelength*(xscale[0]/50), 100, width=2.4)
                root.CanvasPage.create_line(0, 80, entirelength*(xscale[0]/50), 80, width=2.4)
                root.CanvasPage.create_line(0, 70, entirelength*(xscale[0]/50), 70, width=2.4)
            if max(allnotes) >= 96:
                root.CanvasPage.create_line(0, 55, entirelength*(xscale[0]/50), 55, width=1)
                root.CanvasPage.create_line(0, 45, entirelength*(xscale[0]/50), 45, width=1)
            if max(allnotes) >= 101:
                root.CanvasPage.create_line(0, 30, entirelength*(xscale[0]/50), 30, width=2.4)
                root.CanvasPage.create_line(0, 20, entirelength*(xscale[0]/50), 20, width=2.4)
                root.CanvasPage.create_line(0, 10, entirelength*(xscale[0]/50), 10, width=2.4)



        ## note on ##
        for i in midimsg:
            if i[0] == 'note_on' and i[4] == 0:
                if i[2]-20 in blck:
                    black_key_left(i[1]*(xscale[0]/50)+2.5, -abs(i[2]*yscale)+yscale*100+50)
                if i[2]-20 in wht:
                    white_key_left(i[1]*(xscale[0]/50)+2.5, -abs(i[2]*yscale)+yscale*100+50)
            if i[0] == 'note_on' and i[4] > 0:
                if i[2]-20 in blck:
                    black_key(i[1]*(xscale[0]/50)+2.5, -abs(i[2]*yscale)+yscale*100+50)
                if i[2]-20 in wht:
                    white_key(i[1]*(xscale[0]/50)+2.5, -abs(i[2]*yscale)+yscale*100+50)
        
        ## note off ##
        for i in midimsg:
            if i[0] == 'note_off':
                mem3 = []
                for x in midimsg:
                    if x[0] == 'note_on' and x[4] == i[4]:
                        mem3.append(x[1])
                if i[1] not in mem3:
                    # if difference(i[1], x[1]) <= 10:
                    noteStop(i[1]*(xscale[0]/50), -abs(i[2]*yscale)+yscale*100+49.495)


        

        


        

            









        # for i in midimsg:
        #     if i[0] == 'time_signature':
        #         timechange.append([i[0], i[1], i[2], i[3], i[4], i[5]])

        # for i in timechange:
        #     tctime.append(i[1])

        #     for prvs, item, nxt in previous_and_next(tctime):
        #         # how many miditicks between first and last (timechange or last midioff-tick)?
        #         if nxt == None:
        #             break

        #         measurecount = entirelength / (quartersFitInMeasure(numerator, denominator) * mid.ticks_per_beat)
        #         while item < nxt:
        #             if 



                



    ## function run order ##
    translateMIDI()
    root.CanvasPage.configure(scrollregion=root.CanvasPage.bbox('all'))
    

def printX():
    x = simpledialog.askinteger('Xscale:', 'Set Xscale (min 0 max 100)', parent=root, minvalue=0, maxvalue=100)
    xscale.clear()
    xscale.append(int(x))
    renderMusic('pompiedompiedom')
    
    
def exportCanvas():
    print('exportCanvas')
    root.CanvasPage.postscript(file="~/Desktop/test.eps", width=0, height=0, x=500, y=1000)
            



#########################################################
# Program running order                                 #
#########################################################
buildGUI()
root.bind('<Key>', renderMusic)
openFile()

root.mainloop()
