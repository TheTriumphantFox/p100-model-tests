class Iou {
    private final String name;
    private final double amount;

    Iou(String name, double amount) {
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
