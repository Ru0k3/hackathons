package com.example.loginactivity;

import com.example.loginactivity.BookResponse;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;

public interface GoogleBooksService {
    @GET("volumes")
    Call<BookResponse> searchBooks(
            @Query("q") String query,
            @Query("maxResults") int maxResults
    );
}