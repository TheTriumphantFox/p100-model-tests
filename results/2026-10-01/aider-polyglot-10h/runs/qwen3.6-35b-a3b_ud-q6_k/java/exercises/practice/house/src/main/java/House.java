class House {

    private static final String[] SUBJECTS = {
        "the house that Jack built",
        "the malt",
        "the rat",
        "the cat",
        "the dog",
        "the cow with the crumpled horn",
        "the maiden all forlorn",
        "the man all tattered and torn",
        "the priest all shaven and shorn",
        "the rooster that crowed in the morn",
        "the farmer sowing his corn",
        "the horse and the hound and the horn"
    };

    private static final String[] VERBS = {
        "",
        "that lay in",
        "that ate",
        "that killed",
        "that worried",
        "that tossed",
        "that milked",
        "that kissed",
        "that married",
        "that woke",
        "that kept",
        "that belonged to"
    };

    String verse(int verse) {
        StringBuilder sb = new StringBuilder();
        sb.append("This is ").append(SUBJECTS[verse - 1]);

        for (int i = verse - 1; i > 0; i--) {
            sb.append(" ").append(VERBS[i]).append(" ").append(SUBJECTS[i - 1]);
        }

        sb.append(".");
        return sb.toString();
    }

    String verses(int startVerse, int endVerse) {
        StringBuilder sb = new StringBuilder();
        for (int i = startVerse; i <= endVerse; i++) {
            sb.append(verse(i));
            if (i < endVerse) {
                sb.append("\n");
            }
        }
        return sb.toString();
    }

    String sing() {
        return verses(1, 12);
    }

}
