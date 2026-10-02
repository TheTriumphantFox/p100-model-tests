import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONObject;

class RestApi {

    private final Map<String, User> users = new HashMap<>();

    RestApi(User... users) {
        for (User u : users) {
            this.users.put(u.name(), u);
        }
    }

    /** Handle GET requests without payload. */
    String get(String url) {
        if ("/users".equals(url)) {
            JSONArray arr = new JSONArray();
            for (User u : users.values()) {
                arr.put(u.toJson());
            }
            JSONObject resp = new JSONObject();
            resp.put("users", arr);
            return resp.toString();
        }
        throw new UnsupportedOperationException("Unsupported GET URL: " + url);
    }

    /** Handle GET requests with payload. */
    String get(String url, JSONObject payload) {
        if ("/users".equals(url)) {
            JSONArray requested = payload.optJSONArray("users");
            List<User> selected = new ArrayList<>();
            if (requested != null) {
                for (int i = 0; i < requested.length(); i++) {
                    String name = requested.getString(i);
                    User u = users.get(name);
                    if (u != null) {
                        selected.add(u);
                    }
                }
            } else {
                selected.addAll(users.values());
            }
            selected.sort((a, b) -> a.name().compareTo(b.name()));
            JSONArray arr = new JSONArray();
            for (User u : selected) {
                arr.put(u.toJson());
            }
            JSONObject resp = new JSONObject();
            resp.put("users", arr);
            return resp.toString();
        }
        throw new UnsupportedOperationException("Unsupported GET URL with payload: " + url);
    }

    /** Handle POST requests with payload. */
    String post(String url, JSONObject payload) {
        switch (url) {
            case "/add":
                String newName = payload.getString("user");
                if (users.containsKey(newName)) {
                    throw new IllegalArgumentException("User already exists: " + newName);
                }
                User newUser = User.builder().setName(newName).build();
                users.put(newName, newUser);
                return newUser.toJson().toString();

            case "/iou":
                String lender = payload.getString("lender");
                String borrower = payload.getString("borrower");
                double amount = payload.getDouble("amount");

                User lenderUser = users.get(lender);
                User borrowerUser = users.get(borrower);
                if (lenderUser == null || borrowerUser == null) {
                    throw new IllegalArgumentException("Unknown lender or borrower");
                }

                // Update lender's owedBy list
                User updatedLender = User.builder()
                        .setName(lenderUser.name())
                        .addOwedBy(lenderUser.owedBy())
                        .owedBy(lender, amount)
                        .build();

                // Update borrower's owes list
                User updatedBorrower = User.builder()
                        .setName(borrowerUser.name())
                        .addOwes(borrowerUser.owes())
                        .owes(lender, amount)
                        .build();

                users.put(lender, updatedLender);
                users.put(borrower, updatedBorrower);

                List<User> updated = List.of(updatedLender, updatedBorrower);
                updated.sort((a, b) -> a.name().compareTo(b.name()));
                JSONArray arr = new JSONArray();
                for (User u : updated) {
                    arr.put(u.toJson());
                }
                JSONObject resp = new JSONObject();
                resp.put("users", arr);
                return resp.toString();

            default:
                throw new UnsupportedOperationException("Unsupported POST URL: " + url);
        }
    }
}
