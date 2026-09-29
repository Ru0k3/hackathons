package com.example.myapplication.ui;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "meetings")
public class MeetingEntity {

    @PrimaryKey
    @NonNull
    public String meetingId;

    public String userA;
    public String userB;
    public String scheduledTime;
    public long meetingTimeMillis;
    public String status;
    public String shareableLink;

    // Default constructor for Room
    public MeetingEntity() {
        this.meetingId = "";
    }

    public MeetingEntity(@NonNull String meetingId, String userA, String userB, String scheduledTime, long meetingTimeMillis, String status, String shareableLink) {
        this.meetingId = meetingId;
        this.userA = userA;
        this.userB = userB;
        this.scheduledTime = scheduledTime;
        this.meetingTimeMillis = meetingTimeMillis;
        this.status = status;
        this.shareableLink = shareableLink;
    }
}
