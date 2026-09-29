package com.example.loginactivity;

import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.loginactivity.BookResponse;
import java.util.List;

public class SearchAdapter extends RecyclerView.Adapter<SearchAdapter.VH> {
    private final List<BookResponse.Item> books;

    public SearchAdapter(List<BookResponse.Item> books) { this.books = books; }

    @NonNull @Override
    public VH onCreateViewHolder(@NonNull ViewGroup p, int vt) {
        View v = LayoutInflater.from(p.getContext()).inflate(android.R.layout.simple_list_item_2, p, false);
        return new VH(v);
    }

    @Override
    public void onBindViewHolder(@NonNull VH h, int pos) {
        BookResponse.VolumeInfo info = books.get(pos).volumeInfo;
        h.t1.setText(info.title);

        // Use system theme colors instead of hardcoded Color.BLACK
        h.t1.setTextColor(h.itemView.getContext().getColor(android.R.color.tab_indicator_text));

        String author = (info.authors != null && !info.authors.isEmpty()) ? info.authors.get(0) : "Unknown Author";
        h.t2.setText(author);

        // Force HTTPS for image loading
        String rawUrl = (info.imageLinks != null) ? info.imageLinks.thumbnail : "";
        final String secureUrl = rawUrl.replace("http://", "https://");

        h.itemView.setOnClickListener(v -> {
            Intent intent = new Intent(v.getContext(), BookDetailActivity.class);
            intent.putExtra("FROM_SEARCH", true);
            intent.putExtra("book_title", info.title);
            intent.putExtra("book_author", author);
            intent.putExtra("book_url", secureUrl);
            v.getContext().startActivity(intent);
        });
    }

    @Override public int getItemCount() { return books != null ? books.size() : 0; }

    static class VH extends RecyclerView.ViewHolder {
        TextView t1, t2;
        VH(View v) { super(v); t1 = v.findViewById(android.R.id.text1); t2 = v.findViewById(android.R.id.text2); }
    }
}
