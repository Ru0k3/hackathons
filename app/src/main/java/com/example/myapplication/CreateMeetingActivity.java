package com.example.myapplication;

import android.os.Bundle;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import okhttp3.*;

import java.io.IOException;

public class CreateMeetingActivity extends AppCompatActivity {

    private static final String BACKEND_URL =
            "http://10.0.2.2:8000/meetings/email";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_create_meeting);

        EditText etEmail = findViewById(R.id.etUserBGmail);
        EditText etSubject = findViewById(R.id.etSubject);
        EditText etDuration = findViewById(R.id.etDuration);
        EditText etAvailability = findViewById(R.id.etAvailability);
        EditText etDescription = findViewById(R.id.etDescription);
        Button btnSubmit = findViewById(R.id.btnSubmitMeeting);

        btnSubmit.setOnClickListener(v -> {

            OkHttpClient client = new OkHttpClient();

            RequestBody body = new FormBody.Builder()
                    .add("to_email", etEmail.getText().toString())
                    .add("subject", etSubject.getText().toString())
                    .add("duration", etDuration.getText().toString())
                    .add("availability", etAvailability.getText().toString())
                    .add("description", etDescription.getText().toString())
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
                                    CreateMeetingActivity.this,
                                    "Failed to send meeting request",
                                    Toast.LENGTH_SHORT
                            ).show()
                    );
                }

                @Override
                public void onResponse(Call call, Response response) {
                    runOnUiThread(() ->
                            Toast.makeText(
                                    CreateMeetingActivity.this,
                                    "Meeting request sent successfully",
                                    Toast.LENGTH_SHORT
                            ).show()
                    );
                    finish();
                }
            });
        });
    }
}

