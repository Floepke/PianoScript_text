import sys, os, platform
from mido import MidiFile
from tkinter import END, filedialog, messagebox, scrolledtext, Scrollbar, simpledialog
from musicfunctions import *
from logicfunctions import *

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
    root.title("PianoScript")

    frame = tk.Frame(root).pack(expand=True, fill='both')

    root.CanvasPage = tk.Canvas(frame)
    root.CanvasPage.place(relx=0, rely=0, relheight=1
            , relwidth=1, bordermode='ignore')
    root.CanvasPage.configure(borderwidth="2")
    root.CanvasPage.configure(relief="flat")
    root.CanvasPage.configure(selectbackground="#f4f4f4")
    root.CanvasPage.configure(takefocus="0", bg=bgr)


    vbar=Scrollbar(root.CanvasPage,orient='horizontal', width=20)
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
            label="Export Pdf",
            command=printCanvas)
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
file = ''


def openFile():
    print('openFile')
    file = filedialog.askopenfile(parent=root, 
                                  mode='rb', 
                                  title='Select a MIDI-file', 
                                  filetypes=[("MIDI-file", "*.mid")])
    file = file.name
    print(file)
    root.CanvasPage.delete('all')
    renderMusic(file)
    root.title(f"PianoScript | {file}")


def exitRoot():# Working
    root.destroy()

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


# default scale settings
yscale = 5
xscale = 0.25

counting = 0

def renderMusic(file):
    root.CanvasPage.delete('all')
    midifile = MidiFile(file)
    midimsg = []
    allnotes = []
    

    def setChannel():# this function changes the channel of notes to make the seperation for left and right hand.
        print('setChannel')

    def MIDImsgToList():
        ticksperbeat = midifile.ticks_per_beat
        msperbeat = 1
        formem = 0
        tslist = []
        counting = 0
        # place messages in dict.
        for i in midifile:
            midimsg.append(i.dict())
        # time to tick
        for i in midimsg:
            i['time'] = round((ticksperbeat * (1 / msperbeat) * 1000000 * i['time']), 0)
            if i['type'] == 'set_tempo':
                msperbeat = i['tempo']       
        # delta to relative tick
        for i in midimsg:
            i['time'] += formem
            formem = i['time']
        # change every note_on with 0 velocity to note_off.
            if i['type'] == 'note_on' and i['velocity'] == 0:
                i['type'] = 'note_off'
        # make list of all used notes to use later in the program.
            if i['type'] == 'note_on':
                allnotes.append(i['note'])
        # remove unnessesary elements of 'time_signature'.
            if i['type'] == 'time_signature':
                i.pop('clocks_per_click', None)
                i.pop('notated_32nd_notes_per_beat', None)
        # add length(in ticks) of the current 'time_signature' as 'length'.
                tslist.append([i['type'], i['time']])
            if i['type'] == 'end_of_track':
                tslist.append([i['type'], i['time']])
        formem = 0
        for i in tslist:
            diff = difference(formem, i[1])
            formem = i[1]
            i[1] = diff
        del tslist[0]
        for i in midimsg:
            if i['type'] == 'time_signature':
                i['length'] = tslist[counting][1]
                counting += 1
  
        for i in midimsg: print(i)


    def drawNotes():
        ## Labelstorage ##
        blck = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 48, 
        50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
        wht = [1, 3, 4, 6, 8, 9, 11, 13, 15, 16, 18, 20, 21, 23, 25, 27, 28, 30, 32, 33, 35, 
        37, 39, 40, 42, 44, 45, 47, 49, 51, 52, 54, 56, 57, 59, 61, 63, 64, 66, 68, 69, 71, 
        73, 75, 76, 78, 80, 81, 83, 85, 87, 88]

        # note on
        for i in midimsg:
            if i['type'] == 'note_on' and i['channel'] == 0:
                if i['note']-20 in blck:
                    black_key_left(i['time']*xscale+3, -abs(i['note']*5), root.CanvasPage)
                if i['note']-20 in wht:
                    white_key_left(i['time']*xscale+3, -abs(i['note']*5), root.CanvasPage)
                    
            if i['type'] == 'note_on' and i['channel'] > 0:
                if i['note']-20 in blck:
                    black_key_right(i['time']*xscale+3, -abs(i['note']*5), root.CanvasPage)
                if i['note']-20 in wht:
                    white_key_right(i['time']*xscale+3, -abs(i['note']*5), root.CanvasPage)
        


        # note off
        for i in midimsg:
            if i['type'] == 'note_off':
                noteStop(i['time']*xscale-0.6, -abs(i['note']*5), root.CanvasPage)



    def drawStaff():
        y = -550
        def staffLength():
            for i in midimsg:
                if i['type'] == 'end_of_track':
                    return i['time']*xscale

        def staffLines():
            if allnotes:
                if min(allnotes) <= 23:
                    root.CanvasPage.create_line(0, 440+y, staffLength(), 440+y, width=2.4)
                if min(allnotes) <= 28:
                    root.CanvasPage.create_line(0, 425+y, staffLength(), 425+y, width=1)
                    root.CanvasPage.create_line(0, 415+y, staffLength(), 415+y, width=1)
                if min(allnotes) <= 35:
                    root.CanvasPage.create_line(0, 400+y, staffLength(), 400+y, width=2.4)
                    root.CanvasPage.create_line(0, 390+y, staffLength(), 390+y, width=2.4)
                    root.CanvasPage.create_line(0, 380+y, staffLength(), 380+y, width=2.4)
                if min(allnotes) <= 50:
                    root.CanvasPage.create_line(0, 365+y, staffLength(), 365+y, width=1,)
                    root.CanvasPage.create_line(0, 355+y, staffLength(), 355+y, width=1,)
                if min(allnotes) <= 57:
                    root.CanvasPage.create_line(0, 340+y, staffLength(), 340+y, width=2.4)
                    root.CanvasPage.create_line(0, 330+y, staffLength(), 330+y, width=2.4)
                    root.CanvasPage.create_line(0, 320+y, staffLength(), 320+y, width=2.4)
                if min(allnotes) <= 52:
                    root.CanvasPage.create_line(0, 305+y, staffLength(), 305+y, width=1)
                    root.CanvasPage.create_line(0, 295+y, staffLength(), 295+y, width=1)
                if min(allnotes) <= 59:
                    root.CanvasPage.create_line(0, 280+y, staffLength(), 280+y, width=2.4)
                    root.CanvasPage.create_line(0, 270+y, staffLength(), 270+y, width=2.4)
                    root.CanvasPage.create_line(0, 260+y, staffLength(), 260+y, width=2.4)
                root.CanvasPage.create_line(0, 245+y, staffLength(), 245+y, width=1, dash=(5, 5))
                root.CanvasPage.create_line(0, 235+y, staffLength(), 235+y, width=1, dash=(5, 5))
                if max(allnotes) >= 65:
                    root.CanvasPage.create_line(0, 220+y, staffLength(), 220+y, width=2.4)
                    root.CanvasPage.create_line(0, 210+y, staffLength(), 210+y, width=2.4)
                    root.CanvasPage.create_line(0, 200+y, staffLength(), 200+y, width=2.4)
                if max(allnotes) >= 72:
                    root.CanvasPage.create_line(0, 185+y, staffLength(), 185+y, width=1)
                    root.CanvasPage.create_line(0, 175+y, staffLength(), 175+y, width=1)
                if max(allnotes) >= 77:
                    root.CanvasPage.create_line(0, 160+y, staffLength(), 160+y, width=2.4)
                    root.CanvasPage.create_line(0, 150+y, staffLength(), 150+y, width=2.4)
                    root.CanvasPage.create_line(0, 140+y, staffLength(), 140+y, width=2.4)
                if max(allnotes) >= 84:
                    root.CanvasPage.create_line(0, 125+y, staffLength(), 125+y, width=1)
                    root.CanvasPage.create_line(0, 115+y, staffLength(), 115+y, width=1)
                if max(allnotes) >= 89:
                    root.CanvasPage.create_line(0, 100+y, staffLength(), 100+y, width=2.4)
                    root.CanvasPage.create_line(0, 90+y, staffLength(), 90+y, width=2.4)
                    root.CanvasPage.create_line(0, 80+y, staffLength(), 80+y, width=2.4)
                if max(allnotes) >= 96:
                    root.CanvasPage.create_line(0, 65+y, staffLength(), 65+y, width=1)
                    root.CanvasPage.create_line(0, 55+y, staffLength(), 55+y, width=1)
                if max(allnotes) >= 101:
                    root.CanvasPage.create_line(0, 40+y, staffLength(), 40+y, width=2.4)
                    root.CanvasPage.create_line(0, 30+y, staffLength(), 30+y, width=2.4)
                    root.CanvasPage.create_line(0, 20+y, staffLength(), 20+y, width=2.4)
        
        
        def staffStart():
            counting = 0
            if max(allnotes) >= 65:
                counting += 35
            if max(allnotes) >= 72:
                counting += 25
            if max(allnotes) >= 77:
                counting += 35
            if max(allnotes) >= 84:
                counting += 25
            if max(allnotes) >= 89:
                counting += 35
            if max(allnotes) >= 96:
                counting += 25
            if max(allnotes) >= 101:
                counting += 35
            return -abs(counting)


        def staffHeigth():
            counting = 0
            if min(allnotes) <= 23:
                counting += 15
            if min(allnotes) <= 28:
                counting += 25
            if min(allnotes) <= 35:
                counting += 35
            if min(allnotes) <= 50:
                counting += 25
            if min(allnotes) <= 57:
                counting += 35
            if min(allnotes) <= 52:
                counting += 25
            if min(allnotes) <= 59:
                counting += 35
            counting += 10
            if max(allnotes) >= 65:
                counting += 35
            if max(allnotes) >= 72:
                counting += 25
            if max(allnotes) >= 77:
                counting += 35
            if max(allnotes) >= 84:
                counting += 25
            if max(allnotes) >= 89:
                counting += 35
            if max(allnotes) >= 96:
                counting += 25
            if max(allnotes) >= 101:
                counting += 35
            return counting


        def barline(x, blnumber, widget):
            barline_start = staffStart()
            barline_end = barline_start + staffHeigth()
            widget.create_line(x, barline_start-315, x, barline_end-315, width=2, dash=6)
            widget.create_text(x, barline_start-355, text=blnumber, anchor='w')


        def barlines():
            formem = 0
            barlinecount = 2
            for i in midimsg:
                if i['type'] == 'time_signature':
                    measureticklength = measureTicks(i['numerator'], i['denominator'], midifile.ticks_per_beat)
                    print(i['length'] / measureticklength)
                    for _ in range(int(i['length'] / measureticklength)):
                        formem += measureticklength
                        barline(formem*xscale, barlinecount, root.CanvasPage)
                        barlinecount += 1
            # startline
            barline(0, 1, root.CanvasPage)
            # endline
            barline(staffLength(), '', root.CanvasPage)


        def grid():
            formem = 0
            for i in midimsg:
                if i['type'] == 'time_signature':
                    root.CanvasPage.create_text(i['time']*xscale+10, staffStart()+staffHeigth()-300, text=f"{i['numerator']}/{i['denominator']}", anchor='w')
                    measureticklength = measureTicks(i['numerator'], i['denominator'], midifile.ticks_per_beat)
                    for _ in range(int(i['length'] / measureticklength)):
                        white_grey = 0
                        for x in range(i['numerator']):
                            if white_grey == 0:
                                white_grey = 1
                            else:
                                start1 = formem + (measureticklength / i['numerator'] * x) * xscale
                                end1 = start1 + (measureticklength / i['numerator']) * xscale
                                root.CanvasPage.create_rectangle(start1, staffStart()-315, end1, staffStart()+staffHeigth()-315, fill='#ececec', outline='')
                                white_grey = 0
                        formem += measureticklength*xscale
        grid()
        barlines()
        staffLines()
        


    def setCanvasSize():
        bbox = root.CanvasPage.configure(scrollregion=root.CanvasPage.bbox('all'))
        middle = root.CanvasPage.canvasy(1000, gridspacing=None)
        return bbox, middle


    MIDImsgToList()
    drawStaff()
    drawNotes()
    setCanvasSize()
    
    
    

def printX(file=file):
    x = simpledialog.askinteger('Xscale:', 'Set Xscale (min 0 max 100)', parent=root, minvalue=0, maxvalue=100)
    xscale = int(x)
    print(file)
    renderMusic(file)


def printCanvas():
    root.CanvasPage.postscript(file="~/Desktop/export.ps", colormode='color')



#########################################################
# Program running order                                 #
#########################################################
buildGUI()
openFile()
#renderMusic('/home/floepie/MEGAprogram/PianoScript/testmidifiles/test.mid')
root.mainloop()
