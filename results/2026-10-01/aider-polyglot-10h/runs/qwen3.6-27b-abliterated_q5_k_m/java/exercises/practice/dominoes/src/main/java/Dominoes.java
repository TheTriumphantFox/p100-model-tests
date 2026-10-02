import java.util.List;
import java.util.ArrayList;
import java.util.Collections;

class Dominoes {

    List<Domino> formChain(List<Domino> inputDominoes) throws ChainNotFoundException {
        if (inputDominoes.isEmpty()) {
            return new ArrayList<>();
        }

        List<Domino> chain = new ArrayList<>();
        boolean[] used = new boolean[inputDominoes.size()];
        
        // Start with the first domino in the input list
        // We can fix the first domino because the chain is circular, 
        // so any valid chain can be rotated to start with the first domino.
        // However, the first domino can be flipped.
        
        Domino first = inputDominoes.get(0);
        
        // Try first domino as is
        chain.add(first);
        used[0] = true;
        if (solve(inputDominoes, chain, used)) {
            return chain;
        }
        
        // Backtrack
        chain.remove(0);
        used[0] = false;
        
        // Try first domino flipped
        if (first.getLeft() != first.getRight()) {
            chain.add(new Domino(first.getRight(), first.getLeft()));
            used[0] = true;
            if (solve(inputDominoes, chain, used)) {
                return chain;
            }
        }
        
        throw new ChainNotFoundException("No chain found");
    }

    private boolean solve(List<Domino> inputDominoes, List<Domino> chain, boolean[] used) {
        if (chain.size() == inputDominoes.size()) {
            // Check if the chain is closed (loop)
            Domino first = chain.get(0);
            Domino last = chain.get(chain.size() - 1);
            return first.getLeft() == last.getRight();
        }

        int currentEnd = chain.get(chain.size() - 1).getRight();

        for (int i = 0; i < inputDominoes.size(); i++) {
            if (!used[i]) {
                Domino d = inputDominoes.get(i);
                
                // Try normal orientation
                if (d.getLeft() == currentEnd) {
                    chain.add(d);
                    used[i] = true;
                    if (solve(inputDominoes, chain, used)) {
                        return true;
                    }
                    chain.remove(chain.size() - 1);
                    used[i] = false;
                }
                
                // Try flipped orientation
                if (d.getRight() == currentEnd) {
                    // Only flip if it's different from normal to avoid duplicate work for doubles
                    if (d.getLeft() != d.getRight()) {
                        chain.add(new Domino(d.getRight(), d.getLeft()));
                        used[i] = true;
                        if (solve(inputDominoes, chain, used)) {
                            return true;
                        }
                        chain.remove(chain.size() - 1);
                        used[i] = false;
                    }
                }
            }
        }
        
        return false;
    }
}
