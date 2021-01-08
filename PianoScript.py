### IMPORTS ###
from tkinter import Tk, Text, PanedWindow, Canvas, Scrollbar, Menu, filedialog, END, messagebox, simpledialog
import platform















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
	textw.insert('1.0', open('test.pianoscript', 'r').read()) # For test purposes

	root.title(f'PianoScript - {filepath}')
	render('x')
	
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

	else:

		return
	
	filechange = False
	filepath = f.name
	root.title(f'PianoScript - {filepath}')
	render('x')
	
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

## constants ##
scale = 100
paperheigth = root.winfo_fpixels('1m') * 297 * (scale/100)  # a4 210x297 mm
paperwidth = root.winfo_fpixels('1m') * 210 * (scale/100)
marginsx = 20
marginsy = 20
printareawidth = paperwidth - (marginsx * 2)
printareaheight = paperheigth - (marginsy * 2)-20


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


def search_word_return_index(search, symbol):

		cntr = -1
		index = []
		for i in search:
			cntr += 1
			if i.find(symbol) == 0:
				index.append(cntr)
			else:
				pass
		return index


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



def voice_per_line(grid, mpline, voices):
	'''returns a list with 'lines' of music
	which contain notes. structure:
	[[lines[notes]]'''
	newlinepos = newline_pos_list(grid, mpline)
	voiceperline = []
	bottpos = 0
	for newln in newlinepos:
		hlplst = []
		for note in voices:
			if note[2] >= bottpos and note[2] < newln:
				hlplst.append(note)
		voiceperline.append(hlplst)
		bottpos = newln
	
	return voiceperline


def staff_height(mn, mx):
	'''
	This function returns the height of the staff based on the
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



def line_height_list(grid, mpline, voices):
	'''returns a list of heights for each line of music'''

	voiceperline = voice_per_line(grid, mpline, voices)
	linentlst = []
	lineheightlst = []

	for line in voiceperline:
		notelst = []
		for note in line:
			notelst.append(note[1])
		linentlst.append(notelst)
	for height in linentlst:
		if height:
			staffheight = staff_height(min(height), max(height))
			lineheightlst.append(staffheight)
		else:
			staffheight = staff_height(40, 44)
			lineheightlst.append(staffheight)
	return lineheightlst


def page_list(grid, mpline, voices, printareaheight):
	'''returns a list of lines of notes'''
	linevoices = voice_per_line(grid, mpline, voices)
	lineheight = line_height_list(grid, mpline, voices)

	cursy = 0
	count = -1
	finalcount = len(lineheight)-1
	page = []
	pages = [] # fn outputlist

	for line, height in zip(linevoices, lineheight):

		count += 1
		height = height + systemspacing + cursy
		# print('!', count+1, line, height, printareaheight)
		if count == finalcount:
			if height <= printareaheight:
				page.append(line)
				pages.append(page)
			elif height > printareaheight:
				pages.append(page)
				page = []
				page.append(line)
				pages.append(page)
			else:
				pass
			break

		if height <= printareaheight:
			page.append(line)
			cursy = height
		elif height > printareaheight:
			pages.append(page)
			page = []
			page.append(line)
			cursy = lineheight[count] # maybe we need to add systemspacing variable
		else:
			pass
	
	return pages


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
			
			canvas.create_rectangle(55, 55+y, 55+paperwidth, 55+paperheigth+y, fill='black', outline='')
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

def diff(x, y):
	if x >= y:
		return x - y
	elif y > x:
		return y - x
	else:
		pass
	return


def event_x_pos(pos, linenr):
	newlinepos = newline_pos_list(grid, mpline)
	newlinepos.insert(0, 0)
	linelength = diff(newlinepos[linenr], newlinepos[linenr-1])
	factor = printareawidth / linelength
	pos = pos - newlinepos[linenr-1]
	xpos = pos * factor + 70
	return xpos


def note_on(x1, x2, y, linenr):
	x1 = event_x_pos(x1, linenr)
	x2 = event_x_pos(x2, linenr)
	canvas.create_rectangle(x1, y-5, x2, y+5, fill='#bbbbbb', outline='')#e3e3e3
	canvas.create_line(x2, y-5, x2, y+5, width=2)


def barline_list(grid):
    barlines = []
    mem = 0
    for g in grid:
        
        for i in range(g[3]):
            barlines.append(['barline', mem, g[2]])
            mem += g[1]
    return barlines



##########################################################################
## Main			 														##
##########################################################################
















## render variables ##
titlepage = True
pagenumber = 1


## score variables ##
# titles:
title = ''
subtitle = ''
composer = ''
copyright = ''
# settings:
mpline = 4
mgrid = 4
systemspacing = 50
# music:
grid = []
voices = []
measurelines = []

def render(y):
	global title, subtitle, composer, copyright, mpline, grid, voices, staff, mgrid, scale, paperheigth, paperwidth, marginsx, marginsy, printareawidth, printareaheight
	
	fileChecker()

	#clear score lists and variables for rerendering
	title = ''
	subtitle = ''
	composer = ''
	copyright = ''
	mpline = 5
	mgrid = 4
	scale = 100
	grid = []
	staff = []
	voices = []

	def readFile():# this function sets a set of lists and preferences from the score file.
		global title, subtitle, composer, copyright, mpline, grid, voices, staff, mgrid, scale, paperheigth, paperwidth, marginsx, marginsy, printareawidth, printareaheight


		# remove comments
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
		

		# remove comments and empty lines from file
		f = strip_file(getFile())
		
		# set titles if in file
		for i in f.split('\n'):
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

			if 'scale' in i:
				index = i.find('=')+1
				i = i[index:]
				scale = int(i)
				paperheigth = root.winfo_fpixels('1m') * 297 * (scale/100)  # a4 210x297 mm
				paperwidth = root.winfo_fpixels('1m') * 210 * (scale/100)
				marginsx = 20
				marginsy = 20
				printareawidth = paperwidth - (marginsx * 2)
				printareaheight = paperheigth - (marginsy * 2)-20
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


		### VOICES ###
		voices = bracketExtractor(f, '{', '}')

		V = []

		for v in voices:
			V.append("".join(v.split()))

		voices = V


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
			return pitchdict[string]

		
		## create messages in list from file ##
		voicelist = []

		for voice in voices:
			voicelist.insert(0, [])
			splitnote = []
			
			# UP
			index = -1
			for symbol in voice:
				index += 1
				fnd = symbol.find('R')
				if fnd == 0:
					voicelist[0].append([index, 'hand', 'R'])
				else:
					pass

			
			# DOWN
			index = -1
			for symbol in voice:
				index += 1
				fnd = symbol.find('L')
				if fnd == 0:
					voicelist[0].append([index, 'hand', 'L'])
				else:
					pass


			# rest
			index = -1
			for symbol in voice:
				index += 1
				fnd = symbol.find('r')
				if fnd == 0:
					voicelist[0].append([index, 'rest'])
				else:
					pass


			# duration
			index = -1
			for symbol in voice:
				index += 1
				fnd = symbol.find('<')
				if fnd == 0:
					d = voice[index+1:voice[index:].find('>') + index] # reads duration in string format.
					duration = durationConverter(d)
					voicelist[0].append([index, 'duration', duration])
				else:
					pass


			# note
			index = -1
			for symbol in voice:
				index += 1
				if symbol in ['c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G', 'a', 'A', 'b']:
					if voice[index+1] in ['1', '2', '3', '4', '5', '6', '7', '8', '0']:
						note = string2pitch(voice[index]+voice[index+1])
						try:	
							if voice[index+2] == '-':#if '-' after note
								voicelist[0].append([index, 'note', note, 1])
							else:
								voicelist[0].append([index, 'note', note, 0])
						except IndexError:
							voicelist[0].append([index, 'note', note, 0])
					else:
						pass
				else:
					pass


			# cursor
			index = -1
			for symbol in voice:
				index += 1
				ret = '0'
				dig = ['0','1','2','3','4','5','6','7','8','9']
				if symbol.find('_') >= 0:
					for i in voice[index+1:]:
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
			for symbol in voice:
				index += 1
				if symbol.find('=') >= 0:
					voicelist[0].append([index, 'split'])
				else:
					pass

		
		# sort events by index
		for voice in voicelist:
			voice.sort()


		## creating note messages with begin and length using all messages ##
		voices = []
		
		for voice in voicelist:
			_voice = []
			
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
						voices.append(['note', event[2], cursor, cursor+duration, hand, 'bound'])
					else:
						voices.append(['note', event[2], cursor, cursor+duration, hand, 'loose'])
					cursor += duration
				else:
					pass

				if event[1] == 'split':
					note = voices[-1][1]
					voices.append(['split', note, cursor, cursor+duration, 'dummy', 'dummy'])
					cursor += duration
				else:
					pass
		

		voices = page_list(grid, mpline, voices, printareaheight)

		# creating a measure list organized in page and lines of music
		def measure_loop_list():
			barlinepos = barline_pos_list(grid)
			newlinepos = newline_pos_list(grid, mpline)
		
		measurelines = measure_loop_list()
		
		return

	readFile()

	### print file data in console:
	print('\nRender:', '\nTitle = ', title, '\nSubtitle = ', subtitle, '\nComposer = ', 
		composer, '\nCopyright = ', copyright, '\nGrid = ', grid, '\nNotes = \n')

	for page in voices:
		print(f'page {len(page)}:', page)
		for line in page:
			print('line: ', line)
			for note in line:
				pass#print(note)






		









	def drawing():
		canvas.delete('all')
		
		
		def paper():

			counter = 0
			page_y = 0
			
			for page in voices:
				counter += 1
				draw_paper(page_y)
				canvas.create_text(80, page_y+80+printareaheight, text=f'page {counter} | {title} by {composer} | {copyright} - PianoScript®', anchor='w')
				canvas.create_rectangle(70, page_y+70+printareaheight, 70+printareawidth, page_y+90+printareaheight)

				page_y += paperheigth + 50
			
		paper()


		def barlines():
			barlines = []
			mem = 0
			for g in grid:

				for i in range(g[3]):
					barlines.append(['barline', mem, g[2]])
					mem += g[1]
			barlines = [barlines[n:n+mpline] for n in range(0, len(barlines), mpline)]
			print(barlines)









		


		def active_note():
			
			cursy = 90
			lcounter = 0
			pcounter = 0
			for page in voices:
				pcounter += 1
				
				for line in page:
					lcounter += 1
					#create linenotelist
					linenotelist = []
					for note in line:
						linenotelist.append(note[1])
					if linenotelist:
						minnote = min(linenotelist)
						maxnote = max(linenotelist)
					else:
						minnote = 0
						maxnote = 0

					for note in line:
						note_on(note[2], note[3], note_y_pos(note[1], minnote, maxnote, cursy), lcounter)

					cursy += staff_height(minnote, maxnote) + systemspacing

				cursy = (paperheigth+50) * pcounter + 90



		def staff():

			cursy = 90
			pcounter = 0
			for page in voices:
				pcounter += 1
				lcounter = 0
				
				for line in page:
					lcounter += 1
					#create linenotelist
					linenotelist = []
					for note in line:
						linenotelist.append(note[1])
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


		def notes():
			black = [2, 5, 6, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43, 46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82, 84, 86]
			white_dga = [6,11,13,18,23,25,30,35,37,42,47,49,54,59,61,66,71,73,78,83,85,88]
			white_be = [3,8,15,20,27,32,39,44,51,56,63,68,75,80,87] # possible typos
			white_cf = [1,4,9,16,21,28,33,40,45,52,57,64,69,76,81] # possible typos
			
			cursy = 90
			lcounter = 0
			pcounter = 0
			for page in voices:
				pcounter += 1
				
				for line in page:
					lcounter += 1
					#create linenotelist
					linenotelist = []
					for note in line:
						linenotelist.append(note[1])
					if linenotelist:
						minnote = min(linenotelist)
						maxnote = max(linenotelist)



					old_x = 0
					old_y = 0
					boundloose = 0

					for note in line:
						
						if note[1] in white_dga:
							
							if note[4] == 'R':
								white_key_right_dga(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy))
							elif note[4] == 'L':
								white_key_left_dga(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy))
							# elif note[0] == 'split':
							# 	print('!!!')
							else:
								pass

						if note[1] in white_cf:
							
							if note[4] == 'R':
								white_key_right_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy))
							elif note[4] == 'L':
								white_key_left_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy))
							# elif note[0] == 'split':
							# 	print('!!!')
							else:
								pass

						if note[1] in white_be:
							
							if note[4] == 'R':
								white_key_right_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy)+1.5)
							elif note[4] == 'L':
								white_key_left_cefb(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy)+1.5)
							# elif note[0] == 'split':
							# 	print('!!!')
							else:
								pass

						if note[1] in black:
							
							if note[4] == 'R':
								black_key_right(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy))
							elif note[4] == 'L':
								black_key_left(event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy))
							else:
								pass

						
						if boundloose == 1:
							canvas.create_line(old_x, old_y, event_x_pos(note[2], lcounter), note_y_pos(note[1], minnote, maxnote, cursy)-20, width=3)

						if note[5] == 'bound':
							boundloose = 1
							old_x = event_x_pos(note[2], lcounter)
							old_y = note_y_pos(note[1], minnote, maxnote, cursy)-20
						elif note[5] == 'loose':
							boundloose = 0
						else:
							pass


						

					cursy += staff_height(minnote, maxnote) + systemspacing

				cursy = (paperheigth+50) * pcounter + 90

		# drawing order:
		# grid()
		active_note()
		barlines()
		staff()
		notes()



	drawing()
	canvas.configure(scrollregion=bbox_offset(canvas.bbox("all")))

def exportPDF():
	canvas.postscript(file="~/Desktop/export.ps", colormode='gray', x=50, y=50, width=paperwidth, height=paperheigth, rotate=False)

menu.add_command(label ="export", command=exportPDF)


	



















root.bind('<Key>', fileChange)
root.bind('<Key>', render)
newFile()
root.mainloop()