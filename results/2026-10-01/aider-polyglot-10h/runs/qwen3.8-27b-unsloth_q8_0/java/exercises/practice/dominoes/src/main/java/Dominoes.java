import java.util.ArrayList;
import java.util.List;

class Dominoes {

    List<Domino> formChain(List<Domino> inputDominoes) throws ChainNotFoundException {
        if (inputDominoes == null || inputDominoes.isEmpty()) {
            return new ArrayList<>();
        }

        List<Domino> result = backtrack(new ArrayList<>(), new ArrayList<>(inputDominoes), -1);
        if (result == null) {
            throw new ChainNotFoundException("No valid chain found");
        }
        return result;
    }

    private List<Domino> backtrack(List<Domino> currentChain, List<Domino> remaining, int currentEnd) {
        if (remaining.isEmpty()) {
            if (currentChain.isEmpty()) {
                return new ArrayList<>();
            }
            int start = currentChain.get(0).getLeft();
            if (start == currentEnd) {
                return new ArrayList<>(currentChain);
            }
            return null;
        }

        for (int i = 0; i < remaining.size(); i++) {
            Domino d = remaining.get(i);
            List<Domino> newRemaining = new ArrayList<>(remaining);
            newRemaining.remove(i);

            // Try orientation: left matches currentEnd
            if (currentEnd == -1 || d.getLeft() == currentEnd) {
                currentChain.add(d);
                List<Domino> result = backtrack(currentChain, newRemaining, d.getRight());
                if (result != null) {
                    return result;
                }
                currentChain.remove(currentChain.size() - 1);
            }

            // Try orientation: right matches currentEnd (flip the domino)
            if (currentEnd == -1 || d.getRight() == currentEnd) {
                Domino flipped = new Domino(d.getRight(), d.getLeft());
                currentChain.add(flipped);
                List<Domino> result = backtrack(currentChain, newRemaining, d.getLeft());
                if (result != null) {
                    return result;
                }
                currentChain.remove(currentChain.size() - 1);
            }
        }

        return null;
    }
}
