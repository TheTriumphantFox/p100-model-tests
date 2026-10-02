import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;

public class React {

    // Base cell class
    public static abstract class Cell<T> {
        protected T value;

        public T getValue() {
            return value;
        }
    }

    // Input cell: value can be set by user
    public static class InputCell<T> extends Cell<T> {
        public InputCell(T initialValue) {
            this.value = initialValue;
        }

        public void setValue(T newValue) {
            if ((value == null && newValue != null) || (value != null && !value.equals(newValue))) {
                this.value = newValue;
                // Trigger recomputation of all compute cells
                React.recomputeAll();
            }
        }
    }

    // Compute cell: value is derived from other cells
    public static class ComputeCell<T> extends Cell<T> {
        private final Function<List<T>, T> function;
        private final List<Cell<T>> dependencies;
        private final List<Consumer<T>> callbacks = new ArrayList<>();
        private T previousValue;

        public ComputeCell(Function<List<T>, T> function, List<Cell<T>> dependencies) {
            this.function = function;
            this.dependencies = dependencies;
            // Initial computation
            recompute();
            // Register this compute cell for global recomputation
            React.registerComputeCell(this);
        }

        // Recompute value based on dependencies
        private void recompute() {
            List<T> depValues = new ArrayList<>();
            for (Cell<T> dep : dependencies) {
                depValues.add(dep.getValue());
            }
            T newValue = function.apply(depValues);
            if ((value == null && newValue != null) || (value != null && !value.equals(newValue))) {
                previousValue = value;
                value = newValue;
                // Notify callbacks after stable state
                for (Consumer<T> cb : callbacks) {
                    cb.accept(value);
                }
            }
        }

        public void addCallback(Consumer<T> callback) {
            callbacks.add(callback);
        }

        public void removeCallback(Consumer<T> callback) {
            callbacks.remove(callback);
        }

        // Called by global recompute loop
        private void recomputeIfNeeded() {
            List<T> depValues = new ArrayList<>();
            for (Cell<T> dep : dependencies) {
                depValues.add(dep.getValue());
            }
            T newValue = function.apply(depValues);
            if ((value == null && newValue != null) || (value != null && !value.equals(newValue))) {
                previousValue = value;
                value = newValue;
                // Call callbacks immediately; they will be invoked after stable state
                for (Consumer<T> cb : callbacks) {
                    cb.accept(value);
                }
            }
        }
    }

    // Static list of all compute cells for recomputation
    private static final Set<ComputeCell<?>> computeCells = new HashSet<>();

    private static void registerComputeCell(ComputeCell<?> cell) {
        computeCells.add(cell);
    }

    // Recompute all compute cells until stable
    private static void recomputeAll() {
        boolean changed;
        do {
            changed = false;
            for (ComputeCell<?> cell : computeCells) {
                // Store old value
                Object old = cell.getValue();
                cell.recomputeIfNeeded();
                if (old != null && !old.equals(cell.getValue())) {
                    changed = true;
                } else if (old == null && cell.getValue() != null) {
                    changed = true;
                }
            }
        } while (changed);
    }

    // Factory methods
    public static <T> InputCell<T> inputCell(T initialValue) {
        return new InputCell<>(initialValue);
    }

    public static <T> ComputeCell<T> computeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
        return new ComputeCell<>(function, cells);
    }
}
