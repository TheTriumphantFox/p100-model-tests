import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;

public class React {

    public static class Cell<T> {
        private T value;

        public T getValue() {
            return value;
        }

        void setValue(T newValue) {
            this.value = newValue;
        }
    }

    public static class InputCell<T> extends Cell<T> {
        private final List<ComputeCell<T>> dependents = new ArrayList<>();

        public InputCell(T initialValue) {
            setValue(initialValue);
        }

        public void setValue(T newValue) {
            if (newValue == null && getValue() == null) {
                return;
            }
            if (newValue != null && newValue.equals(getValue())) {
                return;
            }
            
            setValue(newValue);
            
            // Collect all compute cells that need to be updated
            Set<ComputeCell<T>> toUpdate = new HashSet<>();
            Set<ComputeCell<T>> visited = new HashSet<>();
            
            // Use a queue for BFS to find all dependents
            List<ComputeCell<T>> queue = new ArrayList<>(dependents);
            while (!queue.isEmpty()) {
                ComputeCell<T> cell = queue.remove(0);
                if (visited.add(cell)) {
                    toUpdate.add(cell);
                    queue.addAll(cell.dependents);
                }
            }
            
            // Sort the cells to update based on dependency order (topological sort)
            // Since it's a DAG, we can just process them in an order where dependencies are processed first.
            // A simple way is to repeatedly find cells whose dependencies are all in 'visited' or not in 'toUpdate'.
            // However, for this exercise, a simpler approach is often sufficient if we just recompute.
            // Let's use a more robust topological sort approach for the subset of cells to update.
            
            List<ComputeCell<T>> sortedCells = new ArrayList<>();
            Set<ComputeCell<T>> processed = new HashSet<>();
            
            // We need to process cells in an order such that if A depends on B, B is processed before A.
            // We can do this by repeatedly finding cells in 'toUpdate' whose dependencies are either 
            // not in 'toUpdate' or have already been processed.
            
            boolean changed = true;
            while (changed) {
                changed = false;
                for (ComputeCell<T> cell : toUpdate) {
                    if (processed.contains(cell)) continue;
                    
                    boolean allDepsProcessed = true;
                    for (Cell<T> dep : cell.dependencies) {
                        if (dep instanceof ComputeCell && toUpdate.contains(dep) && !processed.contains(dep)) {
                            allDepsProcessed = false;
                            break;
                        }
                    }
                    
                    if (allDepsProcessed) {
                        cell.recompute();
                        processed.add(cell);
                        changed = true;
                    }
                }
            }
            
            // Notify callbacks for cells that actually changed value
            for (ComputeCell<T> cell : processed) {
                cell.notifyCallbacks();
            }
        }

        void addDependent(ComputeCell<T> dependent) {
            dependents.add(dependent);
        }
    }

    public static class ComputeCell<T> extends Cell<T> {
        private final Function<List<T>, T> function;
        private final List<Cell<T>> dependencies;
        private final List<ComputeCell<T>> dependents = new ArrayList<>();
        private final List<Consumer<T>> callbacks = new ArrayList<>();

        public ComputeCell(Function<List<T>, T> function, List<Cell<T>> dependencies) {
            this.function = function;
            this.dependencies = dependencies;
            
            for (Cell<T> dep : dependencies) {
                if (dep instanceof InputCell) {
                    ((InputCell<T>) dep).addDependent(this);
                } else if (dep instanceof ComputeCell) {
                    ((ComputeCell<T>) dep).addDependent(this);
                }
            }
            
            recompute();
        }

        public void addCallback(Consumer<T> callback) {
            callbacks.add(callback);
        }

        public void removeCallback(Consumer<T> callback) {
            callbacks.remove(callback);
        }

        void addDependent(ComputeCell<T> dependent) {
            dependents.add(dependent);
        }

        void recompute() {
            List<T> values = new ArrayList<>();
            for (Cell<T> dep : dependencies) {
                values.add(dep.getValue());
            }
            setValue(function.apply(values));
        }

        void notifyCallbacks() {
            for (Consumer<T> callback : callbacks) {
                callback.accept(getValue());
            }
        }
    }

    public static <T> InputCell<T> inputCell(T initialValue) {
        return new InputCell<>(initialValue);
    }

    public static <T> ComputeCell<T> computeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
        return new ComputeCell<>(function, cells);
    }
}
