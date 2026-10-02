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

    private static final String[] ACTIONS = {
        "",
        "that lay in ",
        "that ate ",
        "that killed ",
        "that worried ",
        "that tossed ",
        "that milked ",
        "that kissed ",
        "that married ",
        "that woke ",
        "that kept ",
        "that belonged to "
    };

    String verse(int verse) {
        StringBuilder sb = new StringBuilder("This is ");
        for (int i = verse; i >= 1; i--) {
            sb.append(SUBJECTS[i - 1]);
            if (i > 1) {
                sb.append(ACTIONS[i - 1]);
            } else {
                sb.append(".");
            }
        }
        return sb.toString();
    }

    String verses(int startVerse, int endVerse) {
        StringBuilder sb = new StringBuilder();
        for (int i = startVerse; i <= endVerse; i++) {
            if (i > startVerse) {
                sb.append("\n");
            }
            sb.append(verse(i));
        }
        return sb.toString();
    }

    String sing() {
        return verses(1, 12);
    }

}
