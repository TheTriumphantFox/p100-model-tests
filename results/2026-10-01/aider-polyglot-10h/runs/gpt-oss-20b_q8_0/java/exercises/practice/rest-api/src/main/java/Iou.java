/** Simple immutable representation of an IOU. */
public class Iou {
    private final String lender;
    private final double amount;

    public Iou(String lender, double amount) {
        this.lender = lender;
        this.amount = amount;
    }

    public String lender() {
        return lender;
    }

    public double amount() {
        return amount;
    }
}
