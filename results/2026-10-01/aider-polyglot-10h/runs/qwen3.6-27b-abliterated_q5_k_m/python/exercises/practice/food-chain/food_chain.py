def recite(start_verse, end_verse):
    animals = [
        "fly",
        "spider",
        "bird",
        "cat",
        "dog",
        "goat",
        "cow",
        "horse"
    ]

    reactions = [
        "",
        "It wriggled and jiggled and tickled inside her.",
        "How absurd to swallow a bird!",
        "Imagine that, to swallow a cat!",
        "What a hog, to swallow a dog!",
        "Just opened her throat and swallowed a goat!",
        "I don't know how she swallowed a cow!",
        "She's dead, of course!"
    ]

    verses = []
    for i in range(start_verse, end_verse + 1):
        idx = i - 1
        animal = animals[idx]
        verse = [f"I know an old lady who swallowed a {animal}."]
        
        if idx > 0:
            verse.append(reactions[idx])
        
        if idx == 7:
            # Horse verse ends early
            pass
        else:
            # Cumulative part
            for j in range(idx, 0, -1):
                predator = animals[j]
                prey = animals[j-1]
                if prey == "spider":
                    verse.append(f"She swallowed the {predator} to catch the {prey} that wriggled and jiggled and tickled inside her.")
                else:
                    verse.append(f"She swallowed the {predator} to catch the {prey}.")
            
            verse.append("I don't know why she swallowed the fly. Perhaps she'll die.")
        
        verses.append(verse)

    # Flatten the list of lists into a single list, adding empty strings between verses
    result = []
    for i, verse in enumerate(verses):
        result.extend(verse)
        if i < len(verses) - 1:
            result.append("")
            
    return result
