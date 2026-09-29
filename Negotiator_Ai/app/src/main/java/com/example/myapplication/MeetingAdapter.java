package com.example.myapplication;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.myapplication.ui.MeetingEntity;
import java.util.List;

public class MeetingAdapter extends RecyclerView.Adapter<MeetingAdapter.VH> {

    private final List<MeetingEntity> meetings;

    public MeetingAdapter(List<MeetingEntity> meetings) {
        this.meetings = meetings;
    }

    static class VH extends RecyclerView.ViewHolder {
        TextView tvUsers, tvTime, tvStatus;
        VH(View v) {
            super(v);
            tvUsers = v.findViewById(R.id.tvUsers);
            tvTime = v.findViewById(R.id.tvTime);
            tvStatus = v.findViewById(R.id.tvStatus);
        }
    }

    @NonNull
    @Override
    public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        return new VH(LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_meeting, parent, false));
    }

    @Override
    public void onBindViewHolder(@NonNull VH holder, int position) {
        MeetingEntity m = meetings.get(position);
        holder.tvUsers.setText(m.userA + " ↔ " + m.userB);
        holder.tvTime.setText("Time: " + m.scheduledTime);
        holder.tvStatus.setText("Status: " + m.status);
    }

    @Override
    public int getItemCount() {
        return meetings.size();
    }
}
