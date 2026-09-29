package com.example.loginactivity;

import java.util.List;

public class BookResponse {
    public List<Item> items;

    public static class Item {
        public VolumeInfo volumeInfo;
    }

    public static class VolumeInfo {
        public String title;
        public List<String> authors;
        public ImageLinks imageLinks;
    }

    public static class ImageLinks {
        public String thumbnail;
    }
}
