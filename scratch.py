grid = [['grid', 256, 0, 1], ['grid', 1024, 4, 12]]
mpline = 5

def barline_list(grid):
    barlines = []
    mem = 0
    for g in grid:
        
        for i in range(g[3]):
            barlines.append(['barline', mem, g[2]])
            mem += g[1]
    barlines = [barlines[n:n+mpline] for n in range(0, len(barlines), mpline)]
    return barlines


print(barline_list(grid))