package com.example.myapplication;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.myapplication.ui.preferences.PreferencesActivity;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Session check
        SessionManager sessionManager = new SessionManager(this);
        if (!sessionManager.isLoggedIn()) {
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        // Apply window insets for EdgeToEdge
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Initialize UI components
        Button btnCreateMeeting = findViewById(R.id.btnCreateMeeting);
        Button btnViewMeetings = findViewById(R.id.btnViewMeetings);
        Button btnPreferences = findViewById(R.id.btnPreferences);
        Button btnLogout = findViewById(R.id.btnLogout);

        // Set listeners
        btnCreateMeeting.setOnClickListener(v -> {
            startActivity(new Intent(MainActivity.this, CreateMeetingActivity.class));
        });

        btnViewMeetings.setOnClickListener(v -> {
            startActivity(new Intent(MainActivity.this, MeetingActivity.class));
        });

        btnPreferences.setOnClickListener(v -> {
            startActivity(new Intent(MainActivity.this, PreferencesActivity.class));
        });

        btnLogout.setOnClickListener(v -> {
            sessionManager.logout();
            startActivity(new Intent(MainActivity.this, LoginActivity.class));
            finish();
        });
    }
}
