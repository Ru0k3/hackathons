package com.example.loginactivity;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.bumptech.glide.Glide;
import com.example.loginactivity.database.Book;
import com.example.loginactivity.database.MyDataBase;

public class BookDetailActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Uri data = getIntent().getData();

        // 1. Deep Link Handler (Link from outside the app)
        if (data != null) {
            setContentView(R.layout.activity_book_detail);
            handleDeepLink(data);
        }
        // 2. Search Result Preview (Before saving)
        else if (getIntent().hasExtra("FROM_SEARCH")) {
            setContentView(R.layout.book_details);
            setupSearchUI();
        }
        // 3. Local Library Click (Gatsby Style)
        else {
            setContentView(R.layout.activity_book_detail);
            setupLocalUI();
        }
    }

    private void setupSearchUI() {
        TextView txtTitle = findViewById(R.id.txtSearchDetailTitle);
        ImageView img = findViewById(R.id.imgDetailCover);
        Button btnSave = findViewById(R.id.btnSaveToLibrary);

        String title = getIntent().getStringExtra("book_title");
        String author = getIntent().getStringExtra("book_author");
        String url = getIntent().getStringExtra("book_url");

        if (txtTitle != null) txtTitle.setText(title);
        loadSecureImage(url, img);

        btnSave.setOnClickListener(v -> {
            Book b = new Book(title, author, "Saved from Online Search", url);
            MyDataBase.getInstance(this).bookDao().insertBook(b);
            Toast.makeText(this, "Book Saved to Library!", Toast.LENGTH_SHORT).show();
            finish();
        });
    }

    private void setupLocalUI() {
        String title = getIntent().getStringExtra("book_title");
        String author = getIntent().getStringExtra("book_author");
        String desc = getIntent().getStringExtra("book_desc");
        String url = getIntent().getStringExtra("book_url");

        ((TextView)findViewById(R.id.txtDetailTitle)).setText(title);
        ((TextView)findViewById(R.id.txtDetailGenre)).setText("By " + author);
        ((TextView)findViewById(R.id.txtDetailDesc)).setText(desc);

        ImageView img = findViewById(R.id.imgDetailCover);
        loadSecureImage(url, img);

        // OCEANOFPDF SEARCH LOGIC
        findViewById(R.id.btnReadNow).setOnClickListener(v -> {
            String query = Uri.encode(title);
            String oceanUrl = "https://oceanofpdf.com/?s=" + query;
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(oceanUrl)));
        });

        // SHARING LOGIC (HTTPS Link for Blue Clickable WhatsApp Message)
        findViewById(R.id.btnShare).setOnClickListener(v -> {
            String deepLink = "https://www.mylibraryapp.com/book?title=" + Uri.encode(title) +
                    "&author=" + Uri.encode(author) +
                    "&url=" + Uri.encode(url);

            Intent shareIntent = new Intent(Intent.ACTION_SEND);
            shareIntent.setType("text/plain");
            shareIntent.putExtra(Intent.EXTRA_TEXT, "Check out this book: " + deepLink);
            startActivity(Intent.createChooser(shareIntent, "Share Book"));
        });
    }

    private void handleDeepLink(Uri data) {
        String title = data.getQueryParameter("title");
        String author = data.getQueryParameter("author");
        String url = data.getQueryParameter("url");

        TextView titleView = findViewById(R.id.txtDetailTitle);
        TextView authorView = findViewById(R.id.txtDetailGenre);
        TextView descView = findViewById(R.id.txtDetailDesc);
        ImageView imgView = findViewById(R.id.imgDetailCover);

        if (titleView != null) titleView.setText(title);
        if (authorView != null) authorView.setText("By " + author);
        if (descView != null) descView.setText("This book was shared with you via My Library link.");

        loadSecureImage(url, imgView);

        // Keep OceanofPDF search working on Deep Linked items
        findViewById(R.id.btnReadNow).setOnClickListener(v -> {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://oceanofpdf.com/?s=" + Uri.encode(title))));
        });
    }

    private void loadSecureImage(String url, ImageView imageView) {
        // Automatically converts HTTP to HTTPS to avoid Network Security blocks
        if (url != null && url.startsWith("http://")) {
            url = url.replace("http://", "https://");
        }
        Glide.with(this)
                .load(url)
                .placeholder(android.R.drawable.ic_menu_gallery)
                .error(android.R.drawable.stat_notify_error)
                .into(imageView);
    }
}