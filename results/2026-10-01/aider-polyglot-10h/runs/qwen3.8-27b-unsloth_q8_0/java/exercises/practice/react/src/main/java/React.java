import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;

public class React {

    public static class Cell<T> {
        protected T value;

        public T getValue() {
            return value;
        }

        protected void setValue(T newValue) {
            this.value = newValue;
        }
    }

    public static class InputCell<T> extends Cell<T> {
        private final List<ComputeCell<T>> dependents = new ArrayList<>();

        public InputCell(T initialValue) {
            super();
            this.value = initialValue;
        }

        public void setValue(T newValue) {
            if (this.value == null ? newValue != null : !this.value.equals(newValue)) {
                this.value = newValue;
                for (ComputeCell<T> dependent : dependents) {
                    dependent.recompute();
                }
            }
        }

        void addDependent(ComputeCell<T> dependent) {
            dependents.add(dependent);
        }
    }

    public static class ComputeCell<T> extends Cell<T> {
        private final Function<List<T>, T> function;
        private final List<Cell<T>> cells;
        private final List<Consumer<T>> callbacks = new ArrayList<>();
        private final List<ComputeCell<T>> dependents = new ArrayList<>();

        public ComputeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
            super();
            this.function = function;
            this.cells = cells;
            this.value = computeValue();
            
            for (Cell<T> cell : cells) {
                if (cell instanceof InputCell) {
                    InputCell<T> inputCell = (InputCell<T>) cell;
                    inputCell.addDependent(this);
                } else if (cell instanceof ComputeCell) {
                    ComputeCell<T> computeCell = (ComputeCell<T>) cell;
                    computeCell.addDependent(this);
                }
            }
        }

        private T computeValue() {
            List<T> values = new ArrayList<>();
            for (Cell<T> cell : cells) {
                values.add(cell.getValue());
            }
            return function.apply(values);
        }

        void recompute() {
            T newValue = computeValue();
            if (this.value == null ? newValue != null : !this.value.equals(newValue)) {
                this.value = newValue;
                for (ComputeCell<T> dependent : dependents) {
                    dependent.recompute();
                }
                for (Consumer<T> callback : callbacks) {
                    callback.accept(newValue);
                }
            }
        }

        void addDependent(ComputeCell<T> dependent) {
            dependents.add(dependent);
        }

        public void addCallback(Consumer<T> callback) {
            callbacks.add(callback);
        }

        public void removeCallback(Consumer<T> callback) {
            callbacks.remove(callback);
        }
    }

    public static <T> InputCell<T> inputCell(T initialValue) {
        return new InputCell<>(initialValue);
    }

    public static <T> ComputeCell<T> computeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
        return new ComputeCell<>(function, cells);
    }
}
