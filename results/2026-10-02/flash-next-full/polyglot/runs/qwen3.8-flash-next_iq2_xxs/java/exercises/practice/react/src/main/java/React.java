import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.ArrayList;

public class React {

    public static class Cell<T> {
        protected T value;
        protected final List<ComputeCell<?>> dependents = new ArrayList<>();

        public T getValue() {
            return value;
        }

        public void addDependent(ComputeCell<?> dependent) {
            dependents.add(dependent);
        }
    }

    public static class InputCell<T> extends Cell<T> {

        public InputCell(T initialValue) {
            this.value = initialValue;
        }

        public void setValue(T newValue) {
            if (this.value != null && this.value.equals(newValue)) {
                return;
            }
            this.value = newValue;
            // Notify all dependent compute cells to update their values
            for (ComputeCell<?> dependent : dependents) {
                dependent.update();
            }
        }
    }

    public static class ComputeCell<T> extends Cell<T> {
        private final Function<List<T>, T> function;
        private final List<Cell<?>> dependencies;
        private final List<Consumer<T>> callbacks = new ArrayList<>();

        public ComputeCell(Function<List<T>, T> function, List<Cell<?>> dependencies) {
            this.function = function;
            this.dependencies = dependencies;
            // Register this compute cell as a dependent of each cell it depends on
            for (Cell<?> dep : dependencies) {
                dep.addDependent(this);
            }
            // Initialize the value
            this.update();
        }

        public void addCallback(Consumer<T> callback) {
            callbacks.add(callback);
        }

        public void removeCallback(Consumer<T> callback) {
            callbacks.remove(callback);
        }

        public void update() {
            List<T> values = new ArrayList<>();
            for (Cell<?> dep : dependencies) {
                values.add((T) dep.getValue());
            }
            T newValue = function.apply(values);
            if (this.value == null || !this.value.equals(newValue)) {
                this.value = newValue;
                // Notify callbacks if value changed
                for (Consumer<T> callback : callbacks) {
                    callback.accept(newValue);
                }
            }
        }
    }

    public static <T> InputCell<T> inputCell(T initialValue) {
        return new InputCell<>(initialValue);
    }

    public static <T> ComputeCell<T> computeCell(Function<List<T>, T> function, List<Cell<?>> dependencies) {
        return new ComputeCell<>(function, dependencies);
    }
}
