package com.example.loginactivity;

import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.example.loginactivity.database.Book;
import com.example.loginactivity.database.MyDataBase;
import java.util.ArrayList;
import java.util.List;

public class BookAdapter extends RecyclerView.Adapter<BookAdapter.BookViewHolder> {
    private List<Book> bookList;
    private List<Book> bookListFull;

    public BookAdapter(List<Book> books) {
        this.bookList = books;
        this.bookListFull = new ArrayList<>(books);
    }

    @NonNull
    @Override
    public BookViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_book, parent, false);
        return new BookViewHolder(v);
    }

    @Override
    public void onBindViewHolder(@NonNull BookViewHolder holder, int position) {
        Book b = bookList.get(position);
        holder.tvTitle.setText(b.getTitle());
        holder.tvAuthor.setText(b.getAuthor());
        Glide.with(holder.itemView.getContext()).load(b.getImageUrl()).into(holder.ivCover);

        holder.btnDelete.setOnClickListener(v -> {
            MyDataBase.getInstance(v.getContext()).bookDao().deleteBook(b);
            bookList.remove(position);
            notifyItemRemoved(position);
        });

        holder.itemView.setOnClickListener(v -> {
            Intent i = new Intent(v.getContext(), BookDetailActivity.class);
            i.putExtra("book_title", b.getTitle());
            i.putExtra("book_author", b.getAuthor());
            i.putExtra("book_desc", b.getDescription());
            i.putExtra("book_url", b.getImageUrl());
            v.getContext().startActivity(i);
        });
    }

    public void filter(String text) {
        bookList.clear();
        if (text.isEmpty()) {
            bookList.addAll(bookListFull);
        } else {
            text = text.toLowerCase();
            for (Book item : bookListFull) {
                if (item.getTitle().toLowerCase().contains(text)) {
                    bookList.add(item);
                }
            }
        }
        notifyDataSetChanged();
    }

    @Override public int getItemCount() { return bookList.size(); }

    static class BookViewHolder extends RecyclerView.ViewHolder {
        TextView tvTitle, tvAuthor;
        ImageView ivCover;
        Button btnEdit, btnDelete;
        public BookViewHolder(@NonNull View v) {
            super(v);
            tvTitle = v.findViewById(R.id.tvBookTitle);
            tvAuthor = v.findViewById(R.id.tvBookAuthor);
            ivCover = v.findViewById(R.id.ivBookCover);
            btnEdit = v.findViewById(R.id.btnEditBook);
            btnDelete = v.findViewById(R.id.btnDeleteBook);
        }
    }
}