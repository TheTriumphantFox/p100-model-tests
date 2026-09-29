def Strongest_Extension(class_name, extensions):
    best = None
    best_strength = float('-inf')
    for ext in extensions:
        cap = sum(1 for c in ext if c.isupper())
        sm = sum(1 for c in ext if c.islower())
        strength = cap - sm
        if strength > best_strength:
            best_strength = strength
            best = ext
    return f"{class_name}.{best}"
