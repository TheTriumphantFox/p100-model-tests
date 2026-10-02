class House {

    private static final String[] PARTS = {
        "the house that Jack built",
        "the malt that lay in",
        "the rat that ate",
        "the cat that killed",
        "the dog that worried",
        "the cow with the crumpled horn that tossed",
        "the maiden all forlorn that milked",
        "the man all tattered and torn that kissed",
        "the priest all shaven and shorn that married",
        "the rooster that crowed in the morn that woke",
        "the farmer sowing his corn that kept",
        "the horse and the hound and the horn that belonged to"
    };

    String verse(int verse) {
        StringBuilder sb = new StringBuilder();
        sb.append("This is ");
        for (int i = verse - 1; i >= 0; i--) {
            if (i == 0) {
                sb.append(PARTS[0]);
            } else {
                sb.append(PARTS[i]);
                sb.append(" ");
            }
        }
        sb.append(".");
        return sb.toString();
    }

    String verses(int startVerse, int endVerse) {
        StringBuilder sb = new StringBuilder();
        for (int i = startVerse; i <= endVerse; i++) {
            sb.append(verse(i));
            sb.append("\n");
        }
        return sb.toString();
    }

    String sing() {
        return verses(1, 12);
    }

}
