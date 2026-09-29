package com.example.myapplication.ui.preferences;

import android.os.Bundle;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.myapplication.R;

public class PreferencesActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // ✅ MUST match XML filename exactly
        setContentView(R.layout.activity_preferences);

        Spinner spinnerTime = findViewById(R.id.spinnerTime);
        Spinner spinnerDuration = findViewById(R.id.spinnerDuration);
        Spinner spinnerFlexibility = findViewById(R.id.spinnerFlexibility);

        CheckBox chkMon = findViewById(R.id.chkMon);
        CheckBox chkTue = findViewById(R.id.chkTue);
        CheckBox chkWed = findViewById(R.id.chkWed);
        CheckBox chkThu = findViewById(R.id.chkThu);
        CheckBox chkFri = findViewById(R.id.chkFri);
        CheckBox chkSat = findViewById(R.id.chkSat);
        CheckBox chkSun = findViewById(R.id.chkSun);

        Button btnSave = findViewById(R.id.btnSavePreferences);

        btnSave.setOnClickListener(v -> {
            // (Later you can persist this to Room / backend)
            Toast.makeText(
                    this,
                    "Preferences saved successfully",
                    Toast.LENGTH_SHORT
            ).show();
            finish();
        });
    }
}
