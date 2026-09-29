package com.example.myapplication.ui;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import java.util.List;

@Dao
public interface MeetingDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insert(MeetingEntity meeting);

    @Query("SELECT * FROM meetings")
    List<MeetingEntity> getAll();
}
