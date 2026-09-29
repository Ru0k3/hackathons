package com.example.loginactivity;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.widget.Toast;

public class LibrarySyncService extends Service {
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        new Thread(() -> {
            // Simulate a background sync task
            try {
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            // Stop the service once work is done
            stopSelf();
        }).start();

        return START_NOT_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}