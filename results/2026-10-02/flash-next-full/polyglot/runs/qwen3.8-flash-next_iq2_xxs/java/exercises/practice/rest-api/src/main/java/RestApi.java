import org.json.JSONObject;
import org.json.JSONArray;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class RestApi {

    private final List<User> users;

    RestApi(User... users) {
        this.users = new ArrayList<>();
        for (User user : users) {
            this.users.add(user);
        }
    }

    String get(String url) {
        if ("/users".equals(url)) {
            return usersToJson(users);
        }
        throw new UnsupportedOperationException("Unknown URL: " + url);
    }

    String get(String url, JSONObject payload) {
        if ("/users".equals(url)) {
            JSONArray usersArray = payload.optJSONArray("users");
            if (usersArray == null) {
                return usersToJson(users);
            }
            List<User> filteredUsers = new ArrayList<>();
            for (int i = 0; i < usersArray.length(); i++) {
                String name = usersArray.getString(i);
                for (User user : users) {
                    if (user.name().equals(name)) {
                        filteredUsers.add(user);
                    }
                }
            }
            return usersToJson(filteredUsers);
        }
        throw new UnsupportedOperationException("Unknown URL: " + url);
    }

    String post(String url, JSONObject payload) {
        if ("/add".equals(url)) {
            String name = payload.getString("user");
            User newUser = User.builder().setName(name).build();
            users.add(newUser);
            return newUser.toJson();
        } else if ("/iou".equals(url)) {
            String lender = payload.getString("lender");
            String borrower = payload.getString("borrower");
            double amount = payload.getDouble("amount");

            User lenderUser = null;
            User borrowerUser = null;

            for (User user : users) {
                if (user.name().equals(lender)) {
                    lenderUser = user;
                } else if (user.name().equals(borrower)) {
                    borrowerUser = user;
                }
            }

            if (lenderUser != null && borrowerUser != null) {
                lenderUser.owe(borrower, amount);
                borrowerUser.beOwedBy(lender, amount);
            }

            List<User> updatedUsers = new ArrayList<>();
            for (User user : users) {
                if (user.name().equals(lender) || user.name().equals(borrower)) {
                    updatedUsers.add(user);
                }
            }
            return usersToJson(updatedUsers);
        }
        throw new UnsupportedOperationException("Unknown URL: " + url);
    }

    private String usersToJson(List<User> users) {
        List<User> sortedUsers = new ArrayList<>(users);
        sortedUsers.sort(Comparator.comparing(User::name));
        StringBuilder sb = new StringBuilder();
        sb.append("{\"users\":[");
        for (int i = 0; i < sortedUsers.size(); i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append(sortedUsers.get(i).toJson());
        }
        sb.append("]}");
        return sb.toString();
    }
}
