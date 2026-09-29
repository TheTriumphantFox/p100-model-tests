def max_fill(grid, capacity):
    import math
    total_water = 0
    for well in grid:
        total_water += sum(well)
    return math.ceil(total_water / capacity)
