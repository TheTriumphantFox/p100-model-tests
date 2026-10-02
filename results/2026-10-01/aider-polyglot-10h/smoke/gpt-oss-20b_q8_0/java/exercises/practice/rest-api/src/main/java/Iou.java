/** Simple immutable representation of an IOU between two users. */
public class Iou {
    private final String name;
    private final double amount;

    public Iou(String name, double amount) {
        this.name = name;
        this.amount = amount;
    }

    public String name() {
        return name;
    }

    public double amount() {
        return amount;
    }
}
