package com.example.myapplication;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.location.LocationManager;
import android.os.Build;

public class adbBroadcastReceiver extends BroadcastReceiver {
    MockLocationProvider mockGPS;
    String logTag="MockGpsadbBroadcastReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent != null && "com.example.MY_CUSTOM_ACTION".equals(intent.getAction())) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                mockGPS = new MockLocationProvider(LocationManager.GPS_PROVIDER, context);

                double lat = Double.parseDouble(intent.getStringExtra("lat") != null ? intent.getStringExtra("lat") : "0");
                double lon = Double.parseDouble(intent.getStringExtra("lon") != null ? intent.getStringExtra("lon") : "0");

                // float accurate = Float.parseFloat(intent.getStringExtra("accurate") != null ? intent.getStringExtra("accurate") : "0");
                // Log.i(logTag, String.format("setting mock to Latitude=%f, Longitude=%f Accuracy=%f", lat, lon, 0.0f));
                mockGPS.pushLocation(lat, lon, 0, 0);
            }
        }
    }
}
