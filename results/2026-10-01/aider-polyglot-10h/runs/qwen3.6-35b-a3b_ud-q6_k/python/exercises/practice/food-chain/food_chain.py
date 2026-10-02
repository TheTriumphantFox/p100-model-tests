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

    all_lines = []

    for i in range(start_verse, end_verse + 1):
        verse_lines = []
        animal_index = i - 1
        animal = animals[animal_index]

        verse_lines.append(f"I know an old lady who swallowed a {animal}.")

        if animal == "horse":
            verse_lines.append(reactions[animal_index])
            all_lines.extend(verse_lines)
            continue

        if animal_index > 0:
            verse_lines.append(reactions[animal_index])

        for j in range(animal_index, 0, -1):
            prey = animals[j]
            predator = animals[j - 1]
            line = f"She swallowed the {predator} to catch the {prey}"
            if prey == "spider":
                line += " that wriggled and jiggled and tickled inside her"
            line += "."
            verse_lines.append(line)

        verse_lines.append("I don't know why she swallowed the fly. Perhaps she'll die.")

        all_lines.extend(verse_lines)

    return all_lines
