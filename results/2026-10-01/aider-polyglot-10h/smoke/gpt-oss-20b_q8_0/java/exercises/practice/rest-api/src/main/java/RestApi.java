import org.json.JSONArray;
import org.json.JSONObject;

import java.util.*;
import java.util.stream.Collectors;

class RestApi {

    private final Map<String, User> users = new HashMap<>();

    RestApi(User... users) {
        for (User u : users) {
            this.users.put(u.name(), u);
        }
    }

    String get(String url) {
        if (url.equals("/users")) {
            return users.values().stream()
                    .map(User::toJSON)
                    .collect(JSONArray::new, JSONArray::put, JSONArray::putAll)
                    .toString();
        }
        // support query string: /users?users=Adam,Bob
        if (url.startsWith("/users?users=")) {
            String list = url.substring("/users?users=".length());
            List<String> names = Arrays.stream(list.split(","))
                    .map(String::trim)
                    .filter(n -> !n.isEmpty())
                    .sorted()
                    .collect(Collectors.toList());
            JSONArray arr = new JSONArray();
            for (String name : names) {
                User u = users.get(name);
                if (u != null) {
                    arr.put(u.toJSON());
                }
            }
            return arr.toString();
        }
        throw new UnsupportedOperationException("Unsupported GET URL: " + url);
    }

    String get(String url, JSONObject payload) {
        throw new UnsupportedOperationException("GET with payload not implemented");
    }

    String post(String url, JSONObject payload) {
        switch (url) {
            case "/add":
                String name = payload.getString("user");
                if (users.containsKey(name)) {
                    throw new IllegalArgumentException("User already exists: " + name);
                }
                User newUser = User.builder().setName(name).build();
                users.put(name, newUser);
                return newUser.toJSON().toString();

            case "/iou":
                String lenderName = payload.getString("lender");
                String borrowerName = payload.getString("borrower");
                double amount = payload.getDouble("amount");

                User lender = users.get(lenderName);
                User borrower = users.get(borrowerName);
                if (lender == null || borrower == null) {
                    throw new IllegalArgumentException("Unknown user(s) in IOU");
                }

                // Update lender's owedBy and borrower's owes
                lender = lender.withOwedBy(borrowerName, amount);
                borrower = borrower.withOwes(lenderName, amount);

                users.put(lenderName, lender);
                users.put(borrowerName, borrower);

                JSONArray arr = new JSONArray();
                arr.put(lender.toJSON());
                arr.put(borrower.toJSON());
                return arr.toString();

            default:
                throw new UnsupportedOperationException("Unsupported POST URL: " + url);
        }
    }
}
