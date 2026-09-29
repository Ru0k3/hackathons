package com.example.loginactivity;

import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;
import androidx.appcompat.widget.SearchView;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.loginactivity.database.Book;
import com.example.loginactivity.database.MyDataBase;
import com.google.android.material.switchmaterial.SwitchMaterial;
import com.google.firebase.auth.FirebaseAuth;
import java.util.List;

public class LibraryActivity extends AppCompatActivity {
    private RecyclerView rv;
    private BookAdapter adapter;
    private NetworkReceiver networkReceiver;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_library);

        // 1. Start Background Service
        startService(new Intent(this, LibrarySyncService.class));

        // 2. Initialize Network Receiver
        networkReceiver = new NetworkReceiver();
        registerReceiver(networkReceiver, new IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION));

        // 3. UI Components
        rv = findViewById(R.id.recyclerViewBooks);
        rv.setLayoutManager(new LinearLayoutManager(this));

        // Dark Mode Toggle Logic
        SwitchMaterial sm = findViewById(R.id.switchDarkMode);
        SharedPreferences sp = getSharedPreferences("MODE", MODE_PRIVATE);
        boolean isNightMode = sp.getBoolean("night", false);
        sm.setChecked(isNightMode);

        sm.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if (isChecked) {
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES);
            } else {
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO);
            }
            sp.edit().putBoolean("night", isChecked).apply();
        });

        // Navigation
        findViewById(R.id.btnGoToSearch).setOnClickListener(v ->
                startActivity(new Intent(this, SearchBookActivity.class)));

        findViewById(R.id.btnLogout).setOnClickListener(v -> {
            FirebaseAuth.getInstance().signOut();
            startActivity(new Intent(this, MainActivity.class));
            finish();
        });

        findViewById(R.id.fabAddBook).setOnClickListener(v ->
                startActivity(new Intent(this, AddBookActivity.class)));

        SearchView sv = findViewById(R.id.searchView);
        sv.setOnQueryTextListener(new SearchView.OnQueryTextListener() {
            @Override public boolean onQueryTextSubmit(String query) { return false; }
            @Override public boolean onQueryTextChange(String newText) {
                if (adapter != null) adapter.filter(newText);
                return true;
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        List<Book> books = MyDataBase.getInstance(this).bookDao().getAllBooks();
        adapter = new BookAdapter(books);
        rv.setAdapter(adapter);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Unregister receiver to prevent memory leaks
        if (networkReceiver != null) {
            unregisterReceiver(networkReceiver);
        }
    }
}