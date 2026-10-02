import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

class RestApi {

    private final List<User> users;

    RestApi(User... users) {
        this.users = new ArrayList<>();
        Collections.addAll(this.users, users);
    }

    String get(String url) {
        if ("/users".equals(url)) {
            return buildUsersResponse(null);
        }
        return "";
    }

    String get(String url, JSONObject payload) {
        if ("/users".equals(url)) {
            List<String> requestedUsers = new ArrayList<>();
            if (payload.has("users")) {
                JSONArray usersArray = payload.getJSONArray("users");
                for (int i = 0; i < usersArray.length(); i++) {
                    requestedUsers.add(usersArray.getString(i));
                }
            }
            return buildUsersResponse(requestedUsers);
        }
        return "";
    }

    String post(String url, JSONObject payload) {
        if ("/add".equals(url)) {
            String name = payload.getString("user");
            User newUser = User.builder().setName(name).build();
            users.add(newUser);
            return newUser.toJson().toString();
        } else if ("/iou".equals(url)) {
            String lenderName = payload.getString("lender");
            String borrowerName = payload.getString("borrower");
            double amount = payload.getDouble("amount");

            User lender = findUser(lenderName);
            User borrower = findUser(borrowerName);

            if (lender != null && borrower != null) {
                User updatedLender = updateDebt(lender, borrowerName, amount, false);
                User updatedBorrower = updateDebt(borrower, lenderName, amount, true);

                users.remove(lender);
                users.remove(borrower);
                users.add(updatedLender);
                users.add(updatedBorrower);

                List<User> responseUsers = new ArrayList<>();
                responseUsers.add(updatedLender);
                responseUsers.add(updatedBorrower);
                Collections.sort(responseUsers, (u1, u2) -> u1.name().compareTo(u2.name()));

                JSONArray jsonArray = new JSONArray();
                for (User u : responseUsers) {
                    jsonArray.put(u.toJson());
                }
                JSONObject response = new JSONObject();
                response.put("users", jsonArray);
                return response.toString();
            }
        }
        return "";
    }

    private User updateDebt(User user, String otherName, double amount, boolean isOwedBy) {
        Map<String, Double> debts = isOwedBy ? user.owedBy : user.owes;
        Map<String, Double> credits = isOwedBy ? user.owes : user.owedBy;

        double currentDebt = debts.getOrDefault(otherName, 0.0);
        double currentCredit = credits.getOrDefault(otherName, 0.0);

        User.Builder builder = User.builder().setName(user.name());

        // Copy existing debts/credits excluding the other person
        for (Map.Entry<String, Double> entry : user.owes.entrySet()) {
            if (!entry.getKey().equals(otherName)) {
                builder.owes(entry.getKey(), entry.getValue());
            }
        }
        for (Map.Entry<String, Double> entry : user.owedBy.entrySet()) {
            if (!entry.getKey().equals(otherName)) {
                builder.owedBy(entry.getKey(), entry.getValue());
            }
        }

        // Net the new amount against existing debt/credit
        if (isOwedBy) {
            // User is lending money, so they are owed more
            // If they already owed money, it reduces the debt
            double net = currentCredit - currentDebt + amount;
            if (net > 0) {
                builder.owedBy(otherName, net);
            } else if (net < 0) {
                builder.owes(otherName, -net);
            }
        } else {
            // User is borrowing money, so they owe more
            // If they are already owed money, it reduces the debt
            double net = currentDebt - currentCredit + amount;
            if (net > 0) {
                builder.owes(otherName, net);
            } else if (net < 0) {
                builder.owedBy(otherName, -net);
            }
        }

        return builder.build();
    }

    private User findUser(String name) {
        for (User user : users) {
            if (user.name().equals(name)) {
                return user;
            }
        }
        return null;
    }

    private String buildUsersResponse(List<String> requestedUsers) {
        List<User> filteredUsers;
        if (requestedUsers == null || requestedUsers.isEmpty()) {
            filteredUsers = new ArrayList<>(users);
        } else {
            filteredUsers = users.stream()
                    .filter(u -> requestedUsers.contains(u.name()))
                    .collect(Collectors.toList());
        }
        
        Collections.sort(filteredUsers, (u1, u2) -> u1.name().compareTo(u2.name()));

        JSONArray jsonArray = new JSONArray();
        for (User user : filteredUsers) {
            jsonArray.put(user.toJson());
        }
        
        JSONObject response = new JSONObject();
        response.put("users", jsonArray);
        return response.toString();
    }
}
