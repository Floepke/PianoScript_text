'''This file contains functions about logic.'''



'''This function can handle a list. It gives True if the search value is in the list.
The third number(deflexion) adds a tolerance to the search value. 
Example: numberInList(List, 5, 1) The function will return True if there is a number in the 
source between 4 and 6.'''
def numberInList(searchlist, search, deflexion):
    funcout = False
    for i in searchlist:
        if i >= (search-deflexion) and i <= (search+deflexion):
            funcout = True
    return funcout


''' Returns the difference between two given values in positive number. '''
def difference(x, y):
    if x>=y:
        return x-y
    if y>x:
        return y-x


from itertools import tee, islice, chain
def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)