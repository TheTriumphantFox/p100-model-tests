class House {

    private static final String[] PHRASES = {
        "the house that Jack built.",
        "the malt\nthat lay in the house that Jack built.",
        "the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the cow with the crumpled horn\nthat tossed the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the maiden all forlorn\nthat milked the cow with the crumpled horn\nthat tossed the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the man all tattered and torn\nthat kissed the maiden all forlorn\nthat milked the cow with the crumpled horn\nthat tossed the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the priest all shaven and shorn\nthat married the man all tattered and torn\nthat kissed the maiden all forlorn\nthat milked the cow with the crumpled horn\nthat tossed the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the rooster that crowed in the morn\nthat woke the priest all shaven and shorn\nthat married the man all tattered and torn\nthat kissed the maiden all forlorn\nthat milked the cow with the crumpled horn\nthat tossed the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the farmer sowing his corn\nthat kept the rooster that crowed in the morn\nthat woke the priest all shaven and shorn\nthat married the man all tattered and torn\nthat kissed the maiden all forlorn\nthat milked the cow with the crumpled horn\nthat tossed the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built.",
        "the horse and the hound and the horn\nthat belonged to the farmer sowing his corn\nthat kept the rooster that crowed in the morn\nthat woke the priest all shaven and shorn\nthat married the man all tattered and torn\nthat kissed the maiden all forlorn\nthat milked the cow with the crumpled horn\nthat tossed the dog\nthat worried the cat\nthat killed the rat\nthat ate the malt\nthat lay in the house that Jack built."
    };

    String verse(int verse) {
        StringBuilder sb = new StringBuilder();
        sb.append("This is ");
        for (int i = verse - 1; i >= 0; i--) {
            if (i == 0) {
                sb.append(PHRASES[i]);
            } else {
                sb.append(PHRASES[i].split("\n")[0]);
                sb.append(" that ");
            }
        }
        return sb.toString();
    }

    String verses(int startVerse, int endVerse) {
        StringBuilder sb = new StringBuilder();
        for (int i = startVerse; i <= endVerse; i++) {
            sb.append(verse(i));
            if (i < endVerse) {
                sb.append("\n\n");
            }
        }
        return sb.toString();
    }

    String sing() {
        return verses(1, 12);
    }

}
