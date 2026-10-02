class BottleSong {

    String recite(int startBottles, int takeDown) {
        StringBuilder song = new StringBuilder();
        for (int i = 0; i < takeDown; i++) {
            int current = startBottles - i;
            int next = current - 1;
            
            String currentWord = numberToWord(current);
            String nextWord = numberToWord(next);
            
            String currentBottle = bottleWord(current);
            String nextBottle = bottleWord(next);
            
            String firstLine = capitalize(currentWord) + " green " + currentBottle + " hanging on the wall,";
            String secondLine = firstLine;
            String thirdLine = "And if one green bottle should accidentally fall,";
            String fourthLine = "There'll be " + nextWord + " green " + nextBottle + " hanging on the wall.";
            
            song.append(firstLine).append("\n");
            song.append(secondLine).append("\n");
            song.append(thirdLine).append("\n");
            song.append(fourthLine).append("\n");
            
            if (i < takeDown - 1) {
                song.append("\n");
            }
        }
        return song.toString();
    }
    
    private String numberToWord(int n) {
        switch (n) {
            case 0: return "no";
            case 1: return "one";
            case 2: return "two";
            case 3: return "three";
            case 4: return "four";
            case 5: return "five";
            case 6: return "six";
            case 7: return "seven";
            case 8: return "eight";
            case 9: return "nine";
            case 10: return "ten";
            default: return "";
        }
    }
    
    private String bottleWord(int n) {
        return n == 1 ? "bottle" : "bottles";
    }
    
    private String capitalize(String s) {
        if (s == null || s.isEmpty()) return s;
        return s.substring(0, 1).toUpperCase() + s.substring(1);
    }

}
