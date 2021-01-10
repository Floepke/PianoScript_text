### IMPORTS ###
from tkinter import Tk, Text, PanedWindow, Canvas, Scrollbar, Menu, filedialog, END, messagebox, simpledialog
import platform, subprocess, os

### GUI ###
# Root
root = Tk()
root.title('PianoScript')
scrwidth = root.winfo_screenwidth()
scrheight = root.winfo_screenheight()
root.geometry(f"{int(scrwidth / 1.5)}x{int(scrheight / 1.25)}+{int(scrwidth / 6)}+{int(scrheight / 12)}")
# PanedWindow
paned = PanedWindow(root, relief='sunken', sashwidth=15, sashcursor='arrow')
paned.pack(fill='both', expand=1)
# Left Panel
leftpanel = PanedWindow(paned, relief='raised', width=900)
paned.add(leftpanel)
# Right Panel
rightpanel = PanedWindow(paned,
                            orient='vertical',
                            sashwidth=15,
                            sashcursor='arrow')
paned.add(rightpanel)
# Canvas
canvas = Canvas(leftpanel, bg='grey')
canvas.place(relwidth=1, relheight=1)
vbar = Scrollbar(canvas, orient='vertical', width=20)
vbar.pack(side='right', fill='y')
vbar.config(command=canvas.yview)
canvas.configure(yscrollcommand=vbar.set)
hbar = Scrollbar(canvas, orient='horizontal', width=20)
hbar.pack(side='bottom', fill='x')
hbar.config(command=canvas.xview)
canvas.configure(xscrollcommand=hbar.set)
# if platform.system() == 'Darwin':
# 	root.bind('<Control-,>', lambda event: canvas.yview('scroll', -1, 'units'))
# 	root.bind('<Control-.>', lambda event: canvas.yview('scroll', 1, 'units'))
# if platform.system() == 'Linux':
#     root.bind('<4>', lambda event: canvas.yview('scroll', -1, 'units'))
#     root.bind('<5>', lambda event: canvas.yview('scroll', 1, 'units'))
#linux zoom
def bbox_offset(bbox):
		x1, y1, x2, y2 = bbox
		return (x1-40, y1-40, x2+40, y2+40)
def zoomerP(event):
	canvas.scale("all", event.x, event.y, 1.1, 1.1)
	canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
def zoomerM(event):
	canvas.scale("all", event.x, event.y, 0.9, 0.9)
	canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
canvas.bind("<1>", zoomerP)
canvas.bind("<3>", zoomerM)
# # Text
textw = Text(rightpanel, foreground='white', background='black', insertbackground='white')
textw.place(relwidth=1, relheight=1)
textw.focus_set()
fontsize = 16
textw.configure(font=f'courier {fontsize} ')
# Rightclick menu
def do_popup(event): 
    try: 
        menu.tk_popup(event.x_root, event.y_root)
    finally: 
        menu.grab_release()
menu = Menu(root, tearoff = 0, background='black', foreground='white',
               activebackground='white', activeforeground='black') 
menu.add_command(label ="[x] close menu")
if platform.system() == 'Linux':
    textw.bind("<Button-3>", do_popup)
if platform.system() == 'Darwin':
    textw.bind("<Button-2>", do_popup)







### MAIN CODE ###

##########################################################################
## File management 														##
##########################################################################















file = textw.get('1.0', END + '-1c')
filechange = False
filepath = ''

def fileChange(v):
	global filechange, filepath, file

	if filepath == 'New':
		
		if file == '':

			filechange = False
			root.title(f'PianoScript - {filepath}')
			return

		else:

			filechange = True
			root.title(f'PianoScript - {filepath}*')
			return

	else:# if file is opened file

		sourcefile = textw.get('1.0', END + '-1c')

		if sourcefile != file:

			filechange = True
			root.title(f'PianoScript - {filepath}*')
			return

		else:

			filechange = False
			root.title(f'PianoScript - {filepath}')
			return


	return


def saveQuest():
	
	if messagebox.askyesno('Wish to save?', 'Do you wish to save the current file?'):
		
		saveFile()

	else:
		
		pass

	return


def newFile():
	print('newFile')

	global filechange, filepath, file

	if filechange == True:

		saveQuest()

	else:

		pass

	filechange = False
	filepath = 'New'
	textw.delete('1.0', END)
	textw.insert('1.0', open('empty.pianoscript', 'r').read()) # For test purposes
	render('q')
	root.title(f'PianoScript - {filepath}')
	
	return


def openFile():
	print('openFile')

	global filechange, filepath, file

	if filechange == True:

		saveQuest()

	else:

		pass

	f = filedialog.askopenfile(parent=root, mode='rb', title='Open')
	
	if f:

		textw.delete('1.0', END)
		textw.insert('1.0', f.read())
		render('q')

	else:

		return
	
	filechange = False
	filepath = f.name
	root.title(f'PianoScript - {filepath}')
	
	return


def saveFile():
	print('saveFile')

	global filechange
	
	if filepath == 'New':

		saveAs()
		filechange = False
		fileChange('x')# ?
		return

	else:

		f = open(filepath, 'w')
		d = textw.get('1.0', END + '-1c')
		f.write(d)
		f.close()

	filechange = False
	fileChange('x')
	root.title(f'PianoScript - {filepath}')

	return


def saveAs():
	print('saveAs')

	global filepath, filechange

	f = filedialog.asksaveasfile(mode='w', parent=root)

	if f:

		d = textw.get('1.0', END + '-1c')
		f.write(d)
		f.close()
		
		filechange = False
		filepath = f.name
		root.title(f'PianoScript - {filepath}')

	else:

		pass

	return


def quitEditor():
	print('quitEditor')
	
	global filechange

	if filechange == True:

		saveQuest()

	else:

		pass

	root.destroy()


def getFile():
	global file
	file = textw.get('1.0', END + '-1c')
	return file


def fileChecker():# checks if save file is valid and raises error if not.
	pass

menu.add_separator()
menu.add_command(label ="New", command=newFile)
menu.add_command(label ="Open", command=openFile)
menu.add_command(label ="Save", command=saveFile)
menu.add_command(label ="Save as", command=saveAs)
menu.add_separator()
menu.add_command(label ="Quit", command=quitEditor)

















##########################################################################
## Tools			 													##
##########################################################################

def bracketExtractor(text, openbracket, closebracket):


	def search_symbol_return_index(search, symbol):

		cntr = -1
		index = []
		for i in search:
			cntr += 1
			if i.find(symbol) == 0:
				index.append(cntr)
			else:
				pass
		return index


	start = search_symbol_return_index(text, openbracket)
	end = search_symbol_return_index(text, closebracket)
	startend = list(zip(start, end))
	voicelist = []

	for i in startend:
		voicelist.append(text[i[0]+1:i[1]])

	return voicelist


def strip_file(f):
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


def durationConverter(string): # converts duration string to length in 'pianotick' format.
			
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
		return

	return dur


def string2pitch(string):
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
	ret = pitchdict[string]
	return ret


def barline_pos_list(gridlist):
	barlinepos = [0]
	for grid in gridlist:
		cntr = 0
		for i in range(grid[3]):
			nxtbarln = barlinepos[-1] + grid[1]
			barlinepos.append(nxtbarln)
	return barlinepos


def newline_pos_list(gridlist, mpline):
	gridlist = barline_pos_list(gridlist)
	linelist = [0]
	cntr = 0
	for barline in gridlist:
		cntr += mpline
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
	lowest and highest note.
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
		x = 70
		canvas.create_line(x, y, x+printareawidth, y, width=2)
		canvas.create_line(x, y+10, x+printareawidth, y+10, width=2)
		canvas.create_line(x, y+20, x+printareawidth, y+20, width=2)


	def draw2Line(y):
		x = 70
		canvas.create_line(x, y, x+printareawidth, y, width=1)
		canvas.create_line(x, y+10, x+printareawidth, y+10, width=1)


	def drawDash2Line(y):
		x = 70
		canvas.create_line(x, y, x+printareawidth, y, width=1, dash=(6,6))
		canvas.create_line(x, y+10, x+printareawidth, y+10, width=1, dash=(6,6))

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
		canvas.create_line(70, keyline+205+y, 70+printareawidth, keyline+205+y, width=2)


def draw_paper(y):
			
			#canvas.create_rectangle(55, 55+y, 55+paperwidth, 55+paperheigth+y, fill='black', outline='')
			canvas.create_rectangle(50, 50+y, 50+paperwidth, 50+paperheigth+y, fill='white', outline='')
			#canvas.create_rectangle(70, 70+y, 70+printareawidth, 70+printareaheight+y, fill='', outline='blue')


### noteheads ###
def black_key_right(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 6
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
    y0 = y - 5
    x1 = x + 10
    y1 = y + 2.5
    canvas.create_line(x0,y-20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')


def black_key_left(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 6
    y1 = y + 5
    canvas.create_line(x0,y+20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline='black', fill='black')
    canvas.create_oval(x0+4, y0+4, x1-4, y1-4, outline='white', fill='white')
    

def white_key_left_dga(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 10
    y1 = y + 5
    canvas.create_line(x0,y+20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
    canvas.create_oval(x0+4, y0+4, x1-4, y1-4, outline="black")


def white_key_left_cefb(x, y):  # center coordinates, radius
    x0 = x
    y0 = y - 5
    x1 = x + 10
    y1 = y + 2.5
    canvas.create_line(x0,y+20, x0,y, width=2)
    canvas.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
    canvas.create_oval(x0+4, y0+4, x1-4, y1-4, outline="black")
    

def noteStop(x, y):
    #canvas.create_line(x-5,y-5, x, y, x,y, x-5,y+5, width=2) # orginal klavarscribo design
    #canvas.create_line(x,y, x,y+5, x,y+5, x,y-5, x,y-5, x,y, x,y, x-5,y+5, x-5,y+5, x,y, x,y, x-5,y-5, fill='black', width=1.5) # maybe the pianoscript design
    canvas.create_line(x, y-10, x, y+10, fill='black', width=1.5, dash=3)


def note_y_pos(note, mn, mx, cursy):
	'''
	This function returns the position of c4 relative to 'cursy'(the y axis staff cursor)
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


def note_on(x1, x2, y, linenr):
	x1 = event_x_pos(x1, linenr)
	x2 = event_x_pos(x2, linenr)
	canvas.create_rectangle(x1, y-5, x2, y+5, fill='#bbbbbb', outline='')#e3e3e3
	canvas.create_line(x2, y-5, x2, y+5, width=2)


def event_x_pos(pos, linenr):
	newlinepos = newline_pos_list(grid, mpline)
	newlinepos.insert(0, 0)
	linelength = newlinepos[linenr] - newlinepos[linenr-1]
	factor = printareawidth / linelength
	pos = pos - newlinepos[linenr-1]
	xpos = pos * factor + 70
	return xpos


def special_string_change_tool(string, startbracket, endbracket):

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
                    string = replacer(string, "*", rindex)
    return string

##########################################################################
## Main 			 													##
##########################################################################
















## score variables ##
# titles:
title = ''
subtitle = ''
composer = ''
copyright = ''
# settings:
mpline = 4
systemspacing = 50
scale = 100
titlespace = 60
# music:
grid = []
msg = []
pagespace = []

scale_S = scale/100
## constants ##
paperheigth = root.winfo_fpixels('1m') * 297 * (scale_S)  # a4 210x297 mm
paperwidth = root.winfo_fpixels('1m') * 210 * (scale_S)
marginsx = 40 * (scale_S)
marginsy = 60 * (scale_S)
printareawidth = paperwidth - marginsx
printareaheight = paperheigth - marginsy


def render(q):
	global title, subtitle, composer, copyright, mpline, systemspacing, scale, grid, msg, paperheigth, paperwidth, marginsy, marginsx, printareaheight, printareawidth
	grid = []
	msg = []
	

	def reading():
		global scale_S, title, subtitle, composer, copyright, mpline, systemspacing, scale, grid, msg, paperheigth, paperwidth, marginsy, marginsx, printareaheight, printareawidth
		file = strip_file(getFile())

		# set titles if in file
		for i in file.split('\n'):
			if 'title' in i:
				index = i.find('=')+1
				i = i[index:]
				title = i
			else:
				pass

			if 'subtitle' in i:
				index = i.find('=')+1
				i = i[index:]
				subtitle = i
			else:
				pass

			if 'composer' in i:
				index = i.find('=')+1
				i = i[index:]
				composer = i
			else:
				pass

			if 'copyright' in i:
				index = i.find('=')+1
				i = i[index:]
				copyright = i
			else:
				pass

			if 'mpline' in i:
				index = i.find('=')+1
				i = i[index:]
				mpline = int(i)
			else:
				pass

			if 'mgrid' in i:
				index = i.find('=')+1
				i = i[index:]
				mgrid = int(i)
			else:
				pass

			if 'systemspace' in i:
				index = i.find('=')+1
				i = i[index:]
				systemspacing = int(i)
			else:
				pass

			if 'scale' in i:
				index = i.find('=')+1
				i = i[index:]
				scale = int(i)
				scale_S = scale/100
				paperheigth = root.winfo_fpixels('1m') * 297 * (scale_S)  # a4 210x297 mm
				paperwidth = root.winfo_fpixels('1m') * 210 * (scale_S)
				printareawidth = paperwidth - marginsx
				printareaheight = paperheigth - marginsy
			else:
				pass

			if 'grid' in i:
				i = i.split('.')
				i[1] = durationConverter(i[1])
				i[2] = eval(i[2])
				i[3] = eval(i[3])
				grid.append(i)
			else:
				pass










		### reading voices ##
		msgs = bracketExtractor(file, '{', '}')
		V = []
		for v in msgs:
			V.append("".join(v.split()))
		msgs = V
		

		## create messages in list from file ##
		voicelist = []
		ncounter = 0
		prevnote = 0
		for mess in msgs:
			voicelist.insert(0, [])
			splitnote = []
			
			
			# UP
			index = -1
			for symbol in mess:
				index += 1
				fnd = symbol.find('R')
				if fnd == 0:
					voicelist[0].append([index, 'hand', 'R'])
				else:
					pass

			
			# DOWN
			index = -1
			for symbol in mess:
				index += 1
				fnd = symbol.find('L')
				if fnd == 0:
					voicelist[0].append([index, 'hand', 'L'])
				else:
					pass


			# rest
			index = -1
			for symbol in mess:
				index += 1
				fnd = symbol.find('r')
				if fnd == 0:
					voicelist[0].append([index, 'rest'])
				else:
					pass



			# duration
			index = -1
			for symbol in mess:
				index += 1
				fnd = symbol.find('<')
				if fnd == 0:
					d = mess[index+1:mess[index:].find('>') + index] # reads duration in string format.
					if d[0] == '*':
						pass
					else:
						duration = durationConverter(d)
						voicelist[0].append([index, 'duration', duration])
				else:
					pass

			strippedmess = special_string_change_tool(mess, '<', '>')
			index = -1
			for symbol in strippedmess:
				index += 1
				fnd = symbol.find('W')
				if fnd == 0:
					voicelist[0].append([index, 'duration', 1024])
				fnd = symbol.find('H')
				if fnd == 0:
					voicelist[0].append([index, 'duration', 512])
				fnd = symbol.find('Q')
				if fnd == 0:
					voicelist[0].append([index, 'duration', 256])
				fnd = symbol.find('E')
				if fnd == 0:
					voicelist[0].append([index, 'duration', 128])
				fnd = symbol.find('S')
				if fnd == 0:
					voicelist[0].append([index, 'duration', 64])
				fnd = symbol.find('T')
				if fnd == 0:
					voicelist[0].append([index, 'duration', 32])
				


			# note
			index = -1
			for symbol in mess:
				index += 1
				ncounter += 1
				if symbol in ['c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G', 'a', 'A', 'b']:
					try:
						if mess[index+1] in ['1', '2', '3', '4', '5', '6', '7', '8', '0']:
							note = string2pitch(mess[index]+mess[index+1])
							prevnote = note
							try:	
								if mess[index+2] == '-':#if '-' after note
									voicelist[0].append([index, 'note', note, 1, ncounter])
								else:
									voicelist[0].append([index, 'note', note, 0, ncounter])
							except IndexError:
								voicelist[0].append([index, 'note', note, 0, ncounter])
						else:
							pass
					except IndexError:
						pass
				else:
					pass


			# cursor
			index = -1
			for symbol in mess:
				index += 1
				ret = '0'
				dig = ['0','1','2','3','4','5','6','7','8','9']
				if symbol.find('_') >= 0:
					for i in mess[index+1:]:
						if i in dig:
							if ret == '0':
								ret = i
							else:
								ret += i
						elif not i in dig:
							voicelist[0].append([index, 'cursor', eval(ret)])
							break
						else:
							voicelist[0].append([index, 'cursor', 0])
					else:
						pass
				else:
					pass


			# split note (add split note)
			index = -1
			for symbol in mess:
				index += 1
				if symbol.find('=') >= 0:
					voicelist[0].append([index, 'split', prevnote])
				else:
					pass


			# repeats
			index = -1
			for symbol in mess:
				index += 1
				fnd = symbol.find('[')
				if fnd == 0:
					voicelist[0].append([index, 'bgn_rpt'])
				else:
					pass
			index = -1
			for symbol in mess:
				index += 1
				fnd = symbol.find(']')
				if fnd == 0:
					voicelist[0].append([index, 'end_rpt'])
				else:
					pass

			# dashed barline
			index = -1
			for symbol in mess:
				index += 1
				fnd = symbol.find('|')
				if fnd == 0:
					voicelist[0].append([index, 'dashline'])
				else:
					pass

		
		# sort events by index
		for mess in voicelist:
			mess.sort()












		## creating messages for note, barlines, and split with correct begin times ##
		for voice in voicelist:
			
			#default values for every new voice
			hand = 'UP'
			duration = 256
			cursor = 0


			for event in voice:
				if event[1] == 'hand':
					hand = event[2]
				else:
					pass

				if event[1] == 'duration':
					duration = event[2]
				else:
					pass

				if event[1] == 'cursor':
					if event[2] == 0:
						cursor -= duration
					else:
						cursor = barline_pos_list(grid)[event[2]-1]
				else:
					pass

				if event[1] == 'rest':
					cursor += duration
				else:
					pass

				if event[1] == 'note':
					if event[3] == 1:
						msg.append([event[0], 'note', cursor, cursor+duration, event[2], hand, 'bound'])
					else:
						msg.append([event[0], 'note', cursor, cursor+duration, event[2], hand, 'loose'])
					cursor += duration
				else:
					pass

				if event[1] == 'split':
					note = msg[-1][4]
					msg.append([event[0], 'split', cursor, cursor+duration, note])
					cursor += duration
				else:
					pass

				if event[1] == 'dashline':
					msg.append([event[0], 'dashline', cursor])
				else:
					pass

				if event[1] == 'bgn_rpt':
					msg.append([event[0], 'bgn_rpt', cursor])
				else:
					pass

				if event[1] == 'end_rpt':
					msg.append([event[0], 'end_rpt', cursor])
				else:
					pass


		#adding barline messages with correct begin time
		for barline in barline_pos_list(grid):
			msg.insert(0, ['index', 'barline', barline])


		# adding grid messages
		icount = -1
		cursor = 0
		grdpart = []
		for i in grid:
			oldpos = 0
			for add in range(i[3]):
				length = i[1]
				divide = i[2]
				if divide == 0:
					divide = 1
				amount = i[2]
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
		mem = 0
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
				if note[1] == 'note':
					notelst.append(note[4])
				else:
					pass
			try: lineheight.append(staff_height(min(notelst), max(notelst)))
			except ValueError: lineheight.append(10)

		msgs = msg
		msg = []
		cursy = 40 * (scale_S)
		pagelist = []
		icount = 0
		for line, height in zip(msgs, lineheight):
			icount += 1
			cursy += height + systemspacing
			if icount == len(lineheight):#if this is the last iteration
				if cursy <= printareaheight:
					pagelist.append(line)
					msg.append(pagelist)
					break
				elif cursy > printareaheight:
					msg.append(pagelist)
					pagelist = []
					pagelist.append(line)
					msg.append(pagelist)
					break
				else:
					pass
			else:
				if cursy <= printareaheight:#does fit on paper
					pagelist.append(line)
				elif cursy > printareaheight:#does not fit on paper
					msg.append(pagelist)
					pagelist = []
					pagelist.append(line)
					cursy = 0
					cursy += height + systemspacing
				else:
					pass



		## calculation of empty y space on every page
		# 
		print(pagespace)

	reading()

	







	def drawing():
		canvas.delete('all')

		def paper():

			counter = 0
			page_y = 0
			
			for page in msg:
				counter += 1
				draw_paper(page_y)
				canvas.create_text(80, page_y+20+paperheigth, text=f'page {counter} of {len(msg)} | {title} | {copyright} - PianoScript sheet', anchor='w', font=("Terminal", 16, "normal"))
				#canvas.create_rectangle(70, page_y+5+paperheigth, 70+printareawidth, page_y+35+paperheigth)

				page_y += paperheigth + 50

			canvas.create_text(70, 90, text=title, anchor='w', font=("Terminal", 20, "normal"))
			canvas.create_text(70+printareawidth, 90, text=composer, anchor='e', font=("Courier", 20, "normal"))
			#canvas.create_line(10, 400, 10, 400+pagespace[0])
		
		def note_active():
			cursy = 90 + titlespace
			lcounter = 0
			pcounter = 0
			for page in msg:
				pcounter += 1
				
				for line in page:
					lcounter += 1
					#create linenotelist
					linenotelist = []
					for note in line:
						if note[1] == 'note':
							linenotelist.append(note[4])
					if linenotelist:
						minnote = min(linenotelist)
						maxnote = max(linenotelist)
					else:
						minnote = 40
						maxnote = 44

					for note in line:
						if note[1] == 'note':
							note_on(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)
							prevnote = note[3]
						if note[1] == 'split':
							note_on(note[2], note[3], note_y_pos(note[4], minnote, maxnote, cursy), lcounter)

					cursy += staff_height(minnote, maxnote) + systemspacing

				cursy = (paperheigth+50) * pcounter + 90


		def barlines():
			cursy = 90 + titlespace
			pcounter = 0
			lcounter = 0
			bcounter = 0
			
			for page in msg:
				pcounter += 1
				
				
				for line in page:
					lcounter += 1
					
					#create linenotelist
					linenotelist = []
					for note in line:
						if note[1] == 'note'  or note[1] == 'split':
							linenotelist.append(note[4])
					if linenotelist:
						maxnote = max(linenotelist)
						minnote = min(linenotelist)
					else:
						maxnote = 44
						minnote = 40

					staffheight = staff_height(minnote, maxnote)

					for note in line:
		
						if note[1] == 'barline':
							bcounter += 1
							canvas.create_line(event_x_pos(note[2], lcounter), cursy, event_x_pos(note[2], lcounter), cursy+staffheight, width=2)
							canvas.create_text(event_x_pos(note[2]+7.5, lcounter), cursy-20, text=bcounter, anchor='w')

						if note[1] == 'bgn_rpt':
							canvas.create_line(event_x_pos(note[2], lcounter), cursy-30, event_x_pos(note[2], lcounter), cursy+staffheight+20, width=4)
							canvas.create_line(event_x_pos(note[2], lcounter), cursy-30, event_x_pos(note[2], lcounter)+10, cursy-30, width=4)
							canvas.create_line(event_x_pos(note[2], lcounter), cursy+staffheight+20, event_x_pos(note[2], lcounter)+10, cursy+staffheight+20, width=4)

						if note[1] == 'end_rpt':
							canvas.create_line(event_x_pos(note[2], lcounter), cursy-30, event_x_pos(note[2], lcounter), cursy+staffheight+20, width=4)
							canvas.create_line(event_x_pos(note[2], lcounter), cursy-30, event_x_pos(note[2], lcounter)-10, cursy-30, width=4)
							canvas.create_line(event_x_pos(note[2], lcounter), cursy+staffheight+20, event_x_pos(note[2], lcounter)-10, cursy+staffheight+20, width=4)

					canvas.create_line(70+printareawidth, cursy, 70+printareawidth, cursy+staffheight, width=2)
					
					if lcounter == len(newline_pos_list(grid, mpline)):
						canvas.create_line(70+printareawidth, cursy, 70+printareawidth, cursy+staffheight, width=5)
					
					
					cursy += staffheight + systemspacing

				cursy = (paperheigth+50) * pcounter + 90


		def staff():
			cursy = 90 + titlespace
			pcounter = 0
			lcounter = 0
			for page in msg:
				pcounter += 1
				
				
				for line in page:
					lcounter += 1
					#create linenotelist
					linenotelist = []
					for note in line:
						if note[1] == 'note' or note[1] == 'split':
							linenotelist.append(note[4])
					if linenotelist:
						maxnote = max(linenotelist)
						minnote = min(linenotelist)
					else:
						maxnote = 44
						minnote = 40

					draw_staff_lines(cursy, minnote, maxnote)
					#canvas.create_text(25, cursy+5, text=lcounter)
					staffheight = staff_height(minnote, maxnote)
					
					cursy += staffheight + systemspacing

				cursy = (paperheigth+50) * pcounter + 90


		def note_start():
			black = [2, 5, 6, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
			white_dga = [6,11,13,18,23,25,30,35,37,42,47,49,54,59,61,66,71,73,78,83,85,88]
			white_be = [3,8,15,20,27,32,39,44,51,56,63,68,75,80,87] # possible typos
			white_cf = [1,4,9,16,21,28,33,40,45,52,57,64,69,76,81] # possible typos
			
			cursy = 90 + titlespace
			pcounter = 0
			lcounter = 0
			for page in msg:
				pcounter += 1

				for line in page:
					lcounter += 1


					# create max/min note variables for line
					linenotelist = []
					for note in line:
						if note[1] == 'note':
							linenotelist.append(note[4])
					if linenotelist:
						minnote = min(linenotelist)
						maxnote = max(linenotelist)
					else:
						minnote = 40
						maxnote = 44
					
					staffheight = staff_height(minnote, maxnote)



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

							if note[4] in white_dga:
							
								if note[5] == 'R':
									white_key_right_dga(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
								elif note[5] == 'L':
									white_key_left_dga(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
								# elif note[0] == 'split':
								# 	print('!!!')
								else:
									pass

							if note[4] in white_cf:
								
								if note[5] == 'R':
									white_key_right_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
								elif note[5] == 'L':
									white_key_left_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy))
								# elif note[0] == 'split':
								# 	print('!!!')
								else:
									pass

							if note[4] in white_be:
								
								if note[5] == 'R':
									white_key_right_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)+1.5)
								elif note[5] == 'L':
									white_key_left_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[4], minnote, maxnote, cursy)+1.5)
								# elif note[0] == 'split':
								# 	print('!!!')
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



					cursy += staffheight + systemspacing

				cursy = (paperheigth+50) * pcounter + 90


		def grid_lines():
			cursy = 90 + titlespace
			pcounter = 0
			lcounter = 0
			for page in msg:
				pcounter += 1

				for line in page:
					lcounter += 1

					# create max/min note variables for line
					linenotelist = []
					for note in line:
						if note[1] == 'note':
							linenotelist.append(note[4])
					if linenotelist:
						minnote = min(linenotelist)
						maxnote = max(linenotelist)
					else:
						minnote = 40
						maxnote = 44
					
					staffheight = staff_height(minnote, maxnote)

					for gridline in line:
						if gridline[1] == 'dash':
							canvas.create_line(event_x_pos(gridline[2], 
												lcounter), 
												cursy+(staffheight*0.25), 
												event_x_pos(gridline[2], 
												lcounter), 
												cursy+staffheight-(staffheight*0.25), 
												dash=(6, 6))

					cursy += staffheight + systemspacing

				cursy = (paperheigth+50) * pcounter + 90


		# function order
		paper()
		note_active()
		barlines()
		staff()
		grid_lines()
		note_start()

	drawing()
	canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))
	return len(msg)









def exportPDF():
	print('exportPDF')

	f = filedialog.asksaveasfile(mode='w', parent=root, filetypes=[("Postscript","*.ps")])

	if f:
		name = f.name[:-3]
		counter = 0

		for export in range(render('q')):
			counter += 1
			print('printing page ', counter, '!')
			canvas.postscript(file=f"{name} p {counter}.ps", colormode='gray', x=50, y=50+(export*(paperheigth+50)), width=paperwidth, height=paperheigth, rotate=False)
			os.remove(f.name)

	else:

		pass

	return

menu.add_command(label ="export postscript...", command=exportPDF)


def autosave(q):
	global filepath
	if filepath == 'New':
		render('q')
	else:
		saveFile()
		render('q')









newFile()
#exportPDF()
root.bind('<Key>', autosave)
root.mainloop()