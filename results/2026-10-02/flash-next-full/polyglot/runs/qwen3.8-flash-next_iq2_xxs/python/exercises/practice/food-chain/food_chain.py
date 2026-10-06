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
    comments = [
        "I don't know why she swallowed the fly. Perhaps she'll die.",
        "It wriggled and jiggled and tickled inside her.",
        "How absurd to swallow a bird!",
        "Imagine that, to swallow a cat!",
        "What a hog, to swallow a dog!",
        "Just opened her throat and swallowed a goat!",
        "I don't know how she swallowed a cow!",
        "She's dead, of course!"
    ]
    chain = [
        "She swallowed the spider to catch the fly.",
        "She swallowed the bird to catch the spider that wriggled and jiggled and tickled inside her.",
        "She swallowed the cat to catch the bird.",
        "She swallowed the dog to catch the cat.",
        "She swallowed the goat to catch the dog.",
        "She swallowed the cow to catch the goat."
    ]

    verses = []
    for i in range(start_verse - 1, end_verse):
        verse = []
        verse.append(f"I know an old lady who swallowed a {animals[i]}.")
        if i == 0:
            verse.append(comments[0])
        elif i == len(animals) - 1:
            verse.append(comments[-1])
        else:
            verse.append(comments[i])
            for j in range(i, 0, -1):
                verse.append(chain[j - 1])
            verse.append(comments[0])
        verses.extend(verse)
        if i != end_verse - 1:
            verses.append("")

    return verses
