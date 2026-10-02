import java.util.List;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

public class React {

    public static class Cell<T> {
        private T value;
        private boolean dirty = true;

        public T getValue() {
            if (dirty) {
                throw new IllegalStateException("Cell value is not computed yet");
            }
            return value;
        }

        protected void setValue(T newValue) {
            if (newValue == null && this.value != null || newValue != null && !newValue.equals(this.value)) {
                this.value = newValue;
                dirty = true;
            }
        }

        protected void markClean() {
            dirty = false;
        }

        protected boolean isDirty() {
            return dirty;
        }
    }

    public static class InputCell<T> extends Cell<T> {
        public InputCell(T initialValue) {
            super.setValue(initialValue);
            super.markClean();
        }

        public void setValue(T newValue) {
            super.setValue(newValue);
        }
    }

    public static class ComputeCell<T> extends Cell<T> {
        private final Function<List<T>, T> function;
        private final List<Cell<T>> cells;
        private final Set<Consumer<T>> callbacks = new HashSet<>();

        public ComputeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
            this.function = function;
            this.cells = cells;
        }

        public void addCallback(Consumer<T> callback) {
            callbacks.add(callback);
        }

        public void removeCallback(Consumer<T> callback) {
            callbacks.remove(callback);
        }

        protected void compute() {
            List<T> values = new ArrayList<>();
            for (Cell<T> cell : cells) {
                values.add(cell.getValue());
            }
            T newValue = function.apply(values);
            T oldValue = super.getValue();
            super.setValue(newValue);
            if (newValue == null && oldValue != null || newValue != null && !newValue.equals(oldValue)) {
                for (Consumer<T> callback : callbacks) {
                    callback.accept(newValue);
                }
            }
            super.markClean();
        }
    }

    public static <T> InputCell<T> inputCell(T initialValue) {
        return new InputCell<>(initialValue);
    }

    public static <T> ComputeCell<T> computeCell(Function<List<T>, T> function, List<Cell<T>> cells) {
        ComputeCell<T> cell = new ComputeCell<>(function, cells);
        cell.compute();
        return cell;
    }

    public static void updateAll(Cell<?>... cells) {
        boolean changed;
        do {
            changed = false;
            for (Cell<?> cell : cells) {
                if (cell instanceof ComputeCell<?> computeCell && computeCell.isDirty()) {
                    computeCell.compute();
                    changed = true;
                }
            }
        } while (changed);
    }
}
