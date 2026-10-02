import static java.util.Collections.unmodifiableList;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.json.JSONObject;

/** POJO representing a User in the database. */
public class User {
    private final String name;
    private final List<Iou> owes;
    private final List<Iou> owedBy;

    private User(String name, List<Iou> owes, List<Iou> owedBy) {
        this.name = name;
        this.owes = new ArrayList<>(owes);
        this.owedBy = new ArrayList<>(owedBy);
    }

    public String name() {
        return name;
    }

    /** IOUs this user owes to other users. */
    public List<Iou> owes() {
        return unmodifiableList(owes);
    }

    /** IOUs other users owe to this user. */
    public List<Iou> owedBy() {
        return unmodifiableList(owedBy);
    }

    /** Total balance: (total owed by others) - (total owed to others). */
    public double balance() {
        double totalOwedBy = owedBy.stream().mapToDouble(Iou::amount).sum();
        double totalOwes = owes.stream().mapToDouble(Iou::amount).sum();
        return totalOwedBy - totalOwes;
    }

    public static Builder builder() {
        return new Builder();
    }

    /** Return a new User with an additional owedBy entry. */
    public User withOwedBy(String lender, double amount) {
        List<Iou> newOwedBy = new ArrayList<>(owedBy);
        newOwedBy.add(new Iou(lender, amount));
        return new User(name, owes, newOwedBy);
    }

    /** Return a new User with an additional owes entry. */
    public User withOwes(String borrower, double amount) {
        List<Iou> newOwes = new ArrayList<>(owes);
        newOwes.add(new Iou(borrower, amount));
        return new User(name, newOwes, owedBy);
    }

    /** Convert this User to a JSONObject matching the API spec. */
    public JSONObject toJSON() {
        JSONObject obj = new JSONObject();
        obj.put("name", name);

        JSONObject owesObj = new JSONObject();
        for (Iou i : owes) {
            owesObj.put(i.name(), i.amount());
        }
        obj.put("owes", owesObj);

        JSONObject owedByObj = new JSONObject();
        for (Iou i : owedBy) {
            owedByObj.put(i.name(), i.amount());
        }
        obj.put("owed_by", owedByObj);

        obj.put("balance", balance());
        return obj;
    }

    public static class Builder {
        private String name;
        private final List<Iou> owes = new ArrayList<>();
        private final List<Iou> owedBy = new ArrayList<>();

        public Builder setName(String name) {
            this.name = name;
            return this;
        }

        public Builder owes(String name, double amount) {
            owes.add(new Iou(name, amount));
            return this;
        }

        public Builder owedBy(String name, double amount) {
            owedBy.add(new Iou(name, amount));
            return this;
        }

        public User build() {
            return new User(name, owes, owedBy);
        }
    }
}
