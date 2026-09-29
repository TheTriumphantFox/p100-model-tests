def total_match(lst1, lst2):
    count1 = sum(len(s) for s in lst1)
    count2 = sum(len(s) for s in lst2)
    if count1 <= count2:
        return lst1
    else:
        return lst2
