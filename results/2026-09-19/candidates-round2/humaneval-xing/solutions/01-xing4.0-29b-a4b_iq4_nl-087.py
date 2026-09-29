def get_row(lst, x):
    result = []
    for i, row in enumerate(lst):
        if not row:
            continue
        for j, val in enumerate(row):
            if val == x:
                result.append((i, j))
    # Sort by row ascending, then by column descending within each row
    result.sort(key=lambda t: (t[0], -t[1]))
    return result
