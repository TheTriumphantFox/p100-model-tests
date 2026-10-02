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
                updateOwes(lender, borrowerName, amount);
                updateOwes(borrower, lenderName, amount);

                List<User> responseUsers = new ArrayList<>();
                responseUsers.add(findUser(lenderName));
                responseUsers.add(findUser(borrowerName));
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

    private void updateOwes(User user, String otherName, double amount) {
        Map<String, Double> owes = user.owes();
        Map<String, Double> owedBy = user.owedBy();

        boolean isOwedByOther = owedBy.containsKey(otherName);
        boolean isOwesOther = owes.containsKey(otherName);

        if (isOwedByOther && isOwesOther) {
            double owedByAmount = owedBy.get(otherName);
            double owesAmount = owes.get(otherName);
            if (owedByAmount > owesAmount) {
                owedBy.put(otherName, owedByAmount - owesAmount);
                owes.remove(otherName);
            } else {
                owes.put(otherName, owesAmount - owedByAmount);
                owedBy.remove(otherName);
            }
        } else if (isOwedByOther) {
            double owedByAmount = owedBy.get(otherName);
            if (owedByAmount > amount) {
                owedBy.put(otherName, owedByAmount - amount);
            } else {
                owes.put(otherName, amount - owedByAmount);
                owedBy.remove(otherName);
            }
        } else if (isOwesOther) {
            double owesAmount = owes.get(otherName);
            owes.put(otherName, owesAmount + amount);
        } else {
            owes.put(otherName, amount);
        }
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
