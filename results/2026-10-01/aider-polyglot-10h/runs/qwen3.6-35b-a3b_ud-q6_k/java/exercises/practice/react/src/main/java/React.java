import java.util.List;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;

public class React {

    public static class Cell<T> {
        public T getValue() {
            throw new UnsupportedOperationException("Please implement the Cell.getValue() method");
        }
    }

    public static class InputCell<T> extends Cell<T> {
        private T value;
        private final List<ComputeCell<T>> dependents = new ArrayList<>();

        public InputCell(T initialValue) {
            this.value = initialValue;
        }

        @Override
        public T getValue() {
            return value;
        }

        public void setValue(T newValue) {
            if (value == null && newValue == null) {
                return;
            }
            if (value != null && value.equals(newValue)) {
                return;
            }
            this.value = newValue;
            
            Set<ComputeCell<T>> visited = new HashSet<>();
            for (ComputeCell<T> dependent : dependents) {
                dependent.propagate(visited);
            }
        }

        void addDependent(ComputeCell<T> computeCell) {
            dependents.add(computeCell);
        }
    }

    public static class ComputeCell<T> extends Cell<T> {
        private T value;
        private final Function<List<T>, T> function;
        private final List<Cell<T>> inputCells;
        private final List<ComputeCell<T>> dependents = new ArrayList<>();
        private final Set<Consumer<T>> callbacks = new HashSet<>();
        private T previousValue;

        public ComputeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
            this.function = function;
            this.inputCells = cells;
            this.previousValue = null;
            this.value = computeValue();
            
            for (Cell<T> cell : cells) {
                if (cell instanceof InputCell) {
                    ((InputCell<T>) cell).addDependent(this);
                } else if (cell instanceof ComputeCell) {
                    ((ComputeCell<T>) cell).addDependent(this);
                }
            }
        }

        @Override
        public T getValue() {
            return value;
        }

        public void addCallback(Consumer<T> callback) {
            callbacks.add(callback);
        }

        public void removeCallback(Consumer<T> callback) {
            callbacks.remove(callback);
        }

        private T computeValue() {
            List<T> inputValues = new ArrayList<>();
            for (Cell<T> cell : inputCells) {
                inputValues.add(cell.getValue());
            }
            return function.apply(inputValues);
        }

        void propagate(Set<ComputeCell<T>> visited) {
            if (visited.contains(this)) {
                return;
            }
            visited.add(this);

            T newValue = computeValue();
            
            boolean changed = false;
            if (value == null && newValue != null) {
                changed = true;
            } else if (value != null && newValue == null) {
                changed = true;
            } else if (value != null && newValue != null && !value.equals(newValue)) {
                changed = true;
            }

            if (changed) {
                previousValue = value;
                value = newValue;
                
                List<ComputeCell<T>> currentDependents = new ArrayList<>(dependents);
                for (ComputeCell<T> dependent : currentDependents) {
                    dependent.propagate(visited);
                }

                for (Consumer<T> callback : callbacks) {
                    callback.accept(value);
                }
            }
        }
        
        void addDependent(ComputeCell<T> computeCell) {
            dependents.add(computeCell);
        }
    }

    public static <T> InputCell<T> inputCell(T initialValue) {
        return new InputCell<>(initialValue);
    }

    public static <T> ComputeCell<T> computeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
        return new ComputeCell<>(function, cells);
    }
}
