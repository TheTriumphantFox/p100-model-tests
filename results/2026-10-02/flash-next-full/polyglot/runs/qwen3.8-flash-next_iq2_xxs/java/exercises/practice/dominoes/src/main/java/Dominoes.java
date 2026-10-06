import java.util.ArrayList;
import java.util.List;

class Dominoes {

    List<Domino> formChain(List<Domino> inputDominoes) throws ChainNotFoundException {
        if (inputDominoes == null || inputDominoes.isEmpty()) {
            return new ArrayList<>();
        }

        List<Domino> chain = new ArrayList<>();
        boolean[] used = new boolean[inputDominoes.size()];

        // Start with the first domino
        chain.add(inputDominoes.get(0));
        used[0] = true;

        if (findChain(chain, inputDominoes, used)) {
            return chain;
        } else {
            throw new ChainNotFoundException("No domino chain found.");
        }
    }

    private boolean findChain(List<Domino> chain, List<Domino> dominoes, boolean[] used) {
        if (chain.size() == dominoes.size()) {
            // Check if the chain is closed: first left == last right
            Domino first = chain.get(0);
            Domino last = chain.get(chain.size() - 1);
            return first.getLeft() == last.getRight();
        }

        int lastRight = chain.get(chain.size() - 1).getRight();

        for (int i = 0; i < dominoes.size(); i++) {
            if (!used[i]) {
                Domino domino = dominoes.get(i);
                
                // Try orientation 1: left matches previous right
                if (domino.getLeft() == lastRight) {
                    chain.add(domino);
                    used[i] = true;
                    if (findChain(chain, dominoes, used)) {
                        return true;
                    }
                    chain.remove(chain.size() - 1);
                    used[i] = false;
                }

                // Try orientation 2: right matches previous left (flip)
                if (domino.getRight() == lastRight) {
                    Domino flipped = new Domino(domino.getRight(), domino.getLeft());
                    chain.add(flipped);
                    used[i] = true;
                    if (findChain(chain, dominoes, used)) {
                        return true;
                    }
                    chain.remove(chain.size() - 1);
                    used[i] = false;
                }
            }
        }

        return false;
    }

}
