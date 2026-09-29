package com.example.loginactivity;

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.example.loginactivity.database.Book;
import com.example.loginactivity.database.MyDataBase;

public class AddBookActivity extends AppCompatActivity {
    private EditText edtTitle, edtAuthor, edtDescription, edtImageUrl;
    private int bookId = -1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_book);

        // Initialize UI components
        edtTitle = findViewById(R.id.edtAddTitle);
        edtAuthor = findViewById(R.id.edtAddAuthor);
        edtDescription = findViewById(R.id.edtAddDescription);
        edtImageUrl = findViewById(R.id.edtAddImageUrl);
        Button btnSave = findViewById(R.id.btnSaveBook);

        // CHECK: Are we editing an existing book?
        if (getIntent().hasExtra("bookId")) {
            bookId = getIntent().getIntExtra("bookId", -1);
            edtTitle.setText(getIntent().getStringExtra("title"));
            edtAuthor.setText(getIntent().getStringExtra("author"));
            edtDescription.setText(getIntent().getStringExtra("desc"));
            edtImageUrl.setText(getIntent().getStringExtra("url"));
            btnSave.setText("UPDATE BOOK");
        }

        btnSave.setOnClickListener(v -> {
            String title = edtTitle.getText().toString().trim();
            String author = edtAuthor.getText().toString().trim();
            String desc = edtDescription.getText().toString().trim();
            String url = edtImageUrl.getText().toString().trim();

            if (title.isEmpty() || author.isEmpty()) {
                Toast.makeText(this, "Title and Author are required", Toast.LENGTH_SHORT).show();
                return;
            }

            Book book = new Book(title, author, desc, url);

            if (bookId != -1) {
                // UPDATE existing book
                book.setId(bookId);
                MyDataBase.getInstance(this).bookDao().updateBook(book);
                Toast.makeText(this, "Book Updated!", Toast.LENGTH_SHORT).show();
            } else {
                // SAVE new book
                MyDataBase.getInstance(this).bookDao().insertBook(book);
                Toast.makeText(this, "Book Added to Library!", Toast.LENGTH_SHORT).show();
            }

            finish(); // Return to LibraryActivity
        });
    }
}