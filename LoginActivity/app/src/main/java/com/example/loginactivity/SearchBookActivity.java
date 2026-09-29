package com.example.loginactivity;

import android.os.Bundle;
import android.widget.EditText;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.loginactivity.BookResponse;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class SearchBookActivity extends AppCompatActivity {
    private RecyclerView rv;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search_book);

        EditText et = findViewById(R.id.etSearchQuery);
        rv = findViewById(R.id.rvSearchResults);
        rv.setLayoutManager(new LinearLayoutManager(this));

        Retrofit rf = new Retrofit.Builder()
                .baseUrl("https://www.googleapis.com/books/v1/")
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        GoogleBooksService service = rf.create(GoogleBooksService.class);

        findViewById(R.id.btnSearch).setOnClickListener(v -> {
            String query = et.getText().toString();
            // Google's 'q' parameter searches both title and author
            service.searchBooks(query, 20).enqueue(new Callback<BookResponse>() {
                @Override
                public void onResponse(Call<BookResponse> call, Response<BookResponse> response) {
                    if (response.isSuccessful() && response.body() != null && response.body().items != null) {
                        rv.setAdapter(new SearchAdapter(response.body().items));
                    }
                }
                @Override public void onFailure(Call<BookResponse> call, Throwable t) {}
            });
        });
    }
}
