def recite(start_verse, end_verse):
    animals = [
        ("fly", "I don't know why she swallowed the fly. Perhaps she'll die."),
        ("spider", "It wriggled and jiggled and tickled inside her."),
        ("bird", "How absurd to swallow a bird!"),
        ("cat", "Imagine that, to swallow a cat!"),
        ("dog", "What a hog, to swallow a dog!"),
        ("goat", "Just opened her throat and swallowed a goat!"),
        ("cow", "I don't know how she swallowed a cow!"),
        ("horse", "She's dead, of course!")
    ]

    verses = []
    for i in range(start_verse - 1, end_verse):
        verse = []
        verse.append(f"I know an old lady who swallowed a {animals[i][0]}.")
        verse.append(animals[i][1])

        if i > 0:
            # Build the cumulative chain
            chain = []
            for j in range(i, 0, -1):
                if j == 1:  # Special case for spider
                    chain.append(f"She swallowed the {animals[j][0]} to catch the {animals[j-1][0]} that {animals[j-1][1].lower()}")
                else:
                    chain.append(f"She swallowed the {animals[j][0]} to catch the {animals[j-1][0]}.")

            verse.extend(chain)
            verse.append(animals[0][1])

        verses.extend(verse)
        if i < end_verse - 1:
            verses.append("")

    return verses
