package com.example.myapplication;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import okhttp3.*;

import org.json.JSONObject;

import java.io.IOException;

public class LoginActivity extends AppCompatActivity {

    private static final String SLACK_CLIENT_ID = "YOUR_SLACK_CLIENT_ID";
    private static final String REDIRECT_URI = "negotiator://slack-auth";
    private static final String BACKEND_URL = "http://10.0.2.2:8000/auth/slack";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        SessionManager sessionManager = new SessionManager(this);
        if (sessionManager.isLoggedIn()) {
            startActivity(new Intent(this, MainActivity.class));
            finish();
            return;
        }

        setContentView(R.layout.activity_login);

        Button btnSlackLogin = findViewById(R.id.btnSlackLogin);
        Button btnDemoLogin = findViewById(R.id.btnDemoLogin);

        // -------------------------------
        // REAL SLACK LOGIN
        // -------------------------------
        btnSlackLogin.setOnClickListener(v -> {
            String url =
                    "https://slack.com/oauth/v2/authorize"
                            + "?client_id=" + SLACK_CLIENT_ID
                            + "&scope=openid,profile,users:read"
                            + "&redirect_uri=" + REDIRECT_URI;

            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
        });

        // -------------------------------
        // DEMO LOGIN (NO SLACK)
        // -------------------------------
        btnDemoLogin.setOnClickListener(v -> {
            sessionManager.saveSlackUser(
                    "DEMO_USER",
                    "Demo User"
            );

            Toast.makeText(
                    this,
                    "Demo mode enabled",
                    Toast.LENGTH_SHORT
            ).show();

            startActivity(new Intent(this, MainActivity.class));
            finish();
        });

        handleIntent(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        handleIntent(intent);
    }

    private void handleIntent(Intent intent) {
        Uri data = intent.getData();
        if (data == null) return;

        if ("negotiator".equals(data.getScheme())) {
            String code = data.getQueryParameter("code");
            if (code != null) {
                exchangeCodeWithBackend(code);
            }
        }
    }

    private void exchangeCodeWithBackend(String code) {
        OkHttpClient client = new OkHttpClient();

        RequestBody body = new FormBody.Builder()
                .add("code", code)
                .build();

        Request request = new Request.Builder()
                .url(BACKEND_URL)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                runOnUiThread(() ->
                        Toast.makeText(
                                LoginActivity.this,
                                "Slack login failed",
                                Toast.LENGTH_SHORT
                        ).show()
                );
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try {
                    JSONObject json = new JSONObject(response.body().string());
                    String slackId = json.getString("slack_id");
                    String name = json.getString("name");

                    new SessionManager(LoginActivity.this)
                            .saveSlackUser(slackId, name);

                    runOnUiThread(() -> {
                        startActivity(new Intent(LoginActivity.this, MainActivity.class));
                        finish();
                    });

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }
}
