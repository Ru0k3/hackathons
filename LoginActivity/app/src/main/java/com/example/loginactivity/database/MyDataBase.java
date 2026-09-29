package com.example.loginactivity.database;

import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;
import android.content.Context;

@Database(entities = {Book.class}, version = 1, exportSchema = true)
public abstract class MyDataBase extends RoomDatabase {
    public abstract BookDao bookDao();
    private static MyDataBase instance;

    public static synchronized MyDataBase getInstance(Context context) {
        if (instance == null) {
            instance = Room.databaseBuilder(context.getApplicationContext(),
                            MyDataBase.class, "library_db")
                    .fallbackToDestructiveMigration()
                    .allowMainThreadQueries().build();
        }
        return instance;
    }
}