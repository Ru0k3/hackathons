package com.example.myapplication;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.myapplication.ui.AppDatabase;
import com.example.myapplication.ui.MeetingEntity;
import java.util.List;

public class MeetingActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_meeting);

        RecyclerView recyclerView = findViewById(R.id.recyclerMeetings);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        // Get meetings from database
        List<MeetingEntity> meetings = AppDatabase.getDatabase(this).meetingDao().getAll();
        
        MeetingAdapter adapter = new MeetingAdapter(meetings);
        recyclerView.setAdapter(adapter);
    }
}
