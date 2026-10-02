class BottleSong {

    String recite(int startBottles, int takeDown) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < takeDown; i++) {
            if (i > 0) {
                sb.append("\n\n");
            }
            sb.append(verse(startBottles - i));
        }
        return sb.toString();
    }

    private String verse(int bottles) {
        String currentWord = numberToWord(bottles);
        int nextBottles = bottles - 1;
        String nextWord = numberToWord(nextBottles);
        
        String currentBottleStr = bottles == 1 ? "bottle" : "bottles";
        String nextBottleStr = nextBottles == 1 ? "bottle" : "bottles";
        
        String line1 = capitalize(currentWord) + " green " + currentBottleStr + " hanging on the wall,";
        String line2 = line1;
        String line3 = "And if one green bottle should accidentally fall,";
        String line4 = "There'll be " + nextWord.toLowerCase() + " green " + nextBottleStr + " hanging on the wall.";
        
        return line1 + "\n" + line2 + "\n" + line3 + "\n" + line4;
    }

    private String numberToWord(int number) {
        switch (number) {
            case 10: return "Ten";
            case 9: return "Nine";
            case 8: return "Eight";
            case 7: return "Seven";
            case 6: return "Six";
            case 5: return "Five";
            case 4: return "Four";
            case 3: return "Three";
            case 2: return "Two";
            case 1: return "One";
            case 0: return "no";
            default: return "";
        }
    }

    private String capitalize(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1).toLowerCase();
    }

}
