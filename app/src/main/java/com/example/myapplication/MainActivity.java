package com.example.myapplication;

import android.os.Build;
import android.os.Bundle;

import androidx.activity.EdgeToEdge;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import android.content.IntentFilter;

public class MainActivity extends AppCompatActivity {
    private adbBroadcastReceiver myReceiver = new adbBroadcastReceiver();
    public static final String CUSTOM_ACTION = "com.example.MY_CUSTOM_ACTION";

    @Override
    @RequiresApi(api = Build.VERSION_CODES.TIRAMISU)
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        // Register the receiver dynamically
        IntentFilter filter = new IntentFilter(CUSTOM_ACTION);
        registerReceiver(myReceiver, filter, RECEIVER_EXPORTED);

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(myReceiver);
    }
}
