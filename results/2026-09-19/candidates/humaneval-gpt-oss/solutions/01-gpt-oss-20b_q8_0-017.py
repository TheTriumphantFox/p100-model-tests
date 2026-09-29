from typing import List


def parse_music(music_string: str) -> List[int]:
    """Parse a string of musical notes into a list of beat counts.

    The input string contains tokens separated by whitespace. Each token
    represents a note in a simple ASCII notation:

    - 'o'   → whole note, 4 beats
    - 'o|'  → half note, 2 beats
    - '.|'  → quarter note, 1 beat

    Any other token is ignored.

    Args:
        music_string: The string containing the musical notation.

    Returns:
        A list of integers, each representing the number of beats for a note.
    """
    beat_map = {"o": 4, "o|": 2, ".|": 1}
    beats: List[int] = []

    for token in music_string.split():
        if token in beat_map:
            beats.append(beat_map[token])

    return beats
