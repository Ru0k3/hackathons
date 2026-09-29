package com.example.myapplication;

import android.content.Context;
import android.content.SharedPreferences;

public class SessionManager {

    private final SharedPreferences prefs;

    public SessionManager(Context context) {
        prefs = context.getSharedPreferences("negotiator_session", Context.MODE_PRIVATE);
    }

    public void saveSlackUser(String slackId, String name) {
        prefs.edit()
                .putString("SLACK_ID", slackId)
                .putString("SLACK_NAME", name)
                .apply();
    }

    public boolean isLoggedIn() {
        return prefs.contains("SLACK_ID");
    }

    public String getSlackId() {
        return prefs.getString("SLACK_ID", null);
    }

    public void logout() {
        prefs.edit().clear().apply();
    }
}
