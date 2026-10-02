def recite(start_verse, end_verse):
    """
    Generate the lyrics of the cumulative song "I Know an Old Lady Who Swallowed a Fly"
    from verse `start_verse` to verse `end_verse` (1-indexed, inclusive).

    Parameters
    ----------
    start_verse : int
        The first verse number to include.
    end_verse : int
        The last verse number to include.

    Returns
    -------
    list[str]
        The requested portion of the song, with verses separated by a blank line.
    """
    # Define the animals in order and the special lines that accompany each
    animals = [
        ("fly", "I know an old lady who swallowed a fly.", "I don't know why she swallowed the fly. Perhaps she'll die."),
        ("spider", "I know an old lady who swallowed a spider.", "It wriggled and jiggled and tickled inside her."),
        ("bird", "I know an old lady who swallowed a bird.", "How absurd to swallow a bird!"),
        ("cat", "I know an old lady who swallowed a cat.", "Imagine that, to swallow a cat!"),
        ("dog", "I know an old lady who swallowed a dog.", "What a hog, to swallow a dog!"),
        ("goat", "I know an old lady who swallowed a goat.", "Just opened her throat and swallowed a goat!"),
        ("cow", "I know an old lady who swallowed a cow.", "I don't know how she swallowed a cow!"),
        ("horse", "I know an old lady who swallowed a horse.", "She's dead, of course!"),
    ]

    # Build each verse as a list of lines
    verses = []
    for idx, (animal, intro, outro) in enumerate(animals, start=1):
        verse_lines = [intro]
        # Add the special line for all animals except the fly
        if animal != "fly":
            verse_lines.append(outro)
        # For the horse, we do not add any cumulative lines
        if animal == "horse":
            verses.append(verse_lines)
            continue

        # Build the cumulative chain from the current animal down to the fly
        # We walk backwards through the animals list
        for j in range(idx - 1, 0, -1):
            current = animals[j][0]
            previous = animals[j - 1][0]
            if previous == "spider":
                line = f"She swallowed the {current} to catch the {previous} that wriggled and jiggled and tickled inside her."
            else:
                line = f"She swallowed the {current} to catch the {previous}."
            verse_lines.append(line)

        # Finally add the outro line for the fly
        verse_lines.append(outro)
        verses.append(verse_lines)

    # Flatten the requested range of verses, inserting a blank line between them
    selected = []
    for v in verses[start_verse - 1 : end_verse]:
        selected.extend(v)
        selected.append("")  # blank line after each verse
    # Remove the trailing blank line
    if selected and selected[-1] == "":
        selected.pop()

    return selected
