package com.example.loginactivity.database;

import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "books")
public class Book {
    @PrimaryKey(autoGenerate = true)
    private int id;
    private String title;
    private String author;
    private String description;
    private String imageUrl;

    public Book(String title, String author, String description, String imageUrl) {
        this.title = title;
        this.author = author;
        this.description = description;
        this.imageUrl = imageUrl;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public String getTitle() { return title; }
    public String getAuthor() { return author; }
    public String getDescription() { return description; }
    public String getImageUrl() { return imageUrl; }
}