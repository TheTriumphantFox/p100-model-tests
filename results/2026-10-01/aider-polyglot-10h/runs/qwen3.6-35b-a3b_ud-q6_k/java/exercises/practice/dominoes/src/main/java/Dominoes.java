import java.util.List;
import java.util.ArrayList;

class Dominoes {

    public List<Domino> formChain(List<Domino> inputDominoes) throws ChainNotFoundException {
        if (inputDominoes == null || inputDominoes.isEmpty()) {
            return new ArrayList<>();
        }

        // Check if a single domino is valid (must be a double, e.g., [1|1])
        if (inputDominoes.size() == 1) {
            Domino d = inputDominoes.get(0);
            if (d.getLeft() == d.getRight()) {
                return new ArrayList<>(inputDominoes);
            } else {
                throw new ChainNotFoundException("No chain possible");
            }
        }

        // Check degree parity for Eulerian path/circuit existence
        // Although backtracking will handle it, this is a good sanity check or optimization.
        // However, since we need to return the actual chain, we proceed with backtracking.
        
        List<Domino> chain = new ArrayList<>();
        chain.add(inputDominoes.get(0));
        boolean[] used = new boolean[inputDominoes.size()];
        used[0] = true;

        if (buildChain(inputDominoes, chain, used)) {
            return chain;
        } else {
            throw new ChainNotFoundException("No chain possible");
        }
    }

    private boolean buildChain(List<Domino> inputDominoes, List<Domino> chain, boolean[] used) {
        if (chain.size() == inputDominoes.size()) {
            // Check if the chain is closed (first left == last right)
            Domino first = chain.get(0);
            Domino last = chain.get(chain.size() - 1);
            return first.getLeft() == last.getRight();
        }

        Domino lastDomino = chain.get(chain.size() - 1);
        int target = lastDomino.getRight();

        for (int i = 1; i < inputDominoes.size(); i++) {
            if (!used[i]) {
                Domino d = inputDominoes.get(i);
                
                // Try matching left side
                if (d.getLeft() == target) {
                    used[i] = true;
                    chain.add(d);
                    if (buildChain(inputDominoes, chain, used)) {
                        return true;
                    }
                    chain.remove(chain.size() - 1);
                    used[i] = false;
                }
                
                // Try matching right side (flip)
                // Note: If left == right, we already tried it above. 
                // But typically flipping a double [1|1] is same as not flipping.
                // We should avoid double processing if d.getLeft() == d.getRight()
                if (d.getLeft() != d.getRight() && d.getRight() == target) {
                    used[i] = true;
                    chain.add(new Domino(d.getRight(), d.getLeft()));
                    if (buildChain(inputDominoes, chain, used)) {
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
