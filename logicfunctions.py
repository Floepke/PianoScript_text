'''
This file contains functions about logic.
'''



'''
This function can handle a list or variable. It gives True if the search value is in the source.
The third number(searchoffset) adds a tolerance to the search value. 
Example: numberInSource(source, 5, 1) The function will return True if there is a number in the source
between 4 and 6.
'''
def numberInSource(source, search, searchoffset):
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
        if source >= (search-searchoffset) and i <= (search+searchoffset):
            funcout = True
    return funcout


''' Returns the difference between two given values in positive number. '''
def difference(x, y):
    if x>=y:
        return x-y
    if y>x:
        return y-x