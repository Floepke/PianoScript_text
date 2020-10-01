#########################################################
# tools(functions)                                      #
#########################################################

<<<<<<< Updated upstream
### noteheads ###
def black_key(x, y, widget):  # center coordinates, radius
    x0 = x - 5
=======
'''Inside this file are all general functions from the project'''

def difference(x, y):
    if x >= y:
        return x - y
    if y > x:
        return y - x


def quartersFitInMeasure(numerator, denominator):# gives the number of quarter notes that fit in one measure of the given time-signature.
    w = 0
    n = numerator
    d = denominator
    if d < 4:
        w = (n * d) / (d / 2)
    if d == 4:
        w = (n * d) / d
    if d > 4:
        w = (n * d) / (d * 2)
    return w


def numberInSource(source, search, searchoffset):# checks if search value is in source.
    funcout = False
    def isIterable(x):
        try:
            iter(x)
            return True
        except TypeError:
            return False

    if isIterable(source) == True:
        for i in source:
            if i >= (search-searchoffset) and i <= (search+searchoffset):
                funcout = True

    if isIterable(source) == False:
        if source >= (search-searchoffset) and source <= (search+searchoffset):
            funcout = True
    return funcout

def black_key(x, y, widget):
    x0 = x - 4
>>>>>>> Stashed changes
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    widget.create_oval(x0, y0, x1, y1, outline='black', fill='black')
<<<<<<< Updated upstream
    widget.create_line(x0+1,y, x0+1,y-40, width=2)


def black_key_left(x, y, widget):  # center coordinates, radius
=======
    widget.create_line(x0 + 1, y, x0 + 1, y - 40, width=2)


def black_key_left(x, y, widget):
>>>>>>> Stashed changes
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    widget.create_oval(x0, y0, x1, y1, outline='black', fill='black')
<<<<<<< Updated upstream
    widget.create_oval(x0+4, y0+4, x1-4, y1-4, outline='white', fill='white')
    widget.create_line(x0+1,y, x0+1,y+40, width=2)


def white_key(x, y, widget):  # center coordinates, radius
=======
    widget.create_oval(x0 + 4, y0 + 4, x1 - 4, y1 - 4, outline='white', fill='white')
    widget.create_line(x0 + 1, y, x0 + 1, y + 40, width=2)


def white_key(x, y, widget):
>>>>>>> Stashed changes
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    widget.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
<<<<<<< Updated upstream
    widget.create_line(x0+1,y, x0+1,y-40, width=2)


def white_key_left(x, y, widget):  # center coordinates, radius
=======
    widget.create_line(x0 + 1, y, x0 + 1, y - 40, width=2)


def white_key_left(x, y, widget):
>>>>>>> Stashed changes
    x0 = x - 5
    y0 = y - 5
    x1 = x + 5
    y1 = y + 5
    widget.create_oval(x0, y0, x1, y1, outline="black", width=2, fill='white')
<<<<<<< Updated upstream
    widget.create_oval(x0+4, y0+4, x1-4, y1-4, outline="black")
    widget.create_line(x0+1,y, x0+1,y+40, width=2)


def noteStop(x, y, widget):
    #widget.create_line(x-5,y-5, x, y, x,y, x-5,y+5, width=2) # orginal klavarscribo design
    widget.create_line(x,y, x,y+5, x,y+5, x,y-5, x,y-5, x,y, x,y, x-5,y+5, x-5,y+5, x,y, x,y, x-5,y-5, fill='black', width=2) # maybe the pianoscript design
=======
    widget.create_oval(x0 + 4, y0 + 4, x1 - 4, y1 - 4, outline="black")
    widget.create_line(x0 + 1, y, x0 + 1, y + 40, width=2)


def noteStop(x, y, widget):
    widget.create_line(x - 5, y - 5, x, y, x, y, x - 5, y + 5, width=2)  # orginal klavarscribo design
    # widget.create_line(x,y, x,y+5, x,y+5, x,y-5, x,y-5, x,y, x,y, x-5,y+5, x-5,y+5, x,y, x,y, x-5,y-5, fill='black', width=2) # maybe the pianoscript design
>>>>>>> Stashed changes
